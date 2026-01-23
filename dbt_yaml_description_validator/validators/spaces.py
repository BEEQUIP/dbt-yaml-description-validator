import re

_DOUBLE_SPACES = re.compile(r"(?<!^)(?<!\n)[ \t]{2,}")

def check(text: str) -> bool:
    """
    Checks whether a text contains a double space.
    
    :param text: Input text to be checked
    :type text: str
    :return: True if the text contains no double space. False else.
    :rtype: bool
    """
    return _DOUBLE_SPACES.search(text) is None


def fix(text: str) -> str:
    """
    Removes the double spaces from a text.

    :param text: Input text to be fixed
    :type text: str
    :return: The original text without double spaces.
    :rtype: str
    """
    return _DOUBLE_SPACES.sub(" ", text)
