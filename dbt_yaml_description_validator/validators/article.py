ARTICLES = ("the ", "a ", "an ")

def check(text: str) -> bool:
    """
    Checks whether the text starts with an article ("the ", "a ", "an ")
    
    :param text: The input text to check for a leading article.
    :type text: str
    :return: True if the text (after leading whitespace is stripped and lowercased) starts with an article; otherwise False.
    :rtype: bool
    """
    stripped = text.lstrip().lower()
    return stripped.startswith(ARTICLES)