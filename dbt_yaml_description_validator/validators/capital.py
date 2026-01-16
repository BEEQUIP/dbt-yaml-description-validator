'''
Check():    Checks whether the string is non empty and starts with a capital letter
fix():      Converts the first letter to a capital letter when the first letter is not capital

Also removes leading white spaces.
'''

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
    idx = len(text) - len(stripped) # Index van de eerste letter
    return first.upper() + text[idx + 1 :]