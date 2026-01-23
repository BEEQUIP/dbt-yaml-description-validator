from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable
from ruamel.yaml import YAML
from dbt_yaml_description_validator.validators import RULES

yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False
yaml.width = 4096
yaml.indent(mapping=2, sequence=2, offset=2)
yaml.explicit_start = False
yaml.allow_unicode = True
yaml.sequence_indent=2

def iter_schema_files(files: list[str]) -> list[Path]:
    """
    Maakt een lijst van paden naar alle files vanuit een opgegeven lijst. Als er geen lijst gegeven wordt, wordt er in het gehele project gezocht naar schema.yml files.
    Make a list of paths to all files in the given files list. If no files list is given, the project is searched for schema.yml files.
    
    :param files: Lijst met bestanden
    :type files: list[str]
    :return: lijst met paden naar de bestancen
    :rtype: list[Path]
    """
    if files:
        return [Path(f) for f in files if Path(f).is_file()]
    return list(Path.cwd().rglob("schema.yml"))


def load_yaml(path: Path) -> dict:
    """
    Load the yaml file into a python dictionary.

    :param path: path naar de yaml file
    :type path: Path
    :return: python dictionary met inhoud van de yaml
    :rtype: dict
    """
    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)
    return data or {}


def iter_nodes(data: dict) -> list[dict]:
    """
    Go to the models/source level of the dictionary.
    
    :param data: Original dictionary of the yaml file
    :type data: dict
    :return: model/source level of the original yaml file
    :rtype: list[dict]
    """
    nodes = data.get("models")
    if nodes is None:
        nodes = data.get("sources")
    return nodes or []


def iter_column_dicts(node: dict) -> list[dict]:
    """
    Go to the columns level of the dictionary.
    
    :param node: Models/source level dictionary
    :type node: dict
    :return: Column level dictionary
    :rtype: list[dict]
    """
    return node.get("columns") or []


def validate_text(check: Callable[[str], bool], text: str | None) -> bool:
    """
    Method to apply a "Check" function to a text. 
    
    :param check: Check function
    :type check: Callable[[str], bool]
    :param text: Text to be checked
    :type text: str | None
    :return: True if the text satisfy the checking criterion. False else.
    :rtype: bool
    """
    if text is None or text == "":
        return True
    return bool(check(text))


def apply_fix(fix: Callable[[str], str], text: str | None) -> tuple[str | None, bool]:
    """
    Method to apply a "Fix" function to a text.
    
    :param fix: Fix function
    :type fix: Callable[[str], str]
    :param text: Text to be fixed
    :type text: str | None
    :return: The fixed text and a boolean indicating if the text has changed
    :rtype: tuple[str | None, bool]
    """
    if text is None or text == "":
        return text, False
    new_text = fix(text)
    return new_text, new_text != text


def fix_yaml_file_in_place(path: Path, fix_fn: Callable[[str], str]) -> bool:
    """Fixes descriptions in a yaml file using ruamel.yaml."""
    data = load_yaml(path)  # Uses ruamel.yaml
    modified = False
    
    nodes = iter_nodes(data)
    for node in nodes:
        desc = node.get("description")
        if desc:
            fixed_desc, changed = apply_fix(fix_fn, desc)
            if changed:
                node["description"] = fixed_desc
                modified = True
        
        for col in iter_column_dicts(node):
            cdesc = col.get("description")
            if cdesc:
                fixed_desc, changed = apply_fix(fix_fn, cdesc)
                if changed:
                    col["description"] = fixed_desc
                    modified = True
    
    if modified:
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f)
    
    return modified


def main() -> int:
    """
    Main loop for fixing and checking description fields

    :return: 0 if no errors are found, 1 if errors are found, 2 if something went wrong with the input
    :rtype: int
    """
    parser = argparse.ArgumentParser(description="Validate dbt schema.yml descriptions.")
    parser.add_argument("--rule", required=True, choices=sorted(RULES.keys()))
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    rule = RULES[args.rule]
    check_fn = getattr(rule, "check", None)
    fix_fn = getattr(rule, "fix", None)

    # Checks for early break (no callable method provided, no files provided)
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
        if args.fix:
            fix_yaml_file_in_place(path, fix_fn)
        else:
            try:
                data = load_yaml(path)
            except Exception as exc:
                errors.append(f"{path}: Could not parse YAML ({exc})")
                continue

            nodes = iter_nodes(data)

            for node in nodes:
                node_name = node.get("name")
                desc = node.get("description")

                if desc and not validate_text(check_fn, desc):
                    errors.append(f"{path}: Model '{node_name}' failed rule '{args.rule}'")

                for col in iter_column_dicts(node):
                    col_name = col.get("name")
                    cdesc = col.get("description")

                    if cdesc and not validate_text(check_fn, cdesc):
                        errors.append(f"{path}: Column '{col_name}' failed rule '{args.rule}'")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
