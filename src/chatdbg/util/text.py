import re
import textwrap


def make_arrow(pad):
    """generate the leading arrow in front of traceback or debugger"""
    if pad >= 2:
        return "-" * (pad - 2) + "> "
    elif pad == 1:
        return ">"
    return ""


def strip_ansi(s: str) -> str:
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", s)


def truncate_proportionally(text, maxlen=32000, top_proportion=0.5):
    """Omit part of a string if needed to make it fit in a maximum length."""
    if len(text) > maxlen:
        pre = max(0, int((maxlen - 5) * top_proportion))
        post = max(0, maxlen - 5 - pre)
        return text[:pre] + "[...]" + text[len(text) - post :]
    return text

def wrap_long_lines(text, width=80, subsequent_indent='    '):
    wrapped_lines = []
    for line in text.split('\n'):
        if len(line) > width:
            wrapped_lines.extend(textwrap.wrap(line, width, subsequent_indent = subsequent_indent))
        else:
            wrapped_lines.append(line)
    return '\n'.join(wrapped_lines)

def fill_to_width(text, width = 80):
    return "\n".join([ line.ljust(width) for line in text.split("\n")])
