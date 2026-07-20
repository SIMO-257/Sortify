# Sortify

Sortify is a modular Python command-line tool for organizing, moving, and cleaning up files on your computer. It presents an interactive menu where you can pick from a set of pluggable "services", each of which performs a different file operation.

## How it works

- `index.py` is the entry point. It automatically discovers every service file in the `Services/` folder and lists them in an interactive menu. Selecting a service runs its `service_method`.
- `Services/` contains the individual features. Each service module exports four values: `service_name`, `service_uuid`, `service_description`, and `service_method`.
- `Tasks/` holds the reusable building blocks shared by the services:
  - `collect_files.py` — listing files (flat or recursive, optionally filtered by name)
  - `group_files.py` — grouping files by their extension
  - `move_files.py` — creating folders and safely moving files (avoiding name collisions)
  - `display_files.py` — printing a report of discovered files

## Features

- **Organize by extension** — group files into folders named by their extension, either in the current folder or recursively through subfolders.
- **Move by extension** — move files matching certain extensions from one folder into another.
- **Clean by name** — find and delete files whose name contains a given label, with a confirmation step before anything is removed.

## Getting started

Run the program from the project root:

```bash
python index.py
```

Follow the on-screen prompts to choose a service and provide a folder path. Most services show a pre-scan report and ask for confirmation before making any changes to your files.
