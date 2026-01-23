def check(text: str) -> bool:
    """
    Checks whether a description starts with a capital letter.
    
    :param text: The input text to be checked
    :type text: str
    :return: True if the input text starts with a capital letter. False else.
    :rtype: bool
    """
    stripped = text.lstrip()
    return bool(stripped) and stripped[0].isupper()


def fix(text: str) -> str:
    """
    Fixes a description to starts with a capital letter.
    
    :param text: The input text to be fixed
    :type text: str
    :return: The corrected text starting with a capital letter.
    :rtype: bool
    """
    stripped = text.lstrip()
    if not stripped:
        return text
    first = stripped[0]
    if first.isupper():
        return text
    idx = len(text) - len(stripped)
    return first.upper() + text[idx + 1 :]