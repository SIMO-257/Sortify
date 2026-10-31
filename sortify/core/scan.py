import os


def list_files(root_path, recursive=False, name=None):
    """Every file under root_path as (full_path, filename).

    Without recursive only the files directly inside the folder are listed.
    With name, only files whose name (without extension) contains it.
    """
    items = []
    if recursive:
        for current_root, dirs, files in os.walk(root_path):
            for file in files:
                items.append((os.path.join(current_root, file), file))
    else:
        for entry in os.listdir(root_path):
            entry_path = os.path.join(root_path, entry)
            if os.path.isfile(entry_path):
                items.append((entry_path, entry))

    if name:
        needle = name.lower()
        items = [(path, file) for path, file in items
                 if needle in os.path.splitext(file)[0].lower()]
    return items


def list_empty_folders(root_path):
    """Folders with nothing inside, including folders that only hold empty folders.

    Ordered deepest first so each one can be removed with os.rmdir.
    """
    items = []
    for current_root, dirs, files in os.walk(root_path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(current_root, folder)
            if not os.path.islink(folder_path) and is_empty_tree(folder_path):
                items.append((folder_path, folder))
    return items


def is_empty_tree(folder_path):
    for _, dirs, files in os.walk(folder_path):
        if files:
            return False
        if any(os.path.islink(os.path.join(folder_path, d)) for d in dirs):
            return False
    return True
