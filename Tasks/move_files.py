import os


def get_unique_filename(destination_folder, filename):
    name, ext = os.path.splitext(filename)
    unique_name = filename
    counter = 1
    while os.path.exists(os.path.join(destination_folder, unique_name)):
        unique_name = f"{name}({counter}){ext}"
        counter += 1
    return unique_name


def create_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)


def move_file(src, destination_folder, filename):
    unique_name = get_unique_filename(destination_folder, filename)
    dest = os.path.join(destination_folder, unique_name)
    os.rename(src, dest)
    return unique_name
