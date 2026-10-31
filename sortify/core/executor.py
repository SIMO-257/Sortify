"""The only module that changes files. Applies a plan, logs it, and can undo a run."""
import os
import shutil

from sortify.core import logs
from sortify.core.safety import is_inside


def unique_path(path):
    """Add (1), (2)... before the extension until nothing exists at that path."""
    folder, filename = os.path.split(path)
    name, ext = os.path.splitext(filename)
    candidate, counter = path, 1
    while os.path.lexists(candidate):
        candidate = os.path.join(folder, f"{name}({counter}){ext}")
        counter += 1
    return candidate


def make_dirs(folder, created):
    """Create folder and remember every folder that did not exist yet."""
    missing = []
    current = folder
    while current and not os.path.exists(current):
        missing.append(current)
        current = os.path.dirname(current)
    os.makedirs(folder, exist_ok=True)
    created.extend(reversed(missing))


def allowed_destinations(plan):
    """Folders a plan may write into: its own folder and the move target, if any."""
    roots = [plan["folder"]]
    if plan["options"].get("target"):
        roots.append(plan["options"]["target"])
    return roots


def check_action(action, plan):
    """Raise ValueError when an action is outside what the plan allows."""
    src = action["src"]
    if not is_inside(src, plan["folder"]):
        raise ValueError("source is outside the chosen folder")
    if action["op"] == "move" and not any(is_inside(action["dest"], root) for root in allowed_destinations(plan)):
        raise ValueError("destination is outside the allowed folders")


def do_action(action, plan, job_id, created):
    """Perform one action and fill in what really happened. Returns 'done' or 'skipped'."""
    check_action(action, plan)
    op, src = action["op"], action["src"]

    if op == "rmdir":
        if not os.path.isdir(src):
            raise FileNotFoundError("folder no longer exists")
        os.rmdir(src)
        return "done"

    if not os.path.lexists(src) or os.path.isdir(src):
        raise FileNotFoundError("file no longer exists")

    if op == "move":
        if os.path.abspath(src) == os.path.abspath(action["dest"]):
            return "skipped"
        make_dirs(os.path.dirname(action["dest"]), created)
        final = unique_path(action["dest"])
        shutil.move(src, final)
        action["final_dest"] = final
        return "done"

    if op == "delete":
        trash_folder = os.path.join(logs.trash_dir(), job_id)
        os.makedirs(trash_folder, exist_ok=True)
        trashed = unique_path(os.path.join(trash_folder, os.path.basename(src)))
        shutil.move(src, trashed)
        action["trashed_to"] = trashed
        return "done"

    raise ValueError(f"unknown operation {op}")


def summarize(actions):
    summary = {"done": 0, "skipped": 0, "failed": 0, "pending": 0}
    for action in actions:
        summary[action["status"]] = summary.get(action["status"], 0) + 1
    return summary


def apply_plan(plan, action_ids=None, on_progress=None):
    """Run the chosen actions of a plan (all when action_ids is None) and write the log."""
    chosen = set(action_ids) if action_ids is not None else None
    actions = [dict(a, status="pending") for a in plan["actions"] if chosen is None or a["id"] in chosen]

    job_id = logs.new_id()
    created = []
    log = {
        "id": job_id, "kind": "run", "operation": plan["operation"], "folder": plan["folder"],
        "options": plan["options"], "started_at": logs.now(), "finished_at": None,
        "status": "running", "actions": actions, "created_dirs": created,
        "summary": summarize(actions), "undone": False,
    }
    logs.save_log(log)

    try:
        for number, action in enumerate(actions, 1):
            try:
                action["status"] = do_action(action, plan, job_id, created)
            except Exception as e:
                action["status"] = "failed"
                action["error"] = str(e) or e.__class__.__name__
            if on_progress:
                on_progress(action)
            if number % 25 == 0:
                log["summary"] = summarize(actions)
                logs.save_log(log)
        log["status"] = "finished"
    except BaseException:
        log["status"] = "interrupted"
        raise
    finally:
        log["finished_at"] = logs.now()
        log["summary"] = summarize(actions)
        logs.save_log(log)

    return log


def restore(src, current):
    """Put a moved file back where it came from without overwriting anything."""
    if not os.path.lexists(current):
        raise FileNotFoundError("the file is no longer where it was moved to")
    if os.path.lexists(src):
        raise FileExistsError("something already exists at the original location")
    os.makedirs(os.path.dirname(src), exist_ok=True)
    shutil.move(current, src)


def undo_run(log_id):
    """Reverse a finished run. Returns the log of the undo."""
    original = logs.load_log(log_id)
    if original.get("kind") != "run":
        raise ValueError("Only normal runs can be undone.")
    if original.get("undone"):
        raise ValueError("This run was already undone.")
    if original["status"] == "running":
        raise ValueError("This run is still in progress.")

    actions = []
    for action in reversed(original["actions"]):
        if action["status"] != "done":
            continue
        entry = {"op": "undo_" + action["op"], "src": action["src"], "status": "pending"}
        if action["op"] == "move":
            entry["from"] = action["final_dest"]
        elif action["op"] == "delete":
            entry["from"] = action["trashed_to"]
        actions.append(entry)

    undo_id = logs.new_id()
    log = {
        "id": undo_id, "kind": "undo", "undo_of": log_id, "operation": original["operation"],
        "folder": original["folder"], "started_at": logs.now(), "finished_at": None,
        "status": "running", "actions": actions, "summary": summarize(actions), "undone": False,
    }
    logs.save_log(log)

    try:
        for entry in actions:
            try:
                if entry["op"] == "undo_rmdir":
                    os.makedirs(entry["src"], exist_ok=True)
                else:
                    restore(entry["src"], entry["from"])
                entry["status"] = "done"
            except Exception as e:
                entry["status"] = "failed"
                entry["error"] = str(e) or e.__class__.__name__

        for folder in reversed(original.get("created_dirs", [])):
            try:
                os.rmdir(folder)  # only succeeds when the folder is empty
            except OSError:
                pass
        log["status"] = "finished"
    except BaseException:
        log["status"] = "interrupted"
        raise
    finally:
        log["finished_at"] = logs.now()
        log["summary"] = summarize(actions)
        logs.save_log(log)

    if log["summary"]["failed"] == 0:
        original["undone"] = True
        logs.save_log(original)
    return log
