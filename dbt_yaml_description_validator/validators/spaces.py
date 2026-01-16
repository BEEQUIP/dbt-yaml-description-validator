import re

_DOUBLE_SPACES = re.compile(r"(?<!^)(?<!\n)[ \t]{2,}")

def check(text: str) -> bool:
    return _DOUBLE_SPACES.search(text) is None


def fix(text: str) -> str:
    return _DOUBLE_SPACES.sub(" ", text)
    # # Only replace double spaces that are not at the beginning of lines
    # # Split by lines, process each, and rejoin
    # lines = text.split('\n')
    # fixed_lines = []
    # for line in lines:
    #     # Find where actual content starts (skip leading spaces)
    #     stripped = line.lstrip()
    #     leading_spaces = len(line) - len(stripped)
    #     # Apply fix only to the content part, not the indentation
    #     fixed_content = _DOUBLE_SPACES.sub(" ", stripped)
    #     fixed_lines.append(' ' * leading_spaces + fixed_content)
    # return '\n'.join(fixed_lines)
