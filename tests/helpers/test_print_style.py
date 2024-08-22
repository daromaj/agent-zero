import re
import sys
import unittest
from io import StringIO

from python.helpers.print_style import PrintStyle, DisplayStyle


class TestPrintStyle(unittest.TestCase):
    def setUp(self):
        self.print_style = PrintStyle()
        self.held_output = StringIO()
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_print_styles(self):
        for style in DisplayStyle:
            self.print_style.print(f"Testing {style.name}", style=style)
        
        output = self.held_output.getvalue()
        self.assertIn("Testing USER_INPUT", output)
        self.assertIn("Testing AGENT_START", output)
        self.assertIn("Testing AGENT_RESPONSE", output)
        self.assertIn("Testing TOOL_USE", output)
        self.assertIn("Testing TOOL_RESPONSE", output)
        self.assertIn("Testing HINT", output)
        self.assertIn("Testing ERROR", output)
        self.assertIn("Testing WARNING", output)
        self.assertIn("Testing DEFAULT", output)

    def test_stream(self):
        self.print_style.stream("Streaming ", style=DisplayStyle.AGENT_RESPONSE)
        self.print_style.stream("text", style=DisplayStyle.AGENT_RESPONSE)
        
        output = self.held_output.getvalue()
        # Remove ANSI escape codes before asserting
        cleaned_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        self.assertIn("Streaming text", cleaned_output)

    def test_hint(self):
        self.print_style.hint("This is a hint")
        
        output = self.held_output.getvalue()
        self.assertIn("Hint: This is a hint", output)

    def test_error(self):
        self.print_style.error("This is an error")
        
        output = self.held_output.getvalue()
        self.assertIn("Error: This is an error", output)

    def test_custom_style(self):
        custom_style = PrintStyle(bold=True, italic=True, underline=True, 
                                  font_color="red", background_color="yellow")
        custom_style.print("Custom styled text")
        
        output = self.held_output.getvalue()
        self.assertIn("Custom styled text", output)

    def test_log_file_creation(self):
        self.assertIsNotNone(PrintStyle.log_file_path)
        self.assertTrue(PrintStyle.log_file_path.endswith(".html"))

if __name__ == '__main__':
    unittest.main()