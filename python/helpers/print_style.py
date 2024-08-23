import html
import os
import sys
from datetime import datetime

import webcolors

from . import files
from .display_interface import DisplayInterface
from .display_styles import DisplayStyle


class PrintStyle(DisplayInterface):
    last_endline = True
    log_file_path = None
    styles = {}

    def __init__(self, bold=False, italic=False, underline=False, font_color="default", background_color="default", padding=False, log_only=False):
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.font_color = font_color
        self.background_color = background_color
        self.padding = padding
        self.padding_added = False  # Flag to track if padding was added
        self.log_only = log_only

        if PrintStyle.log_file_path is None:
            logs_dir = files.get_abs_path("logs")
            os.makedirs(logs_dir, exist_ok=True)
            log_filename = datetime.now().strftime("log_%Y%m%d_%H%M%S.html")
            PrintStyle.log_file_path = os.path.join(logs_dir, log_filename)
            with open(PrintStyle.log_file_path, "w") as f:
                f.write("<html><body style='background-color:black;font-family: Arial, Helvetica, sans-serif;'><pre>\n")        

    @classmethod
    def initialize_styles(cls):
        cls.styles = {
            DisplayStyle.USER_INPUT: {"background_color": "#6C3483", "font_color": "white", "bold": True, "padding": True},
            DisplayStyle.AGENT_START: {"font_color": "#00800", "background_color": "white", "bold": True, "padding": True},
            DisplayStyle.AGENT_RESPONSE: {"font_color": "white", "background_color": "#1D8348", "padding": True},
            DisplayStyle.TOOL_USE: {"font_color": "#1B4F72", "background_color": "white", "bold": True, "padding": True},
            DisplayStyle.TOOL_RESPONSE: {"font_color": "#133193", "padding": True},
            DisplayStyle.TOOL_ARG_KEY: {"font_color": "#85C1E9", "bold": True},
            DisplayStyle.TOOL_ARG_VALUE: {"font_color": "#85C1E9"},
            DisplayStyle.TOOL_RESPONSE_TEXT: {"font_color": "#85C1E9"},
            DisplayStyle.HINT: {"font_color": "#6C3483", "padding": True},
            DisplayStyle.ERROR: {"font_color": "red", "padding": True},
            DisplayStyle.WARNING: {"font_color": "yellow", "padding": True},
            DisplayStyle.DEFAULT: {},
        }

    def apply_style(self, style: DisplayStyle):
        style_dict = self.styles.get(style, {})
        self.bold = style_dict.get("bold", False)
        self.italic = style_dict.get("italic", False)
        self.underline = style_dict.get("underline", False)
        self.font_color = style_dict.get("font_color", "default")
        self.background_color = style_dict.get("background_color", "default")
        self.padding = style_dict.get("padding", False)

    def print(self, *args, sep=' ', style: DisplayStyle = DisplayStyle.DEFAULT, **kwargs):
        self.apply_style(style)
        self.print_styled(*args, sep=sep, **kwargs)

    def stream(self, *args, sep=' ', style: DisplayStyle = DisplayStyle.DEFAULT, **kwargs):
        self.apply_style(style)
        self.stream_styled(*args, sep=sep, **kwargs)

    def hint(self, text: str):
        self.print("Hint: " + text, style=DisplayStyle.HINT)

    def error(self, text: str):
        self.print("Error: " + text, style=DisplayStyle.ERROR)

    def _get_rgb_color_code(self, color, is_background=False):
        try:
            if color.startswith("#") and len(color) == 7:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
            else:
                rgb_color = webcolors.name_to_rgb(color)
                r, g, b = rgb_color.red, rgb_color.green, rgb_color.blue
            
            if is_background:
                return f"\033[48;2;{r};{g};{b}m", f"background-color: rgb({r}, {g}, {b});"
            else:
                return f"\033[38;2;{r};{g};{b}m", f"color: rgb({r}, {g}, {b});"
        except ValueError:
            return "", ""

    def _get_styled_text(self, text):
        start = ""
        end = "\033[0m"  # Reset ANSI code
        if self.bold:
            start += "\033[1m"
        if self.italic:
            start += "\033[3m"
        if self.underline:
            start += "\033[4m"
        font_color_code, _ = self._get_rgb_color_code(self.font_color)
        background_color_code, _ = self._get_rgb_color_code(self.background_color, True)
        start += font_color_code
        start += background_color_code
        return start + text + end

    def _get_html_styled_text(self, text):
        styles = []
        if self.bold:
            styles.append("font-weight: bold;")
        if self.italic:
            styles.append("font-style: italic;")
        if self.underline:
            styles.append("text-decoration: underline;")
        _, font_color_code = self._get_rgb_color_code(self.font_color)
        _, background_color_code = self._get_rgb_color_code(self.background_color, True)
        styles.append(font_color_code)
        styles.append(background_color_code)
        style_attr = " ".join(styles)
        escaped_text = html.escape(text).replace("\n", "<br>")  # Escape HTML special characters
        return f'<span style="{style_attr}">{escaped_text}</span>'

    def _add_padding_if_needed(self):
        if self.padding and not self.padding_added:
            if not self.log_only:
                print()  # Print an empty line for padding
            self._log_html("<br>")
            self.padding_added = True

    def _log_html(self, html):
        with open(PrintStyle.log_file_path, "a", encoding='utf-8') as f: # type: ignore # add encoding='utf-8'
            f.write(html)

    @staticmethod
    def _close_html_log():
        if PrintStyle.log_file_path:
            with open(PrintStyle.log_file_path, "a") as f:
                f.write("</pre></body></html>")            

    def get(self, *args, sep=' ', **kwargs):
        text = sep.join(map(str, args))
        return text, self._get_styled_text(text), self._get_html_styled_text(text)
        
    def print_styled(self, *args, sep=' ', **kwargs):
        self._add_padding_if_needed()
        if not PrintStyle.last_endline: 
            print()
            self._log_html("<br>")
        plain_text, styled_text, html_text = self.get(*args, sep=sep, **kwargs)
        if not self.log_only:
            print(styled_text, end='\n', flush=True)
        self._log_html(html_text+"<br>\n")
        PrintStyle.last_endline = True

    def stream_styled(self, *args, sep=' ', **kwargs):
        self._add_padding_if_needed()
        self.background_color = "default"
        plain_text, styled_text, html_text = self.get(*args, sep=sep, **kwargs)
        if not self.log_only:
            print(styled_text, end='', flush=True)
        self._log_html(html_text)
        PrintStyle.last_endline = False

    def is_last_line_empty(self):
        lines = sys.stdin.readlines()
        return bool(lines) and not lines[-1].strip()

    def initialize(self):
        # Initialize styles and log file
        self.__class__.initialize_styles()
        self._initialize_log_file()

    def close(self):
        self._close_html_log()

    def _initialize_log_file(self):
        if PrintStyle.log_file_path is None:
            logs_dir = files.get_abs_path("logs")
            os.makedirs(logs_dir, exist_ok=True)
            log_filename = datetime.now().strftime("log_%Y%m%d_%H%M%S.html")
            PrintStyle.log_file_path = os.path.join(logs_dir, log_filename)
            with open(PrintStyle.log_file_path, "w") as f:
                f.write("<html><body style='background-color:black;font-family: Arial, Helvetica, sans-serif;'><pre>\n")

# For terminal display
from .print_style import PrintStyle as DisplayImpl

# For web display
# from .web_display import WebDisplay as DisplayImpl

display = DisplayImpl()
display.initialize()