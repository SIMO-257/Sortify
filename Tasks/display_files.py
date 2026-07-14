
def display_files_by_extensiones(items,folder_path,extensions,no_extension):

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
        files_to_move = no_extension
    else:
        files_to_move = extensions[selected_key]

    print("\n" + "=" * 50)
    print("⚠️ MOVE PREVIEW")
    print("=" * 50)
    print(f"Selected: {selected_label}")
    print(f"Files to move: {len(files_to_move)}")

    for src, filename in files_to_move:
        print(f"  - {filename}")

    confirm = input("Continue with the operation? (y/n): ").strip().lower()

    while confirm not in ["y","n"]:
        print("❌ Wrong input type 'y'or 'n' to confirm the operation or Ctr+c to exit the program.")
        confirm = input("Continue with the operation? (y/n): ").strip().lower()

    if confirm == 'n':
         print("❌ Operation cancelled.")
         return

    return files_to_move
