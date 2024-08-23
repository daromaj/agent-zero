from python.helpers.input_handler import InputHandler
from python.helpers.terminal_input_handler import TerminalInputHandler

class InputHandlerFactory:
    @staticmethod
    def create(handler_type: str) -> InputHandler:
        if handler_type.lower() == "terminal":
            return TerminalInputHandler()
        # Add other handler types here as needed
        else:
            raise ValueError(f"Unknown input handler type: {handler_type}")