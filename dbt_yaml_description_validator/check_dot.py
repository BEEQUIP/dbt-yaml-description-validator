"""
dbt_yaml_description_checker.py

Recursively scans all schema.yml files in the repository to check
if model and column descriptions end with a period. Optionally,
fixes missing periods if the --fix flag is used.

Usage:
    # Just check
    python dbt_yaml_description_checker.py

    # Check and automatically fix
    python dbt_yaml_description_checker.py --fix
"""

import yaml
from pathlib import Path
import time
from tqdm import tqdm
import argparse


def check_description(description: str) -> bool:
    """Return True if description ends with a period."""
    return isinstance(description, str) and description.strip().endswith(".")


def fix_description(description: str) -> str:
    """Return description ending with a period."""
    if not isinstance(description, str):
        return description
    description = description.strip()
    if description and not description.endswith("."):
        description += "."
    return description


def process_file(path: Path, fix: bool = False) -> tuple[list[str], bool]:
    """
    Check/fix descriptions in a YAML file.

    Args:
        path (Path): Path to schema.yml
        fix (bool): If True, missing periods are added

    Returns:
        errors (list): List of description errors
        modified (bool): True if file was modified
    """
    errors = []
    modified = False

    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        errors.append(f"{path}: Could not parse YAML")
        return errors, False

    nodes = data.get("models") or data.get("sources") or []

    for node in nodes:
        desc = node.get("description")
        if desc and not check_description(desc):
            errors.append(f"{path}: Model '{node.get('name')}' description missing final '.'")
            if fix:
                node["description"] = fix_description(desc)
                modified = True

        for col in node.get("columns", []):
            cdesc = col.get("description")
            if cdesc and not check_description(cdesc):
                errors.append(f"{path}: Column '{col.get('name')}' description missing final '.'")
                if fix:
                    col["description"] = fix_description(cdesc)
                    modified = True

    if fix and modified:
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False)

    return errors, modified


def main():
    """
    Docstring for main
    """
    parser = argparse.ArgumentParser(description="Check/fix YAML descriptions.")
    parser.add_argument("--fix", action="store_true", help="Automatically fix missing periods")
    args = parser.parse_args()

    start_time = time.time()
    repo_root = Path.cwd()
    schema_files = list(repo_root.rglob("**/schema.yml"))

    if not schema_files:
        print("No schema.yml files found in the repository.")
        return

    total_errors = []
    modified_files = 0
    unparsable_files = 0

    for file in tqdm(schema_files, desc="Processing schema.yml files", unit="file", ncols=100):
        errors, modified = process_file(file, fix=args.fix)
        if errors and "Could not parse YAML" in errors[0]:
            unparsable_files += 1
        if modified:
            modified_files += 1
        total_errors.extend(errors)

    duration = round(time.time() - start_time, 3)

    # Print errors if checking (or fixing)
    if total_errors and not args.fix:
        print("\n".join(total_errors))

    print("\n--- Description Summary ---")
    print(f"Total schema.yml files found: {len(schema_files)}")
    print(f"Unparsable files skipped: {unparsable_files}")
    print(f"Descriptions missing final '.': {len(total_errors) if not args.fix else 'N/A (auto-fixed)'}")
    if args.fix:
        print(f"Files modified: {modified_files}")
    print(f"Runtime: {duration} seconds")
    print("----------------------------\n")


if __name__ == "__main__":
    main()
