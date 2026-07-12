import importlib
from pathlib import Path

SERVICES_DIR = Path("Services")

def load_services():
    services = []
    for file in sorted(SERVICES_DIR.glob("*.py")):
        if file.name == "__init__.py":
            continue
        module_name = f"Services.{file.stem}"
        module = importlib.import_module(module_name)
        services.append({
            "name": module.service_name,
            "uuid": module.service_uuid,
            "desc": module.service_description,
            "method": module.service_method,
        })
    return services

def show_menu(services):
    print("\n" + "="*50)
    print("  Welcome to Sortify!")
    print("="*50)
    print("  Available services:\n")
    for i, svc in enumerate(services, 1):
        print(f"  [{i}] {svc['name']}")
        print(f"      {svc['desc']}")
        print()
    print("="*50)

def main():
    services = load_services()

    if not services:
        print("No services found in the Services folder.")
        return

    while True:
        show_menu(services)
        choice = input("  Choose a service (1-{}), or 'q' to quit: ".format(len(services))).strip()

        if choice.lower() == "q":
            print("Goodbye!")
            break

        try:
            index = int(choice) - 1
            if 0 <= index < len(services):
                svc = services[index]
                print(f"\n  Starting: {svc['name']} ({svc['uuid']})\n")
                svc["method"]()
                print("\n  Service finished. Exiting program...")
                break
            else:
                print(f"  Please enter a number between 1 and {len(services)}.")
        except ValueError:
            print("  Invalid input. Enter a number or 'q' to quit.")

if __name__ == "__main__":
    main()
