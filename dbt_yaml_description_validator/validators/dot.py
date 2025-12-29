def check(text: str) -> bool:
    lines = [line.rstrip() for line in text.rstrip().splitlines() if line.strip()]
    if not lines:
        return True
    return lines[-1].endswith(".")


def fix(text: str) -> str:
    if check(text):
        return text

    lines = text.splitlines()
    if not lines:
        return text

    last = lines[-1].rstrip()
    lines[-1] = last + "."
    result = "\n".join(lines)

    if text.endswith("\n"):
        result += "\n"

    return result
