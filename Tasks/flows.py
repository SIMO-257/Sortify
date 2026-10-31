"""Console flows shared by the services: scan, preview, confirm, apply, summary."""
import os

from Tasks.collect_files import (
    list_files_flat,
    list_files_flat_withlabel,
    list_files_recursive,
    list_files_recursive_withlabel,
)
from Tasks.collect_folders import collect_empty_folders
from Tasks.group_files import group_by_date_day, group_by_extension
from Tasks.move_files import create_folder, move_file
from Tasks.safety import is_inside
from Tasks.ui import (
    Result,
    ask_choice,
    ask_folder,
    ask_text,
    confirm,
    print_banner,
    print_list,
    print_summary,
)


def scan(recursive, prompt):
    """Ask for a folder and list its files. Returns (folder, items) or None."""
    folder = ask_folder(prompt)
    items = list_files_recursive(folder) if recursive else list_files_flat(folder)
    if not items:
        print("No files found in the specified folder.")
        return None
    return folder, items


def clean_label(text):
    """Lowercase, spaces to underscores, keep only letters, digits and _."""
    text = text.lower().replace(" ", "_")
    return "".join(c for c in text if c.isalnum() or c == "_")


def extension_options(extensions, no_extension):
    """[(key, label, files)] for every extension found."""
    options = [(ext, f"{ext} ({len(extensions[ext])} files)", extensions[ext])
               for ext in sorted(extensions)]
    if no_extension:
        options.append(("no_extension", f"(no extension) ({len(no_extension)} files)", no_extension))
    return options


def move_into_folders(folder, groups, result):
    """groups: {folder_name: [(src, filename)]}. Creates folders and moves files."""
    for folder_name, files in groups.items():
        dest_folder = os.path.join(folder, folder_name)
        create_folder(dest_folder)
        print(f"📁 Folder ready: {folder_name}")
        for src, filename in files:
            try:
                unique_name = move_file(src, dest_folder, filename)
                result.moved += 1
                print(f"✓ Moved: {filename} → {folder_name}/{unique_name}")
            except Exception as e:
                result.fail(filename, e)
                print(f"✗ Error moving {filename}: {e}")


def organize_by_extension(recursive):
    found = scan(recursive, "Enter the folder path to organize")
    if not found:
        return
    folder, items = found
    extensions, no_extension = group_by_extension(items)

    print_banner("📊 PRE-SCAN REPORT")
    print(f"Folder analyzed: {folder}")
    print(f"Total files found: {len(items)}" + (" (including subfolders)" if recursive else ""))
    print("\nExtensions discovered:")
    for _, label, _ in extension_options(extensions, no_extension):
        print(f"  {label}")

    label = ""
    while not label:
        label = clean_label(ask_text("\nEnter a label for the organization (e.g., 'office')"))

    groups = {f"{label}_{ext[1:]}": files for ext, files in extensions.items()}
    if no_extension:
        groups[f"{label}_no_extension"] = no_extension

    print("\n📁 Folders to be created:")
    for name, files in groups.items():
        print(f"  {name} → {len(files)} files")

    if not confirm("\nContinue with organization?"):
        return

    result = Result()
    move_into_folders(folder, groups, result)
    print_summary("ORGANIZATION COMPLETE", result)


def organize_by_date(recursive):
    found = scan(recursive, "Enter the folder path to organize")
    if not found:
        return
    folder, items = found
    dates = group_by_date_day(items)

    print_banner("📊 PRE-SCAN REPORT")
    print(f"Folder analyzed: {folder}")
    print(f"Total files found: {len(items)}")
    print("\n📁 Folders to be created:")
    for name, files in sorted(dates.items()):
        print(f"  {name} → {len(files)} files")

    if not confirm("\nContinue with organization?"):
        return

    result = Result()
    move_into_folders(folder, dates, result)
    print_summary("ORGANIZATION COMPLETE", result)


def pick_by_extension(items, folder, action):
    """Let the user pick one extension. Returns its files, or None."""
    extensions, no_extension = group_by_extension(items)
    options = extension_options(extensions, no_extension)

    print_banner("📊 FILE EXTENSIONS FOUND")
    print(f"Folder analyzed: {folder}")
    print(f"Total files found: {len(items)}")
    print(f"\nChoose an extension to {action}:")
    index = ask_choice("Choose an option", [label for _, label, _ in options])
    return options[index][1], options[index][2]


def delete_files(files, result):
    for src, filename in files:
        try:
            os.remove(src)
            result.deleted += 1
            print(f"✓ Deleted: {filename}")
        except Exception as e:
            result.fail(filename, e)
            print(f"✗ Error deleting {filename}: {e}")


def clean_by_extension(recursive):
    found = scan(recursive, "Enter the folder path to clean")
    if not found:
        return
    folder, items = found
    label, files = pick_by_extension(items, folder, "delete")

    print_banner("⚠️ DELETE PREVIEW")
    print(f"Selected: {label}")
    print(f"Files to delete: {len(files)}")
    print_list([name for _, name in files])

    if not confirm("", word="delete"):
        return

    result = Result()
    delete_files(files, result)
    print_summary("DELETION COMPLETE", result)


def clean_by_name(recursive):
    folder = ask_folder("Enter the folder path to clean")
    name = ask_text("Enter the files name to clean")
    lister = list_files_recursive_withlabel if recursive else list_files_flat_withlabel
    files = lister(folder, name)

    if not files:
        print("No files found in the specified folder.")
        return

    print_banner("📊 FILES FOUND")
    print(f"Folder analyzed: {folder}")
    print(f"Total files found: {len(files)}")
    print_list([filename for _, filename in files])

    if not confirm("", word="delete"):
        return

    result = Result()
    delete_files(files, result)
    print_summary("DELETION COMPLETE", result)


def move_by_extension(recursive):
    found = scan(recursive, "Enter the folder path to organize")
    if not found:
        return
    folder, items = found
    label, files = pick_by_extension(items, folder, "move")

    target = ask_folder("Enter the target folder path to move the files into")
    if is_inside(target, folder):
        print("Error: The target folder must be outside the source folder!")
        return

    print_banner("⚠️ MOVE PREVIEW")
    print(f"Selected: {label}")
    print(f"Files to move: {len(files)}")
    print(f"Target: {target}")
    print_list([name for _, name in files])

    if not confirm(""):
        return

    result = Result()
    for src, filename in files:
        try:
            unique_name = move_file(src, target, filename)
            result.moved += 1
            print(f"✓ Moved: {filename} → {target}/{unique_name}")
        except Exception as e:
            result.fail(filename, e)
            print(f"✗ Error moving {filename}: {e}")
    print_summary("MOVE COMPLETE", result)


def clean_empty_folders():
    folder = ask_folder("Enter the folder path to clean")
    items = collect_empty_folders(folder)

    print_banner("📊 PRE-SCAN REPORT")
    print(f"Folder analyzed: {folder}")
    print(f"Total empty folders found: {len(items)}")
    if not items:
        return
    print("\n📁 Folders to be deleted:")
    print_list([os.path.relpath(path, folder) for path, _ in items])

    if not confirm("\nContinue with deleting these folders?"):
        return

    result = Result()
    for path, name in items:
        try:
            os.rmdir(path)
            result.deleted += 1
            print(f"✓ Removed: {name}")
        except Exception as e:
            result.fail(name, e)
            print(f"✗ Error removing {name}: {e}")
    print_summary("CLEANUP COMPLETE", result)
