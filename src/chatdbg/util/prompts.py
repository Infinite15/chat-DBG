import json
import os
from chatdbg.util.config import chatdbg_config
from .text import truncate_proportionally
from types import NoneType
from typing import Any, Callable, List, Union

def _wrap_it(before: str, x: Union[str, NoneType], after: str="", maxlen: int=2048) -> str:
    if x:
        x = truncate_proportionally(x, maxlen, 0.5)
        before = before + ":\n" if before else ""
        after = after + "\n" if after else ""
        return f"{before}```\n{x}\n```\n{after}"
    else:
        return ""


def _concat_prompt(*args) -> str:
    args = [a for a in args if a]
    return "\n".join(args)


def _user_text_it(user_text: str) -> str:
    return user_text if user_text else "What's the bug? Give me a fix."


def build_initial_prompt(
    stack: str, error: str, details: str, command_line: str, inputs: str, history: str, extra: NoneType="", user_text: str=""
) -> str:
    return _concat_prompt(
        _wrap_it("The program has this stack trace", stack),
        _wrap_it("The program encountered the following error", error, details),
        _wrap_it("This was the command line", command_line),
        _wrap_it("This was the program's input", inputs),
        _wrap_it("This is the history of some debugger commands I ran", history),
        _wrap_it("", extra),
        _user_text_it(user_text),
    )


def build_followup_prompt(history: str, extra: str, user_text: str) -> str:
    return _concat_prompt(
        _wrap_it("This is the history of some debugger commands I ran", history),
        _wrap_it("", extra),
        _user_text_it(user_text),
    )


def initial_instructions(functions: List[Callable[[Any], Any]]) -> str:
    if chatdbg_config.instructions == "":
        file_path = os.path.join(os.path.dirname(__file__), "instructions.txt")
    else:
        file_path = chatdbg_config.instructions

    function_instructions = [json.loads(f.__doc__)["description"] for f in functions]
    with open(file_path, "r") as file:
        template = file.read()
        return template.format_map({"functions": "\n\n".join(function_instructions)})
