import os
import threading
import time

import models
from agent import Agent, AgentConfig
from python.helpers import files
from python.helpers.display_styles import DisplayStyle
from python.helpers.files import read_file
from python.helpers.input_handler import InputHandler
from python.helpers.print_style import display
from python.helpers.input_handler_factory import InputHandlerFactory

def initialize():
    
    # main chat model used by agents (smarter, more accurate)
    # chat_llm = models.get_openai_chat(model_name="gpt-4o-mini", temperature=0)
    # chat_llm = models.get_ollama_chat(model_name="gemma2:latest", temperature=0)
    # chat_llm = models.get_lmstudio_chat(model_name="TheBloke/Mistral-7B-Instruct-v0.2-GGUF", temperature=0)
    # chat_llm = models.get_openrouter(model_name="meta-llama/llama-3-8b-instruct:free")
    # chat_llm = models.get_azure_openai_chat(deployment_name="gpt-4o-mini", temperature=0)
    # chat_llm = models.get_anthropic_chat(model_name="claude-3-5-sonnet-20240620", temperature=0)
    # chat_llm = models.get_google_chat(model_name="gemini-1.5-flash", temperature=0)
    chat_llm = models.get_groq_chat(model_name="llama-3.1-70b-versatile", temperature=0)
    
    # utility model used for helper functions (cheaper, faster)
    utility_llm = chat_llm # change if you want to use a different utility model

    # embedding model used for memory
    # embedding_llm = models.get_openai_embedding(model_name="text-embedding-3-small")
    embedding_llm = models.get_ollama_embedding(model_name="nomic-embed-text")
    # embedding_llm = models.get_huggingface_embedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # agent configuration
    config = AgentConfig(
        chat_model = chat_llm,
        utility_model = utility_llm,
        embeddings_model = embedding_llm,
        # memory_subdir = "",
        auto_memory_count = 0,
        # auto_memory_skip = 2,
        # rate_limit_seconds = 60,
        # rate_limit_requests = 30,
        # rate_limit_input_tokens = 0,
        # rate_limit_output_tokens = 0,
        # msgs_keep_max = 25,
        # msgs_keep_start = 5,
        # msgs_keep_end = 10,
        # max_tool_response_length = 3000,
        # response_timeout_seconds = 60,
        code_exec_docker_enabled = True,
        # code_exec_docker_name = "agent-zero-exe",
        # code_exec_docker_image = "frdel/agent-zero-exe:latest",
        # code_exec_docker_ports = { "22/tcp": 50022 }
        # code_exec_docker_volumes = { files.get_abs_path("work_dir"): {"bind": "/root", "mode": "rw"} }
        code_exec_ssh_enabled = True,
        # code_exec_ssh_addr = "localhost",
        # code_exec_ssh_port = 50022,
        # code_exec_ssh_user = "root",
        # code_exec_ssh_pass = "toor",
        # additional = {},
    )
    
    input_handler = InputHandlerFactory.create("terminal")  # Or use config value if available
    # create the first agent
    agent0 = Agent(number=0, config=config)

    # Start the key capture thread for user intervention during agent streaming
    threading.Thread(target=check_for_intervention, args=(agent0, input_handler), daemon=True).start()

    # start the chat loop
    chat(agent0, input_handler)


# Main conversation loop
def chat(agent: Agent, input_handler: InputHandler):
    
    # start the conversation loop  
    while True:
        # ask user for message
        timeout = agent.get_data("timeout")
        prompt = "User message ('e' to leave):"

        if timeout:
            prompt = f"User message ({timeout}s timeout, 'w' to wait, 'e' to leave):"

        display.print(prompt, style=DisplayStyle.USER_INPUT)

        user_input = input_handler.get_user_input(timeout)

        if not user_input and timeout:
            user_input = read_file("prompts/fw.msg_timeout.md")
            display.stream(f"{user_input}")
        elif user_input.lower() == 'w' and timeout:
            user_input = input_handler.get_user_input()

        display.print(f"> {user_input}", style=DisplayStyle.DEFAULT, log_only=True) 
                
        # exit the conversation when the user types 'exit'
        if user_input.lower() == 'e': break

        # send message to agent0, 
        assistant_response = agent.message_loop(user_input)
        
        # print agent0 response
        display.print(f"{agent.agent_name}: response:", style=DisplayStyle.AGENT_RESPONSE)        
        display.print(f"{assistant_response}", style=DisplayStyle.DEFAULT)        
                        

# User intervention during agent streaming
def intervention(agent: Agent, input_handler: InputHandler):
    if agent.streaming_agent and not agent.paused:
        agent.paused = True # stop agent streaming
        display.print("User intervention ('e' to leave, empty to continue): ", style=DisplayStyle.USER_INPUT)
        user_input = input_handler.get_user_input()
        display.print(f"> {user_input}", style=DisplayStyle.DEFAULT, log_only=True)        
        
        if user_input.lower() == 'e': os._exit(0) # exit the conversation when the user types 'exit'
        if user_input: agent.streaming_agent.intervention_message = user_input # set intervention message if non-empty
        agent.paused = False # continue agent streaming
    

# Capture keyboard input to trigger user intervention
def check_for_intervention(agent: Agent, input_handler: InputHandler):
        global input_lock
        intervent=False            
        while True:
            if intervent: intervention(agent, input_handler)
            intervent = False
            time.sleep(0.1)
            
            if agent.streaming_agent:
                if input_handler.capture_intervention():
                    intervent=True
                    continue

# User input with timeout

if __name__ == "__main__":
    print("Initializing framework...")

    # Start the chat
    initialize()