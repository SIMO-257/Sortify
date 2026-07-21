import os
from Tasks.collect_folders import collect_empty_folders

service_name = "Empty Directories Cleaner"
service_uuid = "a1b2c7"
service_description = "Delete empty folders in the given path"
service_method = None

def run():
    folder_path = input("Enter the folder path to organize: ").strip()

    if not os.path.exists(folder_path):
        print("Error: Path does not exist!")
        return

    if not os.path.isdir(folder_path):
        print("Error: Path is not a folder!")
        return

    items = collect_empty_folders(folder_path)

    print("\n" + "="*50)
    print("📊 PRE-SCAN REPORT")
    print("="*50)
    print(f"Folder analyzed: {folder_path}")
    print(f"Total empty folders found: {len(items)}")
    print("\n📁 Folders to be deleted:")
    for folder_path, folder_name in items:
        print(f"  {folder_name}")
    print("\n" + "="*50)
    confirm = input("Continue with organization? (y/n): ").strip().lower()

    while confirm not in ["y","n"]:
        print("❌ Wrong input type 'y'or 'n' to confirm organization or Ctr+c to exit the program.")
        confirm = input("Continue with organization? (y/n): ").strip().lower()

    if confirm == 'n':
        print("❌ Organization cancelled.")
        return

    print("✅ Starting organization...")

    total_moved = 0

    for folder_path,folder_name in items:
        try:
            os.removedirs(folder_path)
            total_moved += 1
            print(f"✓ Removed: {folder_name} → {folder_path}")
        except Exception as e:
            print(f"✗ Error moving {folder_name}: {e}")

    print("\n" + "="*50)
    print("✅ ORGANIZATION COMPLETE!")
    print("="*50)

    print(f"Total folders removeded: {total_moved}")

service_method = run
