#!/usr/bin/env python3
"""Interactive menu agent for the DreamerV3 repository.

Presents a menu of options and performs the selected action:
  1. Summary of the repository
  2. Show the TODO list
  3. Exit
"""

import os
import pathlib
import re
import textwrap


REPO_ROOT = pathlib.Path(__file__).parent


def get_repo_summary():
    """Return a summary of the repository from the README."""
    readme_path = REPO_ROOT / 'README.md'
    if not readme_path.exists():
        return "README.md not found."

    text = readme_path.read_text(encoding='utf-8')

    # Strip markdown image/link syntax for cleaner display
    text = re.sub(r'!\[.*?\]\(.*?\)', '[image]', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Display everything up to (but not including) the '# Instructions' section
    lines = text.splitlines()
    summary_lines = []
    for line in lines:
        if re.match(r'^#\s+Instructions\b', line.strip(), re.IGNORECASE):
            break
        summary_lines.append(line)

    summary = '\n'.join(summary_lines).strip()
    return summary or text.strip()


def get_todo_list():
    """Scan the repository for TODO/FIXME/HACK/XXX comments and return them."""
    # Match TODO-style tags only when they appear in code comments or after
    # comment markers (#, //, /*, <!--) to avoid matching string literals.
    comment_pattern = re.compile(
        r'(?:#|//|/\*|<!--).*\b(TODO|FIXME|HACK|XXX)\b.*', re.IGNORECASE
    )

    # Extensions covering all source/config/doc file types in this repository
    extensions = {'.py', '.yaml', '.yml', '.md', '.txt', '.sh'}
    # Exclude this script itself from the scan
    this_script = pathlib.Path(__file__).resolve()
    results = []

    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip hidden directories and common non-essential directories
        dirs[:] = [
            d for d in dirs
            if not d.startswith('.')
            and d not in ('__pycache__', 'node_modules', '.git')
        ]
        for filename in sorted(files):
            if pathlib.Path(filename).suffix not in extensions:
                continue
            filepath = (pathlib.Path(root) / filename).resolve()
            if filepath == this_script:
                continue
            rel_path = filepath.relative_to(REPO_ROOT)
            try:
                file_text = filepath.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            for lineno, line in enumerate(file_text.splitlines(), start=1):
                if comment_pattern.search(line):
                    results.append((str(rel_path), lineno, line.strip()))

    return results


def display_menu():
    """Display the main menu."""
    print()
    print("=" * 50)
    print("       DreamerV3 Repository Menu Agent")
    print("=" * 50)
    print("  1. Summary of the repository")
    print("  2. Show the TODO list")
    print("  3. Exit")
    print("=" * 50)


def handle_summary():
    """Display the repository summary."""
    print()
    print("-" * 50)
    print(" REPOSITORY SUMMARY")
    print("-" * 50)
    summary = get_repo_summary()
    for line in summary.splitlines():
        stripped = line.strip()
        if not stripped:
            print()
        elif stripped.startswith('#'):
            # Headings: print as-is
            print(stripped)
        else:
            # Wrap prose lines at 72 characters
            print(textwrap.fill(stripped, width=72))
    print()


def handle_todos():
    """Display all TODO items found in the repository."""
    print()
    print("-" * 50)
    print(" TODO LIST")
    print("-" * 50)
    todos = get_todo_list()
    if not todos:
        print("No TODO items found in the repository.")
    else:
        current_file = None
        for filepath, lineno, line in todos:
            if filepath != current_file:
                print(f"\n{filepath}:")
                current_file = filepath
            print(f"  Line {lineno:4d}: {line}")
    print()


def main():
    """Run the interactive menu agent."""
    print()
    print("Welcome to the DreamerV3 Repository Menu Agent!")

    while True:
        display_menu()
        try:
            choice = input("Enter your choice (1-3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if choice == '1':
            handle_summary()
        elif choice == '2':
            handle_todos()
        elif choice == '3':
            print("\nGoodbye!")
            break
        else:
            print(f"\nInvalid choice '{choice}'. Please enter 1, 2, or 3.")


if __name__ == '__main__':
    main()
