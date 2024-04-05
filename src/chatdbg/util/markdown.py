import re
import textwrap

from chatdbg.util.text import wrap_long_lines
from ..assistant.listeners import BaseAssistantListener
from rich.console import Console
from rich.live import Live
from rich.markdown import *
from rich.panel import Panel
from rich.theme import Theme
from rich.style import Style
from rich.text import Text
from rich import box
import os

from io import StringIO
from types import *
from typing import *

def _make_themes() -> Dict[str, Tuple[Theme, str]]:
    _dark = (
        Theme(
            {
                "markdown.paragraph": "bright_cyan",
                "markdown.text": "bright_cyan",
                "markdown.code": "white",
                "markdown.code_block": "cyan",
                "markdown.item.bullet": "bold cyan",
                "markdown.item.number": "bold cyan",
                "markdown.h1": "bold bright_cyan",
                "markdown.h2": "bold bright_cyan",
                "markdown.h3": "bold bright_cyan",
                "markdown.h4": "bold bright_cyan",
                "markdown.h5": "bold bright_cyan",
                "command": "bold bright_yellow",
                "result": "yellow",
            }
        ),
        "monokai",
    )

    _light = (
        Theme(
            {
                "markdown.block": "bright_blue",
                "markdown.paragraph": "bright_blue",
                "markdown.text": "bright_blue",
                "markdown.code": "cyan",
                "markdown.code_block": "blue",
                "markdown.item.bullet": "bold blue",
                "markdown.item.number": "bold blue",
                "markdown.h1": "bold blue",
                "markdown.h2": "bold blue",
                "markdown.h3": "bold blue",
                "markdown.h4": "bold blue",
                "markdown.h5": "bold blue",
                "command": "bold yellow",
                "result": "yellow",
            }
        ),
        "default",
    )

    _paper = (
        Theme(
            {
                "none": "black on light_steel_blue1",
                "markdown.block": "black on light_steel_blue1",
                "markdown.paragraph": "black on light_steel_blue1",
                "markdown.text": "black on light_steel_blue1",
                "markdown.code": "blue",
                "markdown.code_block": "blue",
                "markdown.item.bullet": "bold blue",
                "markdown.item.number": "bold blue",
                "markdown.h1": "bold black",
                "markdown.h2": "bold black",
                "markdown.h3": "bold black",
                "markdown.h4": "bold black",
                "markdown.h5": "bold black",
                "command": "bold black on wheat1",
                "result": "black on wheat1",
            }
        ),
        "default",
    )

    return {"light": _light, "dark": _dark, "paper": _paper}




# Don't center headings
class LeftHeading(TextElement):
    """A heading."""

    @classmethod
    def create(cls, markdown: "Markdown", token: Token) -> "LeftHeading":
        return cls(token.tag)

    def on_enter(self, context: "MarkdownContext") -> None:
        self.text = Text()
        context.enter_style(self.style_name)

    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.style_name = f"markdown.{tag}"
        super().__init__()

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = self.text
        if self.tag == "h2":
            yield Text("")
        yield text


# class CodeBlock(TextElement):
#     """A code block with syntax highlighting."""

#     style_name = "markdown.code_block"

#     @classmethod
#     def create(cls, markdown: "Markdown", token: Token) -> "CodeBlock":
#         node_info = token.info or ""
#         lexer_name = node_info.partition(" ")[0]
#         return cls(lexer_name or "text", markdown.code_theme)

#     def __init__(self, lexer_name: str, theme: str) -> None:
#         self.lexer_name = lexer_name

#         self.theme = theme

#     def __rich_console__(
#         self, console: Console, options: ConsoleOptions
#     ) -> RenderResult:
#         code = str(self.text).rstrip()
#         syntax = Syntax(
#             code, self.lexer_name, theme=self.theme, word_wrap=True, padding=0
#         )
#         yield syntax


class ChatDBGMarkdownPrinter(BaseAssistantListener):

    themes = _make_themes()

    def __init__(
        self, out, debugger_prompt, chat_prefix, width, stream=False, theme="light"
    ):
        self._out = out
        self._debugger_prompt = debugger_prompt
        self._chat_prefix = chat_prefix
        self._width = min(width, os.get_terminal_size().columns)
        self._stream = stream
        self._theme, self._code_theme = ChatDBGMarkdownPrinter.themes[theme]
        self._console = Console(soft_wrap=False, file=out, theme=self._theme, width=self._width)
        # Markdown.elements['fence'] = CodeBlock
        # Markdown.elements['code_block'] = CodeBlock
        # Markdown.elements["heading_open"] = LeftHeading  # Causes a Crash now...

    # Call backs

    def on_begin_query(self, prompt, user_text):
        pass

    def on_end_query(self, stats):
        pass

    def _print(self, text, **kwargs):
        if text.strip():
            self._console.print(text, end="")

    def _wrap_in_panel(self, rich_element):
        return Panel(
            rich_element, box=box.MINIMAL, padding=(0, 0, 0, len(self._chat_prefix) - 1), style="on black"
        )

    def on_warn(self, text):
        self._print(textwrap.indent(text + "\n\n", "*** "))

    def on_begin_stream(self):
        self._streamed = ""

    def _stream_append(self, text):
        self._streamed += text
        m = self._wrap_in_panel(Markdown(self._streamed, code_theme=self._code_theme))
        self._live.update(m)

    def on_stream_delta(self, text):
        if self._streamed == "":
            self._live = Live(vertical_overflow="visible", console=self._console)
            self._live.start(True)
        self._stream_append(text)

    def on_end_stream(self):
        if self._streamed != "":
            self._live.stop()

    def on_response(self, text):
        if not self._stream and text != None:
            m = self._wrap_in_panel(Markdown(text, code_theme=self._code_theme))
            self._console.print(m)

    def on_function_call(self, call, result):
        prefix=f"[none]{self._chat_prefix}[/]"
        line = f"{self._debugger_prompt}{call}".ljust(self._width)
        entry = f"[command]{prefix}{line}[/]\n"
        self._print(entry)
        if result and len(result) > 0:
            result = wrap_long_lines(result, self._width - len(self._chat_prefix))
            result = "\n".join([line.ljust(self._width) for line in result.split("\n")]) + "\n"

            full_response = f"[result]{textwrap.indent(result, prefix, lambda _: True)}[/]"

            # This is just to make the output look a little more like a stream, if
            # streaming is on.  It's tedious with long results, so only animate a 
            # bit.
            # if self._stream:
            #     with Live(vertical_overflow="visible", console=self._console) as live:
            #         lines = ""
            #         result_lines = re.split("(\w)", result)
            #         for chunk in result_lines[0:200]:
            #             lines += chunk
            #             live.update(
            #                 f"[result]{textwrap.indent(lines, prefix)}[/]"
            #             )
            #         live.update(full_response)
            # else:
            self._print(full_response)
