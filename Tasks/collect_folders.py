import os


def collect_empty_folders(root_path):
    """Folders with nothing inside, including folders that only hold empty folders.

    The list is ordered deepest first so each one can be removed with os.rmdir.
    """
    items = []
    for current_root, dirs, files in os.walk(root_path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(current_root, folder)
            if os.path.islink(folder_path):
                continue
            if is_empty_tree(folder_path):
                items.append((folder_path, folder))
    return items


def is_empty_tree(folder_path):
    for _, dirs, files in os.walk(folder_path):
        if files:
            return False
        if any(os.path.islink(os.path.join(folder_path, d)) for d in dirs):
            return False
    return True
