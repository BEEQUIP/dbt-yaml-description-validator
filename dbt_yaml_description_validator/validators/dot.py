def check(text: str) -> bool:
    lines = [line.rstrip() for line in text.rstrip().splitlines() if line.strip()]
    if not lines:
        return True
    return lines[-1].endswith(".")


def fix(text: str) -> str:
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

