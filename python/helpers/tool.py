from abc import abstractmethod

from agent import Agent
from python.helpers import files, messages
from python.helpers.display_styles import DisplayStyle
from python.helpers.print_style import display


class Response:
    def __init__(self, message: str, break_loop: bool) -> None:
        self.message = message
        self.break_loop = break_loop
    
class Tool:

    def __init__(self, agent: Agent, name: str, args: dict[str,str], message: str, **kwargs) -> None:
        self.agent = agent
        self.name = name
        self.args = args
        self.message = message

    @abstractmethod
    def execute(self,**kwargs) -> Response:
        pass

    def before_execution(self, **kwargs):
        if self.agent.handle_intervention(): return # wait for intervention and handle it, if paused
        display.print(f"{self.agent.agent_name}: Using tool '{self.name}':", style=DisplayStyle.TOOL_USE)
        if self.args and isinstance(self.args, dict):
            for key, value in self.args.items():
                display.stream(self.nice_key(key)+": ", style=DisplayStyle.TOOL_ARG_KEY)
                display.stream(value, style=DisplayStyle.TOOL_ARG_VALUE)
                display.print()
                    
    def after_execution(self, response: Response, **kwargs):
        text = messages.truncate_text(response.message.strip(), self.agent.config.max_tool_response_length)
        msg_response = files.read_file("./prompts/fw.tool_response.md", tool_name=self.name, tool_response=text)
        if self.agent.handle_intervention(): return # wait for intervention and handle it, if paused
        self.agent.append_message(msg_response, human=True)
        display.print(f"{self.agent.agent_name}: Response from tool '{self.name}':", style=DisplayStyle.TOOL_RESPONSE)
        display.print(response.message, style=DisplayStyle.TOOL_RESPONSE_TEXT)

    def nice_key(self, key:str):
        words = key.split('_')
        words = [words[0].capitalize()] + [word.lower() for word in words[1:]]
        result = ' '.join(words)
        return result