import importlib
import re
from pathlib import Path

from Tasks.ui import BackToMenu, QuitProgram

SERVICES_DIR = Path(__file__).resolve().parent / "Services"


def service_number(file):
    match = re.search(r"\d+", file.stem)
    return int(match.group()) if match else 0


def load_services():
    services = []
    for file in sorted(SERVICES_DIR.glob("Service_*.py"), key=service_number):
        module = importlib.import_module(f"Services.{file.stem}")
        services.append({
            "name": module.service_name,
            "uuid": module.service_uuid,
            "desc": module.service_description,
            "method": module.service_method,
        })
    return services


def show_menu(services):
    print("\n" + "=" * 50)
    print("  Welcome to Sortify!")
    print("=" * 50)
    print("  Available services:\n")
    for i, svc in enumerate(services, 1):
        print(f"  [{i}] {svc['name']}")
        print(f"      {svc['desc']}")
        print()
    print("=" * 50)


def run_service(svc):
    print(f"\n  Starting: {svc['name']} ({svc['uuid']})\n")
    try:
        svc["method"]()
    except BackToMenu:
        print("\n  Back to the menu.")
        return
    print("\n  Service finished.")


def main():
    services = load_services()

    if not services:
        print("No services found in the Services folder.")
        return

    try:
        while True:
            show_menu(services)
            choice = input("  Choose a service (1-{}), or 'q' to quit: ".format(len(services))).strip()

            if choice.lower() == "q":
                break

            if choice.isdigit() and 1 <= int(choice) <= len(services):
                run_service(services[int(choice) - 1])
            else:
                print(f"  Please enter a number between 1 and {len(services)}, or 'q' to quit.")
    except (QuitProgram, KeyboardInterrupt, EOFError):
        print()

    print("Goodbye!")


if __name__ == "__main__":
    main()
