ARTICLES = ("the ", "a ", "an ")

def check(text: str) -> bool:
    """
    Checks whether the text starts with an article ("the ", "a ", "an ")
    
    :param text: Description
    :type text: str
    :return: Description
    :rtype: bool
    """
    stripped = text.lstrip().lower()
    return stripped.startswith(ARTICLES)