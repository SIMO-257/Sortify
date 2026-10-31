from Tasks.safety import check_folder

PREVIEW_LIMIT = 20
HELP = "(b = back to menu, q = quit)"


class BackToMenu(Exception):
    """The user typed 'b' at a prompt."""


class QuitProgram(Exception):
    """The user typed 'q' at a prompt."""


class Result:
    """Counts what happened during a run so every service ends the same way."""

    def __init__(self):
        self.moved = 0
        self.deleted = 0
        self.skipped = 0
        self.failed = []

    def fail(self, name, error):
        self.failed.append((name, error))


def ask(prompt):
    value = input(prompt).strip()
    if value.lower() == "b":
        raise BackToMenu()
    if value.lower() == "q":
        raise QuitProgram()
    return value


def ask_folder(prompt):
    """Ask until the user gives a usable folder."""
    while True:
        path, error = check_folder(ask(f"{prompt} {HELP}: "))
        if error:
            print(f"Error: {error}")
            continue
        return path


def ask_text(prompt):
    """Ask until the user gives a non-empty answer."""
    while True:
        value = ask(f"{prompt} {HELP}: ")
        if value:
            return value
        print("Error: This cannot be empty.")


def ask_choice(prompt, labels):
    """Show numbered labels and return the index the user picked."""
    for number, label in enumerate(labels, 1):
        print(f"  [{number}] {label}")
    while True:
        answer = ask(f"{prompt} (1-{len(labels)}) {HELP}: ")
        if answer.isdigit() and 1 <= int(answer) <= len(labels):
            return int(answer) - 1
        print(f"Error: Please enter a number between 1 and {len(labels)}.")


def confirm(prompt, word=None):
    """y/n question, or type a word (like 'delete') for dangerous actions."""
    while True:
        if word:
            answer = ask(f"{prompt} Type '{word}' to confirm or 'n' to cancel: ").lower()
            if answer == word:
                return True
        else:
            answer = ask(f"{prompt} (y/n): ").lower()
            if answer == "y":
                return True
        if answer == "n":
            print("❌ Operation cancelled.")
            return False
        print("❌ Wrong input.")


def ask_yes_no(prompt):
    """Plain y/n question that does not announce a cancellation."""
    while True:
        answer = ask(f"{prompt} (y/n): ").lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("❌ Wrong input, type 'y' or 'n'.")


def print_banner(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def print_list(lines, limit=PREVIEW_LIMIT):
    for line in lines[:limit]:
        print(f"  - {line}")
    if len(lines) > limit:
        print(f"  ...and {len(lines) - limit} more")


def print_summary(title, result):
    print_banner(f"✅ {title}")
    if result.moved:
        print(f"Moved:   {result.moved}")
    if result.deleted:
        print(f"Deleted: {result.deleted}")
    if result.skipped:
        print(f"Skipped: {result.skipped}")
    if result.failed:
        print(f"Failed:  {len(result.failed)}")
        for name, error in result.failed:
            print(f"  ✗ {name}: {error}")
    if not (result.moved or result.deleted or result.skipped or result.failed):
        print("Nothing was changed.")
    print("=" * 50)
