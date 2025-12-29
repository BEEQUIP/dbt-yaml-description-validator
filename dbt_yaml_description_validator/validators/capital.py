def check(text: str) -> bool:
    stripped = text.lstrip()
    return bool(stripped) and stripped[0].isupper()


def fix(text: str) -> str:
    stripped = text.lstrip()
    if not stripped:
        return text
    first = stripped[0]
    if first.isupper():
        return text
    idx = len(text) - len(stripped)
    return text[:idx] + first.upper() + text[idx + 1 :]