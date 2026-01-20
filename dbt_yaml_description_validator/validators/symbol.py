import re

SYMBOL_PATTERN = re.compile(r"[€$£%#@&*^+~]")

def check(text: str) -> bool:
    """
    Checks whether a text contains one of the following characters: "€, $, £, %, #, @, &, *, ^, +, ~"

    :param text: Input text to be checked
    :type text: str
    :return: True if the description contains one of the symbols. False else.
    :rtype: bool
    """
    return not bool(SYMBOL_PATTERN.search(text))
