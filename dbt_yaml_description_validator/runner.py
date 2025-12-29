from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

import yaml

from dbt_yaml_description_validator.validators import RULES


def iter_schema_files(files: list[str]) -> list[Path]:
    if files:
        return [Path(f) for f in files if Path(f).is_file()]
    return list(Path.cwd().rglob("schema.yml"))


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def dump_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)


def iter_nodes(data: dict) -> list[dict]:
    nodes = data.get("models")
    if nodes is None:
        nodes = data.get("sources")
    return nodes or []


def iter_columns(node: dict) -> list[dict]:
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

    if not callable(check_fn):
        return 2

    if args.fix and not callable(fix_fn):
        return 2

    schema_files = iter_schema_files(args.files)
    if not schema_files:
        return 0

    failed = False

    for path in schema_files:
        try:
            data = load_yaml(path)
        except Exception:
            return 1

        nodes = iter_nodes(data)
        modified = False

        for node in nodes:
            desc = node.get("description")

            if args.fix:
                new_desc, changed = apply_fix(fix_fn, desc)  # type: ignore[arg-type]
                if changed:
                    node["description"] = new_desc
                    modified = True
            else:
                if desc and not validate_text(check_fn, desc):
                    failed = True

            for col in iter_columns(node):
                cdesc = col.get("description")

                if args.fix:
                    new_cdesc, changed = apply_fix(fix_fn, cdesc)  # type: ignore[arg-type]
                    if changed:
                        col["description"] = new_cdesc
                        modified = True
                else:
                    if cdesc and not validate_text(check_fn, cdesc):
                        failed = True

        if args.fix and modified:
            dump_yaml(path, data)

    if args.fix:
        return 0

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
