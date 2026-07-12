import os
from pathlib import Path

def list_files_flat(root_path):
    items = []
    for entry in os.listdir(root_path):
        entry_path = os.path.join(root_path, entry)
        if os.path.isfile(entry_path):
            items.append((entry_path, entry))
    return items


def list_files_recursive(root_path):
    items = []
    for current_root, dirs, files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(current_root, file)
            items.append((file_path, file))
    return items

def list_files_flat_withlabel(root_path,label):
    items = []
    for entry in os.listdir(root_path):
        entry_path = os.path.join(root_path, entry)
        if os.path.isfile(entry_path):
            file_name = Path(entry_path).stem
            if label in file_name:
                items.append((entry_path, entry))
    return items

def list_files_recursive_withlabel(root_path,label):
    items = []
    for current_root,dirs,files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(current_root, file)
            file_name = Path(file_path).stem
            if label in file_name:
                items.append((file_path, file))
    return items
