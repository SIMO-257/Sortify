import os
from Tasks.collect_files import list_files_flat
from Tasks.group_files import group_by_extension
from Tasks.move_files import create_folder, move_file

service_name = "File Organizer"
service_uuid = "a1b2c3"
service_description = "Organizes files in a folder by their extensions"
service_method = None

def run():
    folder_path = input("Enter the folder path to organize: ").strip()

    if not os.path.exists(folder_path):
        print("Error: Path does not exist!")
        return

    if not os.path.isdir(folder_path):
        print("Error: Path is not a folder!")
        return

    items = list_files_flat(folder_path)

    if not items:
        print("No files found in the specified folder.")
        return

    extensions, no_extension = group_by_extension(items)

    print("\n" + "="*50)
    print("📊 PRE-SCAN REPORT")
    print("="*50)
    print(f"Folder analyzed: {folder_path}")
    print(f"Total files found: {len(items)}")
    print("\nExtensions discovered:")

    for ext, file_list in extensions.items():
        print(f"  {ext} → {len(file_list)} files")

    if no_extension:
        print(f"  (no extension) → {len(no_extension)} files")

    print("="*50)

    label = input("\nEnter a label for the organization (e.g., 'office'): ").strip().lower()
    label = label.replace(" ", "_")

    cleaned_label = ""
    for char in label:
        if char.isalnum() or char == "_":
            cleaned_label += char
    label = cleaned_label

    if not label:
        print("Error: Label cannot be empty!")
        return

    label_folder = os.path.join(folder_path, label)
    if os.path.exists(label_folder):
        print(f"Error: A folder named '{label}' already exists in {folder_path}!")
        print("Please choose a different label.")
        return

    folder_names = {}

    print("\n📁 Folders to be created:")
    for ext, file_list in extensions.items():
        clean_ext = ext[1:]
        folder_name = f"{label}_{clean_ext}"
        folder_names[ext] = folder_name
        print(f"  {folder_name} → {len(file_list)} files")

    if no_extension:
        folder_name = f"{label}_no_extension"
        folder_names["no_extension"] = folder_name
        print(f"  {folder_name} → {len(no_extension)} files")

    print("\n" + "="*50)
    confirm = input("Continue with organization? (y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ Organization cancelled.")
        return

    print("✅ Starting organization...")

    for ext, folder_name in folder_names.items():
        dest_folder = os.path.join(folder_path, folder_name)
        create_folder(dest_folder)
        print(f"📁 Created folder: {folder_name}")

        file_list = no_extension if ext == "no_extension" else extensions[ext]

        for src, filename in file_list:
            try:
                unique_name = move_file(src, dest_folder, filename)
                print(f"✓ Moved: {filename} → {folder_name}/{unique_name}")
            except Exception as e:
                print(f"✗ Error moving {filename}: {e}")

    print("\n" + "="*50)
    print("✅ ORGANIZATION COMPLETE!")
    print("="*50)

    total_moved = len(items)
    print(f"Total files organized: {total_moved}")

    for ext, folder_name in folder_names.items():
        count = len(no_extension) if ext == "no_extension" else len(extensions[ext])
        if count > 0:
            print(f"  {folder_name}: {count} files")

    print("="*50)

service_method = run
