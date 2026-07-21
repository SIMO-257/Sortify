import os

from Tasks.collect_files import list_files_flat
from Tasks.group_files import group_by_date_day
from Tasks.move_files import create_folder, move_file


service_name = "Files Orginzer Date Based(Days) - [flat]"
service_uuid = "a1l2n4"
service_description = "Orginizing files based on their date(days) excluding subfolders"
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

    dates = group_by_date_day(items)

    print("\n" + "="*50)
    print("📊 PRE-SCAN REPORT")
    print("="*50)
    print(f"Folder analyzed: {folder_path}")
    print(f"Total files found: {len(items)}")
    print("\nDates discovered:")
    print("\n📁 Folders to be created:")
    for folder, file_list in dates.items():
       print(f"  {folder} → {len(file_list)} files")

    print("\n" + "="*50)
    confirm = input("Continue with organization? (y/n): ").strip().lower()

    while confirm not in ["y","n"]:
        print("❌ Wrong input type 'y'or 'n' to confirm organization or Ctr+c to exit the program.")
        confirm = input("Continue with organization? (y/n): ").strip().lower()

    if confirm == 'n':
        print("❌ Organization cancelled.")
        return

    print("✅ Starting organization...")

    for folder,files in dates.items():
        dest_folder = os.path.join(folder_path, folder)
        create_folder(dest_folder)
        print(f"📁 Created folder: {folder}")

        for src, filename in dates[folder]:
            try:
                unique_name = move_file(src, dest_folder, filename)
                print(f"✓ Moved: {filename} → {folder}/{unique_name}")
            except Exception as e:
                print(f"✗ Error moving {filename}: {e}")

    print("\n" + "="*50)
    print("✅ ORGANIZATION COMPLETE!")
    print("="*50)

    total_moved = len(items)
    print(f"Total files organized: {total_moved}")


service_method = run
