"""The local web API. It runs on 127.0.0.1 and every /api call needs the startup token."""
import os
import secrets
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sortify.core import executor, logs
from sortify.core.operations import OPERATIONS, PlanError, build_plan, scan_extensions
from sortify.core.safety import blocked_reason, check_folder, clean_path

WEB_DIR = Path(__file__).resolve().parent / "web"
MAX_PLANS = 50
LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]"}


class PlanRequest(BaseModel):
    operation: str
    folder: str
    options: dict = {}


class ApplyRequest(BaseModel):
    plan_id: str
    action_ids: Optional[list[int]] = None
    confirm: Optional[str] = None


def hostname(header):
    """'localhost:8000' -> 'localhost', '[::1]:8000' -> '[::1]'."""
    header = header.strip()
    if header.startswith("["):
        return header.split("]")[0] + "]"
    return header.split(":")[0]


def shortcuts():
    """Common folders that exist on this computer, for quick access in the folder picker."""
    home = os.path.expanduser("~")
    places = [("Home", home)] + [(name, os.path.join(home, name))
                                 for name in ("Desktop", "Downloads", "Documents", "Pictures")]
    return [{"name": name, "path": path} for name, path in places if os.path.isdir(path)]


def count_items(path):
    """How many things are inside a folder, or None when it cannot be read."""
    try:
        with os.scandir(path) as entries:
            return sum(1 for _ in entries)
    except OSError:
        return None


MAX_COUNTED_FOLDERS = 300  # counting is skipped for huge listings to keep the picker fast


def create_app(token, allowed_hosts=None):
    app = FastAPI(title="Sortify", docs_url=None, redoc_url=None, openapi_url=None)
    plans = OrderedDict()
    hosts = set(allowed_hosts or LOCAL_HOSTS)

    @app.middleware("http")
    async def only_local_hosts(request: Request, call_next):
        # Refuses requests that reached us through another name (DNS rebinding).
        if hostname(request.headers.get("host", "")) not in hosts:
            return JSONResponse({"detail": "Forbidden host"}, status_code=403)
        return await call_next(request)

    def require_token(x_sortify_token: str = Header(default="")):
        if not secrets.compare_digest(x_sortify_token.encode(), token.encode()):
            raise HTTPException(status_code=401, detail="Missing or wrong token")

    api = [Depends(require_token)]

    @app.get("/api/operations", dependencies=api)
    def list_operations():
        return [{"id": key, "name": op["name"], "description": op["description"], "options": op["options"]}
                for key, op in OPERATIONS.items()]

    @app.get("/api/extensions", dependencies=api)
    def extensions(folder: str, recursive: bool = False):
        path, error = check_folder(folder)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return scan_extensions(path, recursive)

    @app.post("/api/plan", dependencies=api)
    def make_plan(body: PlanRequest):
        try:
            plan = build_plan(body.operation, body.folder, body.options)
        except PlanError as e:
            raise HTTPException(status_code=400, detail=str(e))
        plan_id = secrets.token_hex(8)
        plans[plan_id] = plan
        while len(plans) > MAX_PLANS:
            plans.popitem(last=False)
        return {"plan_id": plan_id, **plan}

    @app.post("/api/apply", dependencies=api)
    def apply(body: ApplyRequest):
        plan = plans.get(body.plan_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="Unknown or already applied plan, build it again.")
        if plan["dangerous"] and body.confirm != "delete":
            raise HTTPException(status_code=400, detail="Type 'delete' to confirm this plan.")
        if body.action_ids is not None and not set(body.action_ids) <= {a["id"] for a in plan["actions"]}:
            raise HTTPException(status_code=400, detail="Unknown action ids.")
        del plans[body.plan_id]
        return executor.apply_plan(plan, action_ids=body.action_ids)

    @app.get("/api/logs", dependencies=api)
    def list_logs():
        return logs.list_logs()

    @app.get("/api/logs/{log_id}", dependencies=api)
    def get_log(log_id: str):
        try:
            return logs.load_log(log_id)
        except (ValueError, FileNotFoundError):
            raise HTTPException(status_code=404, detail="Log not found")

    @app.post("/api/logs/{log_id}/undo", dependencies=api)
    def undo(log_id: str):
        try:
            return executor.undo_run(log_id)
        except (ValueError, FileNotFoundError) as e:
            raise HTTPException(status_code=400, detail=str(e) or "Log not found")

    @app.get("/api/fs/browse", dependencies=api)
    def browse(path: str = "", hidden: bool = False):
        current = clean_path(path) or os.path.expanduser("~")
        if not os.path.isdir(current):
            raise HTTPException(status_code=400, detail="Not a folder")
        try:
            names = sorted(n for n in os.listdir(current) if os.path.isdir(os.path.join(current, n)))
        except PermissionError:
            raise HTTPException(status_code=403, detail="No permission to read this folder")
        if not hidden:
            names = [n for n in names if not n.startswith(".")]
        parent = os.path.dirname(current)
        count = len(names) <= MAX_COUNTED_FOLDERS
        return {
            "path": current,
            "parent": parent if parent != current else None,
            "folders": [{"name": n, "items": count_items(os.path.join(current, n)) if count else None}
                        for n in names],
            "blocked": blocked_reason(current),
            "shortcuts": shortcuts(),
        }

    if WEB_DIR.is_dir():
        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")

    return app
