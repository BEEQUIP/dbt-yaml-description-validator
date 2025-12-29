import re

_DOUBLE_SPACES = re.compile(r"[ \t]{2,}")

def check(text: str) -> bool:
    return _DOUBLE_SPACES.search(text) is None


def fix(text: str) -> str:
    return _DOUBLE_SPACES.sub(" ", text)
