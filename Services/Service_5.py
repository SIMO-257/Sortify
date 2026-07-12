import os

from Tasks.collect_files import list_files_recursive_withlabel

service_name = "Files Cleaner By Name - [recursive]"
service_uuid = "a2h2d3"
service_description = "Delete all files based on the file name encluding sub folders"
service_method = None

def run ():
    folder_path = input("Enter the folder path to clean: ").strip()

    if not os.path.exists(folder_path):
        print("Error: Path does not exist!")
        return

    if not os.path.isdir(folder_path):
        print("Error: Path is not a folder!")
        return

    label = input("Enter the files name to clean: ").strip()

    items = list_files_recursive_withlabel(folder_path,label)

    if not items:
         print("No files found in the specified folder.")
         return

    print("\n" + "=" * 50)
    print("📊 FILE FOUND")
    print("=" * 50)
    print(f"Folder analyzed: {folder_path}")
    print(f"Total files found: {len(items)}")

    for src, filename in items :
        print(f"  - {filename}")

    confirm = input("\nType 'delete' to confirm removal: ").strip().lower()

    while confirm != "delete":
        print("❌ Wrong input type 'delete' to confirm removal or Ctr+c to exit the program.")
        confirm = input("\nType 'delete' to confirm removal: ").strip().lower()

    deleted_count = 0
    errors = 0

    for src, filename in items:
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
