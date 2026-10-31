"""Run history stored as one JSON file per run in ~/.sortify/logs."""
import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone

ID_PATTERN = re.compile(r"^[0-9A-Za-z_-]+$")


def home_dir():
    """Where Sortify keeps its logs and trash. Override with SORTIFY_HOME."""
    return os.environ.get("SORTIFY_HOME") or os.path.join(os.path.expanduser("~"), ".sortify")


def logs_dir():
    path = os.path.join(home_dir(), "logs")
    os.makedirs(path, exist_ok=True)
    return path


def trash_dir():
    path = os.path.join(home_dir(), "trash")
    os.makedirs(path, exist_ok=True)
    return path


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id():
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%f")
    return f"{stamp}_{uuid.uuid4().hex[:6]}"


def log_path(log_id):
    if not ID_PATTERN.match(log_id):
        raise ValueError("Invalid log id")
    return os.path.join(logs_dir(), f"{log_id}.json")


def save_log(log):
    """Write the log to a temp file then rename it so it is never half-written."""
    path = log_path(log["id"])
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def load_log(log_id):
    path = log_path(log_id)
    if not os.path.exists(path):
        raise FileNotFoundError(log_id)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_logs():
    """Short info about every run, newest first."""
    runs = []
    for file in sorted(os.listdir(logs_dir()), reverse=True):
        if not file.endswith(".json"):
            continue
        try:
            with open(os.path.join(logs_dir(), file), encoding="utf-8") as f:
                log = json.load(f)
        except (OSError, ValueError):
            continue
        runs.append({key: log.get(key) for key in (
            "id", "operation", "kind", "folder", "started_at", "finished_at",
            "status", "summary", "undone", "undo_of")})
    return runs
