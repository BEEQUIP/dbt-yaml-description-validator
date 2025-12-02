"""
manage_descriptions.py

Recursively scans all schema.yml files in the current repository and
checks or fixes that all model and column descriptions end with a period ('.').

Usage:
    python manage_descriptions.py          # Just checks
    python manage_descriptions.py --fix    # Fixes missing periods
"""

from pathlib import Path
import time
import argparse
import yaml
from tqdm import tqdm

def normalize_description(description: str) -> str:
    """Ensure the description ends with a period."""
    if not isinstance(description, str):
        return description

    description = description.strip()
    if description and not description.endswith("."):
        description += "."
    return description


def check_description(description: str) -> bool:
    """Check if the description ends with a period."""
    if not isinstance(description, str):
        return True  # Non-strings are ignored
    return description.strip().endswith(".")


def process_file(path: Path, fix: bool = False, errors: list = None) -> bool:
    """
    Process a YAML file.
    If fix=True, modifies descriptions and writes back the file.
    If fix=False, collects errors in `errors` list.

    Returns True if any changes were made or if file was parsed successfully.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        if not fix and errors is not None:
            errors.append(f"{path}: Could not parse YAML ({e})")
        return False


    nodes = data.get("models") or data.get("sources") or []
    modified = False

    for node in nodes:
        desc = node.get("description")
        if fix:
            new_desc = normalize_description(desc)
            if new_desc != desc:
                node["description"] = new_desc
                modified = True
        else:
            if desc and not check_description(desc):
                errors.append(f"{path}: Model '{node.get('name')}' description missing final '.'")

        for col in node.get("columns", []):
            cdesc = col.get("description")
            if fix:
                new_cdesc = normalize_description(cdesc)
                if new_cdesc != cdesc:
                    col["description"] = new_cdesc
                    modified = True
            else:
                if cdesc and not check_description(cdesc):
                    errors.append(f"{path}: Column '{col.get('name')}' missing final '.'")

    if fix and modified:
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False)

    return True


def main():
    """
    Check or fix descriptions in all schema.yml files.
    
    By default, validates that descriptions end with a period.
    With --fix, adds a period to any missing descriptions.
    """
    
    parser = argparse.ArgumentParser(description="Check or fix descriptions in schema.yml files.")
    parser.add_argument("--fix", action="store_true", help="Fix missing periods in descriptions")
    args = parser.parse_args()

    start_time = time.time()
    repo_root = Path.cwd()
    schema_files = list(repo_root.rglob("**/schema.yml"))

    if not schema_files:
        print("No schema.yml files found in the repository.")
        return

    if args.fix:
        fixed_files = 0
        for file in tqdm(schema_files, desc="Fixing schema.yml files", unit="file", ncols=100):
            if process_file(file, fix=True):
                fixed_files += 1
        print(f"\nProcessed {len(schema_files)} schema.yml files.")
        print(f"Fixed descriptions in {fixed_files} files.")
    else:
        errors = []
        unparsable = 0
        for file in schema_files:
            if not process_file(file, fix=False, errors=errors):
                unparsable += 1
        if errors:
            print("\n".join(errors))
        print("\n--- Description Validation Summary ---")
        print(f"Total schema.yml files found: {len(schema_files)}")
        print(f"Unparsable files skipped: {unparsable}")
        print(f"Descriptions missing final '.': {len(errors)}")
        print("--------------------------------------")

    duration = round(time.time() - start_time, 3)
    print(f"Total runtime: {duration} seconds")


if __name__ == "__main__":
    main()
