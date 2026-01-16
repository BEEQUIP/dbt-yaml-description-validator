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
yaml.width = 4096  # Prevent unwanted line wrapping


def iter_schema_files(files: list[str]) -> list[Path]:
    if files:
        return [Path(f) for f in files if Path(f).is_file()]
    return list(Path.cwd().rglob("schema.yml"))


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)
    return data or {}


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


def fix_yaml_file_in_place(path: Path, fix_fn: Callable[[str], str]) -> bool:
    """Apply fixes to YAML file while preserving all formatting."""
    content = path.read_text(encoding="utf-8")
    new_content = content
    modified = False
    
    # Pattern to match description fields with their values
    # Handles: description: <quoted or unquoted value>
    #          description: | or > (block scalars)
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if 'description:' in line:
            # Check if it's a quoted/simple value on the same line
            match = re.match(r'^(\s*description:\s*)(.*)$', line)
            if match:
                prefix, value = match.groups()
                
                # If value is empty, it might be a block scalar on next line
                if not value or value in ('|', '|-', '|+', '>', '>-', '>+'):
                    # Block scalar indicator
                    new_lines.append(line)
                    i += 1
                    
                    # Collect block content until we hit next key or end
                    block_start = i
                    base_indent = len(line) - len(line.lstrip())
                    
                    while i < len(lines):
                        next_line = lines[i]
                        
                        # Empty line is part of block
                        if next_line.strip() == '':
                            new_lines.append(next_line)
                            i += 1
                        # If line starts with less indentation, it's a new key
                        elif next_line and not next_line[0].isspace():
                            break
                        elif next_line and len(next_line) - len(next_line.lstrip()) <= base_indent and next_line.lstrip():
                            # Check if it's a new key at same or lower level
                            if ':' in next_line and len(next_line) - len(next_line.lstrip()) <= base_indent:
                                break
                            new_lines.append(next_line)
                            i += 1
                        else:
                            new_lines.append(next_line)
                            i += 1
                    
                    # Now process the block content
                    block_lines = new_lines[block_start:]
                    # Join block lines, remove leading indent
                    block_text = '\n'.join(block_lines)
                    block_indent = base_indent + 2
                    
                    # Extract actual content (skip empty lines at start/end)
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
                            # Rebuild block lines with fixed content
                            fixed_lines = fixed_block.split('\n')
                            new_block_lines = []
                            for fl in fixed_lines:
                                if fl:
                                    new_block_lines.append(' ' * block_indent + fl)
                                else:
                                    new_block_lines.append('')
                            
                            # Replace the old block lines with new ones
                            del new_lines[block_start:]
                            new_lines.extend(new_block_lines)
                else:
                    # Simple value on same line (quoted or unquoted)
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
        if args.fix:
            # Use text-based approach to preserve formatting
            fix_yaml_file_in_place(path, fix_fn)
        else:
            # Use YAML parsing for validation only
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
        print(errors)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
