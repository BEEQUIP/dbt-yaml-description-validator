import yaml
from pathlib import Path
import time

def check_description(description: str) -> bool:
    return description.strip().endswith(".")


def process_file(path: Path, errors: list) -> bool:
    """Parse a YAML file and collect description errors.
    Returns False if YAML could not be parsed."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return False

    nodes = data.get("models") or data.get("sources") or []

    for node in nodes:
        desc = node.get("description")
        if desc and not check_description(desc):
            errors.append(f"{path}: Model '{node.get('name')}' description missing final '.'")

        for col in node.get("columns", []):
            cdesc = col.get("description")
            if cdesc and not check_description(cdesc):
                errors.append(
                    f"{path}: Column '{col.get('name')}' description missing final '.'"
                )

    return True


def main():
    # start = time.time()

    repo_root = Path.cwd()
    schema_files = list(repo_root.rglob("**/schema.yml"))

    errors = []
    unparsable = 0

    for file in schema_files:
        if not process_file(file, errors):
            unparsable += 1

    # Print individual errors
    # if errors:
    #     print("\n".join(errors))

    # Print validation summary
    # duration = round(time.time() - start, 3)
    # print("\n--- Description Validation Summary ---")
    # print(f"Total schema.yml files found: {len(schema_files)}")
    # print(f"Unparsable files skipped: {unparsable}")
    # print(f"Descriptions missing final '.': {len(errors)}")
    # print(f"Runtime: {duration} seconds")
    # print("--------------------------------------\n")

if __name__ == "__main__":
    main()
