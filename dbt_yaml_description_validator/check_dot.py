from pathlib import Path
import time
import argparse
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
    return True


def main():
    """
    Validate or fix descriptions in a single schema.yml file.
    Designed so it can be called once per file by pre-commit.
    """

    parser = argparse.ArgumentParser(
        description="Check or fix descriptions in a schema.yml file."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix descriptions missing a trailing period."
    )
    parser.add_argument(
        "file",
        help="Single schema.yml file to process."
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"{path}: File does not exist.")
        return 1

    if args.fix:
        changed = process_file(path, fix=True)
        if changed:
            print(f"Fixed descriptions in: {path}")
        return 0

    # Validation mode
    errors = []
    ok = process_file(path, fix=False, errors=errors)

    if not ok:
        print(f"{path}: Could not process YAML.")
        return 1

    if errors:
        for e in errors:
            print(e)
        return 1  # Signal failure for pre-commit

    return 0


if __name__ == "__main__":
    main()