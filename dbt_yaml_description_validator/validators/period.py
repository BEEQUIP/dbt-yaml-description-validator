def _contains_list_items(text: str) -> bool:
    """Check if text contains list items (lines starting with '- ')."""
    lines = text.splitlines()
    return any(line.lstrip().startswith("- ") for line in lines)


def check(text: str) -> bool:
    """
    Checks whether a description ends with a period.
    Skip check if the text contains list items.
    
    :param text: Input text to be checked.
    :type text: str
    :return: True if the text ends with a period (or contains lists). False else.
    :rtype: bool
    """
    # Skip period check for descriptions with list items
    if _contains_list_items(text):
        return True
    
    lines = [line.rstrip() for line in text.rstrip().splitlines() if line.strip()]
    if not lines:
        return True
    return lines[-1].endswith(".")


def fix(text: str) -> str:
    """
    Fixes a description to end with a period.
    Adds periods to texts without list items, and removes periods from texts with list items.
    
    :param text: Input text to be fixed
    :type text: str
    :return: The description with proper period handling
    :rtype: str
    """
    # Don't modify empty or whitespace-only descriptions
    if not text.strip():
        return text
    
    # Don't modify period to quoted empty strings like '' or ""
    stripped = text.strip()
    if stripped in ("''", '""'):
        return text
    
    had_trailing_newline = text.endswith("\n")
    lines = text.rstrip("\n").splitlines()
    if not lines:
        return text

    last = lines[-1].rstrip()
    
    # If text contains list items, remove trailing period from the last line
    if _contains_list_items(text):
        if last.endswith("."):
            lines[-1] = last[:-1]
    else:
        # If text doesn't contain list items, add period if missing
        if not last.endswith("."):
            lines[-1] = last + "."

    out = "\n".join(lines)
    if had_trailing_newline:
        out += "\n"
    return out