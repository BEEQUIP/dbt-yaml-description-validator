def check(text: str) -> bool:
    lines = [line.rstrip() for line in text.rstrip().splitlines() if line.strip()]
    if not lines:
        return True
    return lines[-1].endswith(".")


def fix(text: str) -> str:
    lines = text.rstrip().splitlines()
    if not lines:
        return text
    last = lines[-1].rstrip()
    if last.endswith("."):
        return "\n".join(lines)
    lines[-1] = last + "."
    return "\n".join(lines)
