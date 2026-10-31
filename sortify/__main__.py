import argparse
import secrets
import socket
import threading
import webbrowser

import uvicorn

from sortify.api import create_app

HOST = "127.0.0.1"


def free_port(preferred):
    """Use the preferred port when free, otherwise let the system pick one."""
    with socket.socket() as s:
        try:
            s.bind((HOST, preferred))
            return preferred
        except OSError:
            s.bind((HOST, 0))
            return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(prog="sortify", description="Sortify local web app")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser")
    args = parser.parse_args()

    port = free_port(args.port)
    token = secrets.token_urlsafe(24)
    url = f"http://{HOST}:{port}/#token={token}"

    print(f"Sortify is running. Open this link (it contains your private token):\n\n  {url}\n")
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(1.0, webbrowser.open, args=[url]).start()

    uvicorn.run(create_app(token), host=HOST, port=port, log_level="warning")


if __name__ == "__main__":
    main()
