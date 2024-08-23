from python.helpers.input_handler import InputHandler
from python.helpers import timed_input
from ansio import application_keypad, raw_input
from ansio.input import InputEvent, get_input_event
import threading

input_lock = threading.Lock()

class TerminalInputHandler(InputHandler):
    def get_user_input(self, prompt: str, timeout: float = None) -> str:
        if timeout is None:
            return input(prompt).strip()
        else:
            return timed_input.timeout_input(prompt, timeout=timeout)

    def capture_intervention(self) -> bool:
        with input_lock, raw_input, application_keypad:
            event: InputEvent | None = get_input_event(timeout=0.1)
            return event and (event.shortcut.isalpha() or event.shortcut.isspace())

