from pathlib import Path
# import time
import argparse
import sys
import yaml

def normalize_description(description: str) -> str:
    """Ensure the description ends with a period."""

    lines = description.rstrip().splitlines()
    if not lines:
        return description

    if not lines[-1].rstrip().endswith("."):
        lines[-1] = lines[-1].rstrip() + "."

    return "\n".join(lines)

def check_description(description: str) -> bool:
    """Check if the description ends with a period."""

    lines = [line.rstrip() for line in description.rstrip().splitlines() if line.strip()]
    if not lines:
        return True
    return lines[-1].endswith(".")



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
    return modified


def main():
    """
    Validate or fix descriptions in schema.yml files.

    By default, checks that model and column descriptions end with a period.
    Use the --fix flag to automatically append missing periods.
    Accepts optional file paths (used by pre-commit).
    """

    parser = argparse.ArgumentParser(
        description="Check or fix descriptions in schema.yml files."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix descriptions missing a trailing period."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional list of schema files to process. Defaults to all schema.yml files."
    )
    args = parser.parse_args()

    # start_time = time.time()

    # Determine target files
    if args.files:
        schema_files = [Path(f) for f in args.files if Path(f).is_file()]
    else:
        schema_files = list(Path.cwd().rglob("**/schema.yml"))

    if not schema_files:
        print("No schema.yml files found to process.")
        return

    if args.fix:
        fixed_count = 0
        for file_path in schema_files:
            if process_file(file_path, fix=True):
                fixed_count += 1
        sys.exit(0)

    else:
        errors = []
        unparsable_count = 0
        for file_path in schema_files:
            if not process_file(file_path, fix=False, errors=errors):
                unparsable_count += 1

        if errors:
            sys.exit(1)


if __name__ == "__main__":
    main()
