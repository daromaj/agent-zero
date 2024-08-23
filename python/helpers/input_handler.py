from abc import ABC, abstractmethod

class InputHandler(ABC):
    @abstractmethod
    def get_user_input(self, prompt: str = "> ", timeout: float = None) -> str:
        pass

    @abstractmethod
    def capture_intervention(self) -> bool:
        pass