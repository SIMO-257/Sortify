import os

# Folders that must never be organized or cleaned, nor anything inside them.
SYSTEM_DIRS = [
    "/bin", "/boot", "/dev", "/etc", "/lib", "/lib64", "/proc", "/run",
    "/sbin", "/sys", "/usr", "/System", "/Library", "/Applications",
]
WINDOWS_DIRS = ["windows", "program files", "program files (x86)", "programdata"]


def clean_path(raw):
    """Turn what the user typed or pasted into an absolute path."""
    path = raw.strip().strip('"').strip("'").strip()
    if not path:
        return ""
    return os.path.abspath(os.path.expanduser(path))


def is_inside(child, parent):
    """True when child is parent itself or lives somewhere below it."""
    child = os.path.normcase(os.path.realpath(child))
    parent = os.path.normcase(os.path.realpath(parent))
    try:
        return os.path.commonpath([child, parent]) == parent
    except ValueError:  # different drives on Windows
        return False


def blocked_reason(path):
    """Return why a folder is too dangerous to touch, or None if it is fine."""
    real = os.path.realpath(path)
    drive, tail = os.path.splitdrive(real)

    if tail in (os.sep, ""):
        return "this is the root of the disk"

    if real == os.path.realpath(os.path.expanduser("~")):
        return "this is your home folder, pick a folder inside it"

    for system_dir in SYSTEM_DIRS:
        if os.name != "nt" and is_inside(real, system_dir):
            return f"{system_dir} is a system folder"

    if os.name == "nt":
        parts = [p.lower() for p in tail.split(os.sep) if p]
        if parts and parts[0] in WINDOWS_DIRS:
            return f"{parts[0]} is a system folder"

    return None


def check_folder(raw):
    """Validate a typed folder path. Returns (path, error); error is None when ok."""
    path = clean_path(raw)

    if not path:
        return None, "Path cannot be empty."
    if not os.path.exists(path):
        return None, "Path does not exist!"
    if not os.path.isdir(path):
        return None, "Path is not a folder!"

    reason = blocked_reason(path)
    if reason:
        return None, f"Refusing to use this folder: {reason}."

    return path, None
