from abc import ABC, abstractmethod

from .display_styles import DisplayStyle


class DisplayInterface(ABC):
    @abstractmethod
    def initialize(self):
        """Initialize the display."""
        pass

    @abstractmethod
    def print(self, *args, sep=' ', style: DisplayStyle = DisplayStyle.DEFAULT, **kwargs):
        """Print text with styling."""
        pass

    @abstractmethod
    def stream(self, *args, sep=' ', style: DisplayStyle = DisplayStyle.DEFAULT, **kwargs):
        """Stream text with styling."""
        pass

    @abstractmethod
    def hint(self, text: str):
        """Display a hint."""
        pass

    @abstractmethod
    def error(self, text: str):
        """Display an error."""
        pass

    @abstractmethod
    def close(self):
        """Close the display and perform any necessary cleanup."""
        pass