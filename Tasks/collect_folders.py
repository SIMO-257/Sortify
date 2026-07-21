import os

def collect_empty_folders(root_path):
    items = []
    for current_root, dirs, files in os.walk(root_path):
        for folder in dirs:
            folder_path = os.path.join(current_root, folder)
            if not os.listdir(folder_path):
                items.append((folder_path, folder))
    return items
