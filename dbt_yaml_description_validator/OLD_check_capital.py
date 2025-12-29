from pathlib import Path
import argparse
import sys
import yaml


# ------------------------------------------------------------
# VALIDATION LOGIC
# ------------------------------------------------------------

def fix_description(text: str) -> str:
    """Return a possibly fixed version of the description."""
    if not text:
        return text
    stripped = text.lstrip()
    if not stripped:
        return text
    if stripped[0].isupper():
        return text
    return text.replace(stripped[0], stripped[0].upper(), 1)


def validate_description(text: str) -> bool:
    """Return True if the description is considered valid."""
    if not text:
        return True
    stripped = text.lstrip()
    return stripped[0].isupper()


# ------------------------------------------------------------
# FILE PROCESSING
# ------------------------------------------------------------

def process_file(path: Path, fix: bool = False, errors: list | None = None) -> bool:
    """
    Process a YAML file containing dbt models or sources.
    If fix=True, descriptions are modified in-place.
    If fix=False, invalid descriptions append messages to `errors`.
    Returns True if the file was modified (fix mode) or parsed successfully.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        if not fix and errors is not None:
            errors.append(f"{path}: Could not parse YAML ({exc})")
        return False

    nodes = data.get("models") or data.get("sources") or []
    modified = False

    for node in nodes:
        desc = node.get("description")

        if fix:
            new_desc = fix_description(desc)
            if new_desc != desc:
                node["description"] = new_desc
                modified = True
        else:
            if desc and not validate_description(desc):
                errors.append(f"{path}: Model '{node.get('name')}' description invalid")

        for col in node.get("columns", []):
            cdesc = col.get("description")

            if fix:
                new_desc = fix_description(cdesc)
                if new_desc != cdesc:
                    col["description"] = new_desc
                    modified = True
            else:
                if cdesc and not validate_description(cdesc):
                    errors.append(f"{path}: Column '{col.get('name')}' description invalid")

    if fix and modified:
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False)

    return modified


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    """
    Validate or fix descriptions in schema.yml files.
    Use the --fix flag to automatically fix the descriptions.
    """
    parser = argparse.ArgumentParser(description="Validate or fix dbt description fields.")
    parser.add_argument("--fix", action="store_true", help="Automatically fix descriptions.")
    parser.add_argument("files", nargs="*", help="Optional schema.yml paths.")
    args = parser.parse_args()

    if args.files:
        schema_files = [Path(f) for f in args.files if Path(f).is_file()]
    else:
        schema_files = list(Path.cwd().rglob("schema.yml"))

    if not schema_files:
        print("No schema.yml files found to process.")
        sys.exit(0)

    if args.fix:
        for file_path in schema_files:
            process_file(file_path, fix=True)
        sys.exit(0)

    errors = []
    for file_path in schema_files:
        process_file(file_path, fix=False, errors=errors)

    if errors:
        # for e in errors:
        #     print(e)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
