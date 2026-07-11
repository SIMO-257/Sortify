import os

from Tasks.collect_files import list_files_recursive
from Tasks.group_files import group_by_extension

service_name = "Ultimate files Destroyer"
service_uuid = "a2b2c2"
service_description = "Delete all files based on extension including sub folders"
service_method = None 

def run():
    folder_path = input("Enter the folder path to clean: ").strip()

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
    
    options = []
    for ext in sorted(extensions.keys()):
        options.append((ext, f"{ext} ({len(extensions[ext])} files)"))

    if no_extension:
        options.append(("no_extension", f"(no extension) ({len(no_extension)} files)"))

    if not options:
        print("No files found in the specified folder.")
        return
        
    print("\n" + "=" * 50)
    print("📊 FILE EXTENSIONS FOUND")
    print("=" * 50)
    print(f"Folder analyzed: {folder_path}")
    print(f"Total files found: {len(items)}")
    print("\nChoose an extension to delete:")

    for index, (_, label) in enumerate(options, 1):
        print(f"  [{index}] {label}")

    print("=" * 50)

    choice = input(f"Choose an option (1-{len(options)}): ").strip()
    
    try:
        selected_index = int(choice) - 1
    except ValueError:
        print("Error: Invalid selection.")
        return

    if selected_index < 0 or selected_index >= len(options):
        print(f"Error: Please enter a number between 1 and {len(options)}.")
        return

    selected_key, selected_label = options[selected_index]

    if selected_key == "no_extension":
        files_to_delete = no_extension
    else:
        files_to_delete = extensions[selected_key]

    print("\n" + "=" * 50)
    print("⚠️ DELETE PREVIEW")
    print("=" * 50)
    print(f"Selected: {selected_label}")
    print(f"Files to delete: {len(files_to_delete)}")
    
    for src, filename in files_to_delete:
        print(f"  - {filename}")

    confirm = input("\nType 'delete' to confirm removal: ").strip().lower()

    if confirm != "delete":
        print("❌ Deletion cancelled.")
        return

    deleted_count = 0
    errors = 0

    for src, filename in files_to_delete:
        try:
            os.remove(src)
            deleted_count += 1
            print(f"✓ Deleted: {filename}")
        except Exception as exc:
            errors += 1
            print(f"✗ Error deleting {filename}: {exc}")

    print("\n" + "=" * 50)
    print("✅ DELETION COMPLETE")
    print("=" * 50)
    print(f"Deleted files: {deleted_count}")

    if errors:
        print(f"Errors: {errors}")

service_method = run
