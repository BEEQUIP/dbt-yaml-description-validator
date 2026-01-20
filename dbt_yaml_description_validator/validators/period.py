def check(text: str) -> bool:
    """
    Checks whether a description ends with a period.
    
    :param text: Input text to be checked.
    :type text: str
    :return: True if the text ends with a period. False else.
    :rtype: bool
    """
    lines = [line.rstrip() for line in text.rstrip().splitlines() if line.strip()]
    if not lines:
        return True
    return lines[-1].endswith(".")

def fix(text: str) -> str:
    """
    Fixes a description to end with a period.
    
    :param text: Input text to be fixed
    :type text: str
    :return: The description with a trailing period
    :rtype: bool
    """
    # Don't add period to empty or whitespace-only descriptions
    if not text.strip():
        return text
    
    # Don't add period to quoted empty strings like '' or ""
    stripped = text.strip()
    if stripped in ("''", '""'):
        return text
    
    had_trailing_newline = text.endswith("\n")

    lines = text.rstrip("\n").splitlines()
    if not lines:
        return text

    last = lines[-1].rstrip()
    if not last.endswith("."):
        lines[-1] = last + "."

    out = "\n".join(lines)
    if had_trailing_newline:
        out += "\n"
    return out
