"""Operations build a plan: a list of actions that would be done. They never change files.

An action is a dict:
    {"id": 0, "op": "move",   "src": "...", "dest": "..."}   dest is the wanted path
    {"id": 1, "op": "delete", "src": "..."}                  goes to the trash folder
    {"id": 2, "op": "rmdir",  "src": "..."}                  removes an empty folder
"""
import os

from sortify.core.group import group_by_date_day, group_by_extension
from sortify.core.safety import check_folder, is_inside
from sortify.core.scan import list_empty_folders, list_files


class PlanError(ValueError):
    """The options given for an operation are not usable."""


def clean_label(text):
    """Lowercase, spaces to underscores, keep only letters, digits and _."""
    text = text.lower().replace(" ", "_")
    return "".join(c for c in text if c.isalnum() or c == "_")


def extension_key(extension):
    """'.PDF' -> '.pdf'. An empty string means files without an extension."""
    return extension.strip().lower()


def scan_extensions(folder, recursive):
    """[{'extension': '.pdf', 'count': 3}] with '' for no extension."""
    extensions, no_extension = group_by_extension(list_files(folder, recursive))
    found = [{"extension": ext, "count": len(files)} for ext, files in sorted(extensions.items())]
    if no_extension:
        found.append({"extension": "", "count": len(no_extension)})
    return found


def files_with_extension(folder, recursive, extension):
    extensions, no_extension = group_by_extension(list_files(folder, recursive))
    return no_extension if extension == "" else extensions.get(extension, [])


def make_plan(operation, folder, options, actions, groups, dangerous=False):
    for number, action in enumerate(actions):
        action["id"] = number
    return {
        "operation": operation,
        "folder": folder,
        "options": options,
        "actions": actions,
        "groups": [{"name": name, "count": count} for name, count in groups],
        "dangerous": dangerous,
    }


def moves_into_folders(folder, groups):
    """groups: {folder_name: [(src, filename)]} -> move actions."""
    actions = []
    for folder_name, files in groups.items():
        for src, filename in files:
            actions.append({"op": "move", "src": src, "dest": os.path.join(folder, folder_name, filename)})
    return actions


def organize_by_extension(folder, options):
    label = clean_label(str(options.get("label", "")))
    if not label:
        raise PlanError("A label is required (letters, digits and _).")

    extensions, no_extension = group_by_extension(list_files(folder, bool(options.get("recursive"))))
    groups = {f"{label}_{ext[1:]}": files for ext, files in sorted(extensions.items())}
    if no_extension:
        groups[f"{label}_no_extension"] = no_extension

    actions = moves_into_folders(folder, groups)
    summary = [(f"{name}/", len(files)) for name, files in groups.items()]
    return make_plan("organize_by_extension", folder, {**options, "label": label}, actions, summary)


def organize_by_date(folder, options):
    dates = group_by_date_day(list_files(folder, bool(options.get("recursive"))))
    actions = moves_into_folders(folder, dates)
    summary = [(f"{name}/", len(files)) for name, files in sorted(dates.items())]
    return make_plan("organize_by_date", folder, options, actions, summary)


def clean_by_extension(folder, options):
    if "extension" not in options:
        raise PlanError("Choose an extension.")
    extension = extension_key(str(options["extension"]))
    files = files_with_extension(folder, bool(options.get("recursive")), extension)
    actions = [{"op": "delete", "src": src} for src, _ in files]
    label = extension or "(no extension)"
    return make_plan("clean_by_extension", folder, {**options, "extension": extension}, actions,
                     [(f"delete {label}", len(files))], dangerous=True)


def clean_by_name(folder, options):
    name = str(options.get("name", "")).strip()
    if not name:
        raise PlanError("The file name cannot be empty (it would match every file).")
    files = list_files(folder, bool(options.get("recursive")), name)
    actions = [{"op": "delete", "src": src} for src, _ in files]
    return make_plan("clean_by_name", folder, {**options, "name": name}, actions,
                     [(f"names containing '{name}'", len(files))], dangerous=True)


def move_by_extension(folder, options):
    if "extension" not in options:
        raise PlanError("Choose an extension.")
    target, error = check_folder(str(options.get("target", "")))
    if error:
        raise PlanError(f"Target folder: {error}")
    if is_inside(target, folder):
        raise PlanError("The target folder must be outside the source folder.")

    extension = extension_key(str(options["extension"]))
    files = files_with_extension(folder, bool(options.get("recursive")), extension)
    actions = [{"op": "move", "src": src, "dest": os.path.join(target, filename)} for src, filename in files]
    return make_plan("move_by_extension", folder, {**options, "extension": extension, "target": target},
                     actions, [(f"move to {target}", len(files))])


def clean_empty_folders(folder, options):
    empty = list_empty_folders(folder)
    actions = [{"op": "rmdir", "src": path} for path, _ in empty]
    return make_plan("clean_empty_folders", folder, options, actions,
                     [("empty folders", len(empty))])


RECURSIVE = {"name": "recursive", "label": "Include subfolders", "type": "bool", "default": False}
EXTENSION = {"name": "extension", "label": "Extension", "type": "extension", "required": True}

OPERATIONS = {
    "organize_by_extension": {
        "name": "Organize by extension",
        "description": "Move files into folders named <label>_<extension>.",
        "options": [RECURSIVE, {"name": "label", "label": "Label for the folders", "type": "text", "required": True}],
        "plan": organize_by_extension,
    },
    "organize_by_date": {
        "name": "Organize by date",
        "description": "Move files into one folder per modification day (YYYY-MM-DD).",
        "options": [RECURSIVE],
        "plan": organize_by_date,
    },
    "move_by_extension": {
        "name": "Move by extension",
        "description": "Move all files with one extension into another folder.",
        "options": [RECURSIVE, EXTENSION,
                    {"name": "target", "label": "Target folder", "type": "folder", "required": True}],
        "plan": move_by_extension,
    },
    "clean_by_extension": {
        "name": "Delete by extension",
        "description": "Delete all files with one extension. They go to the Sortify trash and can be undone.",
        "options": [RECURSIVE, EXTENSION],
        "plan": clean_by_extension,
    },
    "clean_by_name": {
        "name": "Delete by name",
        "description": "Delete files whose name contains some text. They go to the Sortify trash and can be undone.",
        "options": [RECURSIVE, {"name": "name", "label": "Text in the file name", "type": "text", "required": True}],
        "plan": clean_by_name,
    },
    "clean_empty_folders": {
        "name": "Remove empty folders",
        "description": "Remove folders that contain no files.",
        "options": [],
        "plan": clean_empty_folders,
    },
}


def build_plan(operation, raw_folder, options):
    """Validate the folder and options, then return the plan for the operation."""
    if operation not in OPERATIONS:
        raise PlanError(f"Unknown operation: {operation}")
    folder, error = check_folder(raw_folder)
    if error:
        raise PlanError(error)
    return OPERATIONS[operation]["plan"](folder, dict(options or {}))
