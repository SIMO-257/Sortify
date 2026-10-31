"""Console flows: ask, build a plan, preview it, confirm, apply it, print a summary.

All the real work is done by sortify.core, so the console and the web app behave the same.
"""
import os

from sortify.console.ui import (
    Result,
    ask_choice,
    ask_folder,
    ask_text,
    ask_yes_no,
    confirm,
    print_banner,
    print_list,
    print_summary,
)
from sortify.core import executor, logs
from sortify.core.operations import PlanError, build_plan, scan_extensions
from sortify.core.safety import check_folder


def pick_extension(folder, recursive, action):
    """Show the extensions found and return the one the user picked."""
    found = scan_extensions(folder, recursive)
    if not found:
        print("No files found in the specified folder.")
        return None

    print_banner("📊 FILE EXTENSIONS FOUND")
    print(f"Folder analyzed: {folder}")
    print(f"Total files found: {sum(f['count'] for f in found)}")
    print(f"\nChoose an extension to {action}:")
    labels = [f"{f['extension'] or '(no extension)'} ({f['count']} files)" for f in found]
    return found[ask_choice("Choose an option", labels)]["extension"]


def show_progress(action):
    name = os.path.basename(action["src"]) or action["src"]
    if action["status"] == "failed":
        print(f"✗ {action['op']} {name}: {action['error']}")
    elif action["status"] == "skipped":
        print(f"- Already in place: {name}")
    elif action["op"] == "move":
        print(f"✓ Moved: {name} → {action['final_dest']}")
    elif action["op"] == "delete":
        print(f"✓ Deleted: {name} (moved to the Sortify trash)")
    else:
        print(f"✓ Removed folder: {name}")


def run_plan(operation, folder, options, title):
    """Plan, preview, confirm and apply. Returns the log, or None when nothing was done."""
    try:
        plan = build_plan(operation, folder, options)
    except PlanError as e:
        print(f"Error: {e}")
        return None

    if not plan["actions"]:
        print("Nothing to do in the specified folder.")
        return None

    print_banner("⚠️ PREVIEW" if plan["dangerous"] else "📊 PREVIEW")
    print(f"Folder: {plan['folder']}")
    print(f"Actions planned: {len(plan['actions'])}")
    for group in plan["groups"]:
        print(f"  {group['name']} → {group['count']}")
    print_list([os.path.relpath(a["src"], plan["folder"]) for a in plan["actions"]])

    word = "delete" if plan["dangerous"] else None
    if plan["dangerous"]:
        print("\nDeleted files go to the Sortify trash and can be undone from the menu.")
    if not confirm("\nContinue?", word=word):
        return None

    log = executor.apply_plan(plan, on_progress=show_progress)
    result = Result()
    for action in log["actions"]:
        if action["status"] == "skipped":
            result.skipped += 1
        elif action["status"] == "failed":
            result.fail(os.path.basename(action["src"]), action["error"])
        elif action["op"] == "move":
            result.moved += 1
        else:
            result.deleted += 1
    print_summary(title, result)
    print(f"Run id (for undo): {log['id']}")
    return log


def organize_by_extension(recursive):
    folder = ask_folder("Enter the folder path to organize")
    label = ask_text("Enter a label for the organization (e.g., 'office')")
    run_plan("organize_by_extension", folder, {"recursive": recursive, "label": label}, "ORGANIZATION COMPLETE")


def organize_by_date(recursive):
    folder = ask_folder("Enter the folder path to organize")
    run_plan("organize_by_date", folder, {"recursive": recursive}, "ORGANIZATION COMPLETE")


def clean_by_extension(recursive):
    folder = ask_folder("Enter the folder path to clean")
    extension = pick_extension(folder, recursive, "delete")
    if extension is not None:
        run_plan("clean_by_extension", folder, {"recursive": recursive, "extension": extension}, "DELETION COMPLETE")


def clean_by_name(recursive):
    folder = ask_folder("Enter the folder path to clean")
    name = ask_text("Enter the files name to clean")
    run_plan("clean_by_name", folder, {"recursive": recursive, "name": name}, "DELETION COMPLETE")


def move_by_extension(recursive):
    folder = ask_folder("Enter the folder path to organize")
    extension = pick_extension(folder, recursive, "move")
    if extension is None:
        return
    target = ask_folder("Enter the target folder path to move the files into")
    run_plan("move_by_extension", folder,
             {"recursive": recursive, "extension": extension, "target": target}, "MOVE COMPLETE")


def clean_empty_folders():
    folder = ask_folder("Enter the folder path to clean")
    run_plan("clean_empty_folders", folder, {}, "CLEANUP COMPLETE")


def undo_last_run():
    runs = [r for r in logs.list_logs() if r["kind"] == "run" and not r["undone"]]
    if not runs:
        print("There is nothing to undo.")
        return

    print_banner("↩️ RUNS THAT CAN BE UNDONE")
    shown = runs[:10]
    labels = [f"{r['started_at']}  {r['operation']}  {r['folder']}  {r['summary']}" for r in shown]
    run = shown[ask_choice("Choose the run to undo", labels)]

    if not ask_yes_no("Undo this run?"):
        return

    log = executor.undo_run(run["id"])
    summary = log["summary"]
    print(f"Restored: {summary['done']}, failed: {summary['failed']}")
    for action in log["actions"]:
        if action["status"] == "failed":
            print(f"  ✗ {os.path.basename(action['src'])}: {action['error']}")
