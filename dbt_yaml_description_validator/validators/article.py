ARTICLES = ("the ", "a ", "an ")

def check(text: str) -> bool:
    stripped = text.lstrip().lower()
    return stripped.startswith(ARTICLES)