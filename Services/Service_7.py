import os
import shutil

from Tasks.collect_files import list_files_recursive
from Tasks.display_files import display_files_by_extensiones
from Tasks.group_files import group_by_extension

service_name = "Files Replacer Extension Based - [recursive]"
service_uuid = "a1l2n3"
service_description = "Moving files from a folder to another based on extension including subfolders"
service_method = None

def run():
    folder_path = input("Enter the folder path to organize: ").strip()

    if not os.path.exists(folder_path):
        print("Error: Path does not exist!")
        return

    if not os.path.isdir(folder_path):
        print("Error: Path is not a folder!")
        return

    items = list_files_recursive(folder_path)

    if not items:
        print("No files found in the specified folder.")
        return

    extensions, no_extension = group_by_extension(items)

    file_list = display_files_by_extensiones(items,folder_path,extensions,no_extension)

    if not file_list:
        return

    target_path = input("Enter the target folder path to move the files into: ").strip()

    if not os.path.exists(target_path):
        print("Error: Path does not exist!")
        return

    if not os.path.isdir(target_path):
        print("Error: Path is not a folder!")
        return

    confirm = input("Continue with organization? (y/n): ").strip().lower()

    while confirm not in ["y","n"]:
        print("❌ Wrong input type 'y'or 'n' to confirm the operation or Ctr+c to exit the program.")
        confirm = input("Continue with othe operation? (y/n): ").strip().lower()

    if confirm == 'n':
        print("❌ Operation cancelled.")
        return

    for src, file_name in file_list:
        try:
            dest = os.path.join(target_path, file_name)
            shutil.move(src, dest)
            print(f"✓ Moved: {file_name} → {target_path}/")
        except Exception as e:
            print(f"✗ Error moving {file_name}: {e}")
    print("\n" + "="*50)
    print("✅ ORGANIZATION COMPLETE!")
    print("="*50)

    total_moved = len(file_list)
    print(f"Total files organized: {total_moved}")

service_method = run
