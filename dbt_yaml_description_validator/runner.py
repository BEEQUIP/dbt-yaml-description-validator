from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

from ruamel.yaml import YAML

from dbt_yaml_description_validator.validators import RULES

yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False
# yaml.width = 4096  # Prevent unwanted line wrapping
# yaml.indent(mapping=2, sequence=2, offset=0)


def iter_schema_files(files: list[str]) -> list[Path]:
    if files:
        return [Path(f) for f in files if Path(f).is_file()]
    return list(Path.cwd().rglob("schema.yml"))


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)
    return data or {}


def dump_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f)


def iter_nodes(data: dict) -> list[dict]:
    nodes = data.get("models")
    if nodes is None:
        nodes = data.get("sources")
    return nodes or []


def iter_column_dicts(node: dict) -> list[dict]:
    return node.get("columns") or []


def validate_text(check: Callable[[str], bool], text: str | None) -> bool:
    if text is None or text == "":
        return True
    return bool(check(text))


def apply_fix(fix: Callable[[str], str], text: str | None) -> tuple[str | None, bool]:
    if text is None or text == "":
        return text, False
    new_text = fix(text)
    return new_text, new_text != text


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate dbt schema.yml descriptions.")
    parser.add_argument("--rule", required=True, choices=sorted(RULES.keys()))
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    rule = RULES[args.rule]
    check_fn = getattr(rule, "check", None)
    fix_fn = getattr(rule, "fix", None)

    # Check of de functies wel callable zijn
    if not callable(check_fn):
        print(f"Rule '{args.rule}' does not define a callable 'check(text)'.", file=sys.stderr)
        return 2

    if args.fix and not callable(fix_fn):
        print(f"Rule '{args.rule}' does not support --fix.", file=sys.stderr)
        return 2

    schema_files = iter_schema_files(args.files)
    if not schema_files:
        return 0

    errors: list[str] = []

    for path in schema_files:
        try:
            data = load_yaml(path)
        except Exception as exc:
            errors.append(f"{path}: Could not parse YAML ({exc})")
            continue

        nodes = iter_nodes(data)
        modified = False

        for node in nodes:
            node_name = node.get("name")
            desc = node.get("description")

            if args.fix:
                new_desc, changed = apply_fix(fix_fn, desc)
                if changed:
                    node["description"] = new_desc
                    modified = True
            else:
                if desc and not validate_text(check_fn, desc):
                    errors.append(f"{path}: Model '{node_name}' failed rule '{args.rule}'")

            for col in iter_column_dicts(node):
                col_name = col.get("name")
                cdesc = col.get("description")

                if args.fix:
                    new_cdesc, changed = apply_fix(fix_fn, cdesc)
                    if changed:
                        col["description"] = new_cdesc
                        modified = True
                else:
                    if cdesc and not validate_text(check_fn, cdesc):
                        errors.append(f"{path}: Column '{col_name}' failed rule '{args.rule}'")

        if args.fix and modified:
            dump_yaml(path, data)

    if errors:
        # for e in errors:
        #     print(e)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
