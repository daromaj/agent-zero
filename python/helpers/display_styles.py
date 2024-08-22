from enum import Enum, auto

class DisplayStyle(Enum):
    USER_INPUT = auto()
    AGENT_START = auto()
    AGENT_RESPONSE = auto()
    TOOL_USE = auto()
    TOOL_RESPONSE = auto()
    TOOL_ARG_KEY = auto()
    TOOL_ARG_VALUE = auto()
    TOOL_RESPONSE_TEXT = auto()
    HINT = auto()
    ERROR = auto()
    WARNING = auto()
    DEFAULT = auto()