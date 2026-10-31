# Sortify

Sortify organizes, moves and cleans files **on your own computer**. It has two interfaces that share one engine:

- a **console menu** (`python index.py`), and
- a **local web app** (`python -m sortify`) that opens in your browser. Nothing is uploaded, the server only listens on `127.0.0.1`.

## What it can do

| Operation | Description |
|---|---|
| Organize by extension | Move files into `<label>_<extension>` folders |
| Organize by date | Move files into one folder per modification day |
| Move by extension | Move all files with one extension into another folder |
| Delete by extension | Delete all files with one extension |
| Delete by name | Delete files whose name contains some text (case-insensitive) |
| Remove empty folders | Remove folders that contain no files |
| Undo | Put back the files of a previous run |

All operations except "remove empty folders" work on one folder, or on the folder and all its subfolders.

## Safety

- **Preview first.** Every operation builds a plan and shows it. Nothing changes until you confirm. Deleting needs you to type `delete`.
- **Deleted files go to a trash folder** (`~/.sortify/trash`), so a run can be undone.
- **Nothing is overwritten.** If a name is taken, the file becomes `name(1).ext`.
- **Dangerous folders are refused**: the disk root, your home folder and system folders.
- **Every run is logged** as a JSON file in `~/.sortify/logs`. Set `SORTIFY_HOME` to move this folder.

## Run it

```bash
pip install -e .          # installs fastapi and uvicorn
python -m sortify         # web app, opens your browser
python index.py           # console menu
```

The web app prints a private link ending in `#token=...`. Open that link: the token stops other websites
from talking to the server on your machine. Options: `--port 9000`, `--no-browser`.

In the console, type `b` at any prompt to go back to the menu and `q` to quit.

## Project layout

```
sortify/
  core/            the engine, no printing or input()
    safety.py      path checks, blocked folders
    scan.py        list files and empty folders
    group.py       group by extension or date
    operations.py  build a plan (a list of actions) without touching files
    executor.py    the only code that changes files; apply and undo
    logs.py        JSON logs and trash location
  console/         prompts and console flows built on the core
  api.py           FastAPI app (token, host check, plan/apply/logs/undo/browse)
  web/             the built frontend, served by the API
Services/          the console menu entries (index.py loads them)
frontend/          React + Vite + TypeScript source of the web app
tests/             pytest
```

### API

| Endpoint | Purpose |
|---|---|
| `GET /api/operations` | operations and their options |
| `GET /api/extensions` | extensions found in a folder |
| `POST /api/plan` | build a plan, changes nothing |
| `POST /api/apply` | apply the chosen actions of a plan |
| `GET /api/logs`, `GET /api/logs/{id}` | history |
| `POST /api/logs/{id}/undo` | undo a run |
| `GET /api/fs/browse` | list folders for the folder picker |

All calls need the `X-Sortify-Token` header.

## Development

```bash
pip install -e ".[dev]"
pytest

cd frontend
npm install
npm run build      # writes into sortify/web
npm run dev        # dev server, proxies /api to 127.0.0.1:8000
```
