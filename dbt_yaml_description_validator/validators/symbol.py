import re

SYMBOL_PATTERN = re.compile(r"[€$£¥%#@&*^=+<>|~]") # Best strict, kan ook versoepeld worden

def check(text: str) -> bool:
    return not bool(SYMBOL_PATTERN.search(text))
