import re


def make_arrow(pad):
    """generate the leading arrow in front of traceback or debugger"""
    if pad >= 2:
        return "-" * (pad - 2) + "> "
    elif pad == 1:
        return ">"
    return ""


def strip_color(s):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", s)


def truncate_proportionally(text, maxlen=32000, top_proportion=0.5):
    """Omit part of a string if needed to make it fit in a maximum length."""
    if len(text) > maxlen:
        pre = max(0, int((maxlen - 3) * top_proportion))
        post = max(0, maxlen - 3 - pre)
        return text[:pre] + "..." + text[len(text) - post :]
    return text

