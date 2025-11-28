"""
fix_descriptions.py

Recursively scans all schema.yml files in the current repository and
ensures that all model and column descriptions end with a period ('.').
Only rewrites files that contain changes for efficiency.

Usage:
    python fix_descriptions.py
"""

import yaml
from pathlib import Path
import time
from tqdm import tqdm  # Progress bar


def fix_description(description: str) -> str:
    """Ensure the description ends with a period."""
    if not isinstance(description, str):
        return description

    description = description.strip()
    if description and not description.endswith("."):
        description += "."
    return description


def fix_file(path: Path) -> bool:
    """
    Fix all model and column descriptions in a single YAML file.

    Returns True if any changes were made, False otherwise.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        # Skip unparsable files
        return False

    modified = False
    nodes = data.get("models") or data.get("sources") or []

    for node in nodes:
        if "description" in node:
            new_desc = fix_description(node["description"])
            if new_desc != node["description"]:
                node["description"] = new_desc
                modified = True

        for col in node.get("columns", []):
            if "description" in col:
                new_desc = fix_description(col["description"])
                if new_desc != col["description"]:
                    col["description"] = new_desc
                    modified = True

    if modified:
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False)

    return modified


def main():
    start_time = time.time()
    repo_root = Path.cwd()
    schema_files = list(repo_root.rglob("**/schema.yml"))

    if not schema_files:
        print("No schema.yml files found in the repository.")
        return

    fixed_files = 0

    # Process files with progress bar
    for file in tqdm(schema_files, desc="Processing schema.yml files", unit="file", ncols=100):
        if fix_file(file):
            fixed_files += 1

    duration = round(time.time() - start_time, 3)
    print(f"\nProcessed {len(schema_files)} schema.yml files.")
    print(f"Fixed descriptions in {fixed_files} files.")
    print(f"Total runtime: {duration} seconds.")


if __name__ == "__main__":
    main()
