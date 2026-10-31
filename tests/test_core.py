import json
import os

import pytest

from sortify.core import executor, logs
from sortify.core.operations import PlanError, build_plan, scan_extensions


def write(path, text="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def names(path):
    return sorted(p.name for p in path.iterdir())


def tree(path):
    return sorted(str(p.relative_to(path)) for p in path.rglob("*"))


def test_plan_changes_nothing(tmp_path):
    write(tmp_path / "a.pdf")
    before = tree(tmp_path)
    plan = build_plan("organize_by_extension", str(tmp_path), {"label": "docs"})
    assert plan["actions"][0]["dest"].endswith(os.path.join("docs_pdf", "a.pdf"))
    assert tree(tmp_path) == before


def test_plan_errors(tmp_path):
    with pytest.raises(PlanError):
        build_plan("nope", str(tmp_path), {})
    with pytest.raises(PlanError):
        build_plan("organize_by_extension", str(tmp_path), {"label": "!!!"})
    with pytest.raises(PlanError):
        build_plan("clean_by_name", str(tmp_path), {"name": "  "})
    with pytest.raises(PlanError):
        build_plan("clean_by_extension", str(tmp_path), {})
    with pytest.raises(PlanError):
        build_plan("clean_empty_folders", "/", {})
    with pytest.raises(PlanError):
        build_plan("clean_empty_folders", str(tmp_path / "missing"), {})


def test_organize_by_extension_flat_and_recursive(tmp_path):
    write(tmp_path / "a.pdf")
    write(tmp_path / "sub" / "b.pdf")
    write(tmp_path / "noext")
    flat = build_plan("organize_by_extension", str(tmp_path), {"label": "d"})
    assert len(flat["actions"]) == 2
    deep = build_plan("organize_by_extension", str(tmp_path), {"label": "d", "recursive": True})
    assert len(deep["actions"]) == 3
    executor.apply_plan(deep)
    assert names(tmp_path / "d_pdf") == ["a.pdf", "b.pdf"]
    assert names(tmp_path / "d_no_extension") == ["noext"]


def test_organizing_twice_does_not_rename_files(tmp_path):
    write(tmp_path / "a.pdf")
    options = {"label": "d", "recursive": True}
    executor.apply_plan(build_plan("organize_by_extension", str(tmp_path), options))
    log = executor.apply_plan(build_plan("organize_by_extension", str(tmp_path), options))
    assert log["summary"]["skipped"] == 1
    assert names(tmp_path / "d_pdf") == ["a.pdf"]


def test_same_names_are_never_overwritten(tmp_path):
    write(tmp_path / "one" / "a.txt", "one")
    write(tmp_path / "two" / "a.txt", "two")
    executor.apply_plan(build_plan("organize_by_extension", str(tmp_path), {"label": "d", "recursive": True}))
    assert sorted(p.read_text() for p in (tmp_path / "d_txt").iterdir()) == ["one", "two"]


def test_organize_by_date(tmp_path):
    f = write(tmp_path / "a.txt")
    os.utime(f, (86400 * 365, 86400 * 365))
    executor.apply_plan(build_plan("organize_by_date", str(tmp_path), {}))
    assert len(names(tmp_path)) == 1 and names(tmp_path)[0].startswith("19")


def test_delete_goes_to_trash_and_can_be_undone(tmp_path):
    write(tmp_path / "a.tmp", "keep me")
    write(tmp_path / "b.txt")
    plan = build_plan("clean_by_extension", str(tmp_path), {"extension": ".TMP"})
    assert plan["dangerous"] and len(plan["actions"]) == 1
    log = executor.apply_plan(plan)
    assert names(tmp_path) == ["b.txt"]
    assert open(log["actions"][0]["trashed_to"]).read() == "keep me"

    undo = executor.undo_run(log["id"])
    assert undo["summary"]["done"] == 1
    assert (tmp_path / "a.tmp").read_text() == "keep me"
    assert logs.load_log(log["id"])["undone"] is True


def test_delete_by_name_is_case_insensitive_and_matches_stem(tmp_path):
    write(tmp_path / "Report1.txt")
    write(tmp_path / "other.report")
    plan = build_plan("clean_by_name", str(tmp_path), {"name": "report"})
    assert [os.path.basename(a["src"]) for a in plan["actions"]] == ["Report1.txt"]


def test_move_by_extension_and_undo(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    write(src / "a.jpg")
    dst.mkdir()
    plan = build_plan("move_by_extension", str(src), {"extension": ".jpg", "target": str(dst)})
    log = executor.apply_plan(plan)
    assert names(dst) == ["a.jpg"]
    executor.undo_run(log["id"])
    assert names(src) == ["a.jpg"] and names(dst) == []


def test_undo_removes_folders_the_run_created(tmp_path):
    write(tmp_path / "a.pdf")
    log = executor.apply_plan(build_plan("organize_by_extension", str(tmp_path), {"label": "d"}))
    assert names(tmp_path) == ["d_pdf"]
    executor.undo_run(log["id"])
    assert names(tmp_path) == ["a.pdf"]


def test_move_target_inside_source_is_refused(tmp_path):
    write(tmp_path / "a.jpg")
    (tmp_path / "t").mkdir()
    with pytest.raises(PlanError):
        build_plan("move_by_extension", str(tmp_path), {"extension": ".jpg", "target": str(tmp_path / "t")})


def test_empty_folders_removed_deepest_first_and_undone(tmp_path):
    root = tmp_path / "work"
    (root / "a" / "b").mkdir(parents=True)
    write(root / "full" / "f.txt")
    plan = build_plan("clean_empty_folders", str(root), {})
    assert len(plan["actions"]) == 2
    log = executor.apply_plan(plan)
    assert root.exists() and names(root) == ["full"]
    executor.undo_run(log["id"])
    assert (root / "a" / "b").is_dir()


def test_only_selected_actions_run(tmp_path):
    write(tmp_path / "a.tmp")
    write(tmp_path / "b.tmp")
    plan = build_plan("clean_by_extension", str(tmp_path), {"extension": ".tmp"})
    executor.apply_plan(plan, action_ids=[plan["actions"][0]["id"]])
    assert len(names(tmp_path)) == 1


def test_apply_refuses_actions_outside_the_plan_folder(tmp_path):
    inside, outside = tmp_path / "in", tmp_path / "out"
    write(inside / "a.tmp")
    write(outside / "precious.txt")
    plan = build_plan("clean_by_extension", str(inside), {"extension": ".tmp"})
    plan["actions"].append({"id": 99, "op": "delete", "src": str(outside / "precious.txt")})
    log = executor.apply_plan(plan)
    assert (outside / "precious.txt").exists()
    assert log["summary"]["failed"] == 1


def test_missing_file_is_reported_as_failed_not_a_crash(tmp_path):
    f = write(tmp_path / "a.tmp")
    plan = build_plan("clean_by_extension", str(tmp_path), {"extension": ".tmp"})
    f.unlink()
    log = executor.apply_plan(plan)
    assert log["summary"]["failed"] == 1 and "no longer exists" in log["actions"][0]["error"]


def test_undo_does_not_overwrite(tmp_path):
    write(tmp_path / "a.tmp", "old")
    log = executor.apply_plan(build_plan("clean_by_extension", str(tmp_path), {"extension": ".tmp"}))
    write(tmp_path / "a.tmp", "new")
    undo = executor.undo_run(log["id"])
    assert undo["summary"]["failed"] == 1
    assert (tmp_path / "a.tmp").read_text() == "new"


def test_undo_twice_is_refused(tmp_path):
    write(tmp_path / "a.tmp")
    log = executor.apply_plan(build_plan("clean_by_extension", str(tmp_path), {"extension": ".tmp"}))
    executor.undo_run(log["id"])
    with pytest.raises(ValueError):
        executor.undo_run(log["id"])


def test_logs_are_valid_json_and_listed_newest_first(tmp_path, sortify_home):
    write(tmp_path / "a.tmp")
    first = executor.apply_plan(build_plan("clean_by_extension", str(tmp_path), {"extension": ".tmp"}))
    second = executor.undo_run(first["id"])
    runs = logs.list_logs()
    assert runs[0]["id"] == second["id"]
    with open(sortify_home / "logs" / f"{first['id']}.json") as f:
        assert json.load(f)["status"] == "finished"
    assert not list((sortify_home / "logs").glob("*.tmp"))


def test_log_ids_cannot_escape_the_logs_folder():
    with pytest.raises(ValueError):
        logs.load_log("../../etc/passwd")


def test_scan_extensions(tmp_path):
    write(tmp_path / "a.PDF"); write(tmp_path / "b.pdf"); write(tmp_path / "c")
    assert scan_extensions(str(tmp_path), False) == [
        {"extension": ".pdf", "count": 2}, {"extension": "", "count": 1}]
