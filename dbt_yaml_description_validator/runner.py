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

def iter_schema_files(files: list[str]) -> list[Path]:
    """
    Maakt een lijst van paden naar alle files vanuit een opgegeven lijst. Als er geen lijst gegeven wordt, wordt er in het gehele project gezocht naar schema.y*ml files.
    Make a list of paths to all files in the given files list. If no files list is given, the project is searched for schema.y*ml files.
    
    :param files: Lijst met bestanden
    :type files: list[str]
    :return: lijst met paden naar de bestancen
    :rtype: list[Path]
    """
    if files:
        return [Path(f) for f in files if Path(f).is_file()]
    return list(Path.cwd().rglob("schema.y*ml"))


def load_yaml(path: Path) -> dict:
    """
    Load the yaml file into a python dictionary.

    :param path: path naar de yaml file
    :type path: Path
    :return: python dictionary with the contents of the yaml file
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


def fix_yaml_file_in_place(path: Path, fix_fn: Callable[[str], str]) -> bool:
    """
    Fixes the descriptions in a yaml file while preserving all formatting and structure.
    Uses careful string manipulation to modify only description values.

    :param path: Path of the yaml file
    :type path: Path
    :param fix_fn: Fix function
    :type fix_fn: Callable[[str], str]
    :return: True if the yaml is fixed somewhere. False else.
    :rtype: bool
    """
    content = path.read_text(encoding="utf-8")
    modified = False
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if 'description:' in line:
            match = re.match(r'^(\s*description:\s*)(.*)$', line)
            if match:
                prefix, value = match.groups()
                
                # Block scalar indicator (|, |-, |+, >, >-, >+)
                if not value or value in ('|', '|-', '|+', '>', '>-', '>+'):
                    new_lines.append(line)
                    i += 1
                    
                    block_start = i
                    base_indent = len(line) - len(line.lstrip())
                    
                    # Collect all indented lines that belong to this description block
                    while i < len(lines):
                        next_line = lines[i]
                        
                        if next_line.strip() == '':
                            new_lines.append(next_line)
                            i += 1
                        elif not next_line[0].isspace():
                            break
                        elif len(next_line) - len(next_line.lstrip()) <= base_indent and next_line.lstrip():
                            if ':' in next_line and len(next_line) - len(next_line.lstrip()) <= base_indent:
                                break
                            new_lines.append(next_line)
                            i += 1
                        else:
                            new_lines.append(next_line)
                            i += 1
                    
                    # Extract and fix the block content
                    block_lines = new_lines[block_start:]
                    block_indent = base_indent + 2
                    
                    stripped_lines = []
                    for bl in block_lines:
                        if bl.strip():
                            stripped_lines.append(bl[block_indent:] if len(bl) > block_indent else bl.lstrip())
                        else:
                            stripped_lines.append('')
                    
                    if stripped_lines:
                        block_content = '\n'.join(stripped_lines).rstrip()
                        fixed_block = fix_fn(block_content)
                        
                        if fixed_block != block_content:
                            modified = True
                            fixed_lines = fixed_block.split('\n')
                            new_block_lines = []
                            for fl in fixed_lines:
                                if fl:
                                    new_block_lines.append(' ' * block_indent + fl)
                                else:
                                    new_block_lines.append('')
                            
                            del new_lines[block_start:]
                            new_lines.extend(new_block_lines)
                else:
                    # Inline description
                    fixed_value = fix_fn(value)
                    if fixed_value != value:
                        modified = True
                        new_lines.append(prefix + fixed_value)
                    else:
                        new_lines.append(line)
                    i += 1
            else:
                new_lines.append(line)
                i += 1
        else:
            new_lines.append(line)
            i += 1
    
    if modified:
        new_content = '\n'.join(new_lines)
        path.write_text(new_content, encoding="utf-8")
    
    return modified


def main() -> int:
    """
    Main loop for fixing and checking description fields

    :return: 0 if no errors are found, 1 if errors are found, 2 if something went wrong with the input
    :rtype: int
    """
    parser = argparse.ArgumentParser(description="Validate dbt schema.y*ml descriptions.")
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
