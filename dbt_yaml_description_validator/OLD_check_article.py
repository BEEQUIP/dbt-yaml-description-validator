from pathlib import Path
import argparse
import sys
import yaml


ARTICLES = ("the ", "a ", "an ")


# ------------------------------------------------------------
# VALIDATION LOGIC
# ------------------------------------------------------------

def starts_with_article(text: str) -> bool:
    """
    Return True if the description starts with an article:
    'The', 'A', or 'An' (case-insensitive, ignoring leading whitespace).
    """
    if not text:
        return True

    stripped = text.lstrip().lower()
    return stripped.startswith(ARTICLES)


# ------------------------------------------------------------
# FILE PROCESSING
# ------------------------------------------------------------

def process_file(path: Path, errors: list[str]) -> bool:
    """
    Process a YAML file containing dbt models or sources.
    Appends validation errors to `errors`.
    Returns True if parsed successfully.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        errors.append(f"{path}: Could not parse YAML ({exc})")
        return False

    nodes = data.get("models") or data.get("sources") or []

    for node in nodes:
        desc = node.get("description")
        name = node.get("name")

        if desc and not starts_with_article(desc):
            errors.append(
                f"{path}: Model '{name}' description must start with an article (The, A, An)"
            )

        for col in node.get("columns", []):
            cdesc = col.get("description")
            cname = col.get("name")

            if cdesc and not starts_with_article(cdesc):
                errors.append(
                    f"{path}: Column '{cname}' description must start with an article (The, A, An)"
                )

    return True


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    """
    Validate that model and column descriptions start with an article.
    """
    parser = argparse.ArgumentParser(
        description="Check that dbt descriptions start with an article (The, A, An)."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional schema.yml paths (used by pre-commit)."
    )
    args = parser.parse_args()

    if args.files:
        schema_files = [Path(f) for f in args.files if Path(f).is_file()]
    else:
        schema_files = list(Path.cwd().rglob("schema.yml"))

    if not schema_files:
        print("No schema.yml files found to process.")
        sys.exit(0)

    errors: list[str] = []

    for file_path in schema_files:
        process_file(file_path, errors)

    if errors:
        # Uncomment if you want visible output in pre-commit
        # for e in errors:
        #     print(e)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
