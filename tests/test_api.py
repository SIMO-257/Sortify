import pytest
from fastapi.testclient import TestClient

from sortify.api import create_app, hostname

TOKEN = "secret-token"


@pytest.fixture
def client():
    return TestClient(create_app(TOKEN, allowed_hosts={"testserver"}), headers={"X-Sortify-Token": TOKEN})


def names(path):
    return sorted(p.name for p in path.iterdir())


def test_token_is_required(tmp_path):
    bare = TestClient(create_app(TOKEN, allowed_hosts={"testserver"}))
    assert bare.get("/api/operations").status_code == 401
    assert bare.get("/api/operations", headers={"X-Sortify-Token": "wrong"}).status_code == 401
    assert bare.get("/api/logs").status_code == 401
    assert bare.post("/api/plan", json={"operation": "organize_by_date", "folder": str(tmp_path)}).status_code == 401


def test_foreign_hosts_are_refused():
    app = TestClient(create_app(TOKEN), headers={"X-Sortify-Token": TOKEN})
    assert app.get("/api/operations").status_code == 403
    assert app.get("/api/operations", headers={"Host": "evil.example.com"}).status_code == 403
    assert app.get("/api/operations", headers={"Host": "localhost:8000"}).status_code == 200
    assert app.get("/api/operations", headers={"Host": "127.0.0.1:1234"}).status_code == 200


def test_hostname():
    assert hostname("localhost:8000") == "localhost"
    assert hostname("[::1]:8000") == "[::1]"
    assert hostname("127.0.0.1") == "127.0.0.1"


def test_operations_listed(client):
    ops = client.get("/api/operations").json()
    assert {o["id"] for o in ops} >= {"organize_by_extension", "clean_by_name", "clean_empty_folders"}
    assert all("options" in o for o in ops)


def test_full_flow_organize_and_undo(client, tmp_path):
    (tmp_path / "a.pdf").write_text("x")
    (tmp_path / "b.txt").write_text("x")
    plan = client.post("/api/plan", json={"operation": "organize_by_extension", "folder": str(tmp_path),
                                          "options": {"label": "docs"}}).json()
    assert len(plan["actions"]) == 2 and not plan["dangerous"]
    assert names(tmp_path) == ["a.pdf", "b.txt"]  # planning changed nothing

    keep = [a["id"] for a in plan["actions"] if a["src"].endswith("a.pdf")]
    log = client.post("/api/apply", json={"plan_id": plan["plan_id"], "action_ids": keep}).json()
    assert log["summary"]["done"] == 1
    assert names(tmp_path) == ["b.txt", "docs_pdf"]

    assert client.post("/api/apply", json={"plan_id": plan["plan_id"]}).status_code == 404  # used once

    shown = client.get(f"/api/logs/{log['id']}").json()
    assert shown["operation"] == "organize_by_extension"
    assert client.get("/api/logs").json()[0]["id"] == log["id"]

    undo = client.post(f"/api/logs/{log['id']}/undo").json()
    assert undo["summary"]["done"] == 1
    assert names(tmp_path) == ["a.pdf", "b.txt"]
    assert client.post(f"/api/logs/{log['id']}/undo").status_code == 400


def test_delete_needs_the_word_delete(client, tmp_path):
    (tmp_path / "a.tmp").write_text("x")
    plan = client.post("/api/plan", json={"operation": "clean_by_extension", "folder": str(tmp_path),
                                          "options": {"extension": ".tmp"}}).json()
    assert plan["dangerous"]
    assert client.post("/api/apply", json={"plan_id": plan["plan_id"]}).status_code == 400
    assert client.post("/api/apply", json={"plan_id": plan["plan_id"], "confirm": "yes"}).status_code == 400
    assert names(tmp_path) == ["a.tmp"]
    ok = client.post("/api/apply", json={"plan_id": plan["plan_id"], "confirm": "delete"})
    assert ok.status_code == 200 and names(tmp_path) == []


def test_bad_plan_requests(client, tmp_path):
    def post(**body):
        return client.post("/api/plan", json=body)

    assert post(operation="nope", folder=str(tmp_path)).status_code == 400
    assert post(operation="clean_by_name", folder=str(tmp_path), options={"name": ""}).status_code == 400
    assert post(operation="clean_empty_folders", folder="/").status_code == 400
    assert post(operation="clean_empty_folders", folder=str(tmp_path / "missing")).status_code == 400


def test_unknown_action_ids_rejected(client, tmp_path):
    (tmp_path / "a.tmp").write_text("x")
    plan = client.post("/api/plan", json={"operation": "clean_by_extension", "folder": str(tmp_path),
                                          "options": {"extension": ".tmp"}}).json()
    r = client.post("/api/apply", json={"plan_id": plan["plan_id"], "action_ids": [5], "confirm": "delete"})
    assert r.status_code == 400 and names(tmp_path) == ["a.tmp"]


def test_extensions_endpoint(client, tmp_path):
    (tmp_path / "a.pdf").write_text("x")
    assert client.get("/api/extensions", params={"folder": str(tmp_path)}).json() == [{"extension": ".pdf", "count": 1}]
    assert client.get("/api/extensions", params={"folder": "/"}).status_code == 400


def test_browse(client, tmp_path):
    (tmp_path / "b").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / ".hidden").mkdir()
    (tmp_path / "file.txt").write_text("x")
    data = client.get("/api/fs/browse", params={"path": str(tmp_path)}).json()
    assert data["folders"] == ["a", "b"] and data["parent"] == str(tmp_path.parent)
    assert ".hidden" in client.get("/api/fs/browse", params={"path": str(tmp_path), "hidden": True}).json()["folders"]
    assert client.get("/api/fs/browse", params={"path": "/"}).json()["blocked"]
    assert client.get("/api/fs/browse", params={"path": str(tmp_path / "file.txt")}).status_code == 400
    assert client.get("/api/fs/browse").json()["path"]


def test_log_id_traversal_is_not_found(client):
    assert client.get("/api/logs/..%2F..%2Fetc%2Fpasswd").status_code == 404
