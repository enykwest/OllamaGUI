'''
Changes:
- Bug fix: Something was going wrong with our primary Agent when we set the system prompt via settings. This was fixed by updating save_sys_prompt in chat_window.py to match the current version of conversation_handler.py
- Bug Fix: the "Send on Enter" checkbox would load properly, but the internal setting was incorrect
- Bug Fix: When we switched to crewai llm backend max_new_tokens was is ignored. I think I fixed this but it needs some more testing.
- Deleted bug list items associated with google's Gemma3. Fixing them is outside of the scope of this app.

ToDo: make it work, make it right, make it fast
- Implentment tests to the easy installers
- Add the advice to avoid memory leaks when using pytorch to documentation, then delete from bug list.
- We currently pass the full settings dictionary to the llm_backend crewai LLM class. Our internal settings will inevitably collide with crewai's the future so we should re-factor our settings dictionary to have scopes such as settings.gui and setting.llm or something.
- Implement the full suite of "Openai" query options (or at least setup the basics)
  - Add `max_new_tokens` - done, handled by passing settings to crewai LLM class in llm_backend
- #feature/high_priority/tools , try adding some of the built-in crewai tools to the request, then work on a custom tool.
- #UX/low_priority/settings , add an "OK" button for temporary changes to settings.
- #feature/low_priority/save_chat , Now that we have a deticated module for chat history (conversation_handler.py) we should re-work saving and loading conversations. Right now we just dump text histories of the chat.
- #feature/low_priority/endpoints , Setup Generic OpenAI-compatible Endpoint via crewai LLM class
  - https://docs.crewai.com/v1.15.22/en/learn/llm-connections#connecting-to-openai-compatible-llms
  - Add API Key to settings GUI
  - Add base_url to settings GUI
- #feature/med_priority/RAG , Implement attaching files or RAG folders.
  - Defered in favor of crewai as that may affect how we do things
- #UX/low_priority/GUI , Build settings window from backend?
    - Add torch_dtype to settings menu for transformers pipeline (e.g. float32, 16, 8 or 4)
    - Allow quantized models with bitsandbytes.
- #UX/low_priority/model_prefixes , Warn user (or better yet auto-fix) about model prefixes (e.g. ollama/ of openai/ or microsoft/).
  - I may want to seperate Ollama and cloud LLMs again in the backend as there are some errors we might be able to auto-handle, like requesting a model you haven't downloaded yet.

Bugs:
- #UX/low_priority/lag , The window freezes on sending the prompt as it waits for the response. We should try an asyncronous "send" that lets the user still adjust the GUI, but ignores additional send commands.
- Changing settings doesn't change the currently loaded model, you need to create a new window or restart.
    - Work around: Server is no longer started when window starts. Added "Start Server" command to File menu.
    - #bug/low_priority/mem_leak if two GUIs are open, closing one doesn't unload the model from GPU when using transformers pipeline, memory is cleared when all windows are closed.
        - This issues was exacerbated by Spyder. The window started by Spyder doesn't unload memory until Spyder is closed, but new windows DO clear their memory when closed.
        - Starting a server twice from the same window doubles memory usage, but doesn't release previous allocation until closed.
        - Simple work around, close previous window before starting new server. If you accidently double start a server, close the window.
        - New window should also receive the old LLM object in case we want two seperate chats with the same backend
'''

# Disable crewai telemetry
# Set environment flags BEFORE importing crewai
import os
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

from gui.chat_window import ChatWindow as baseGUI
import tkinter as tk
from utils.llm_backend import get_llm_backend
from utils.llm_backend import LLMConnectionError
from utils.llm_backend import PlaceholderLLM
#from crewai import Agent
from utils.CustomAgent import CustomAgent as Agent # Debugging
import copy

class OllamaGui(baseGUI):
    def __init__(self):
        super().__init__()

        # edit menu bar
        self.menu_bar_options['File']['Start Server'] = self.start_server
        self.create_menu() # re-initilize menu bar
        self.llm_backend = PlaceholderLLM(model="PlaceholderLLM")

    def start_server(self,fix=True):
        try:
            self.llm_backend = get_llm_backend(self.settings)
            self.protocol("WM_DELETE_WINDOW", self.exit)
    
            connectionStatus, errorMsg = self.llm_backend.test_LLM_connection(fix=fix, previousAttempt=None)
            if connectionStatus:
                # Push system prompt to chat history
                self.chat_history.add_message(
                  {
                  'role'   : 'system' ,
                  'content' :  self.settings['sys_prompt'] ,
                  }
                )

                # Announce that LLM is ready to use
                self.push_to_chat_window(r'Hello World!')
            else:
                self.push_to_chat_window(f'{errorMsg}')

        except LLMConnectionError:
            self.llm_backend = PlaceholderLLM()
            self.push_to_chat_window('LLMConnectionError \n loading placeholder LLM \n Are your settings correct?')


    def exit(self):
        try:
            self.llm_backend.exit()
            
        except AttributeError:
            pass # llm_backend.exit not defined 
        except Exception as e:
            print(f"Closing backend failed with: {e}") # without the try-except the GUI may refuse to close
        print('Closing GUI\n\n')
        self.destroy()


    def process_prompt(self, prompt: str) -> (str, str):
        '''
        Send a prompt to the LLM model and Return the model name and response.
        
        Currently we are using crewai's Agent class, which templates the prompt for you.
        Messages are formated like so:
        [{'role': 'system', 'content': 'You are <agent role>. <agent backstory>.\nYour personal goal is: <agent goal>', 'cache_breakpoint': True},
         {'role': 'user', 'content': "\nCurrent Task: " + <task description> + "\n\nThis is the expected criteria for your final answer: " + <task expected_outcome> + "\nyou MUST return the actual complete content as the final answer, not a summary.\n\nThis is the context you're working with:\n" + <task context> + "\n\nProvide your complete response:", 'cache_breakpoint': True}]

        Technically that is the output for a Crew, not an Agents, but you get the idea.

        '''
        # As of 10/1/2026 (crewai-1.15.23) the system_template flag does not work as intended,
        # Instead of sending as "system" (like the default template) it puts the system prompt into the user prompt
        # Since we capture the users input in our own chat history before it get mangled,
        # we will simply add "system" and "user" labels to the template.
        # Reference: https://docs.crewai.com/v1.15.23/en/guides/advanced/customizing-prompts#understanding-crewais-prompt-system
        agent = Agent(
            llm=self.llm_backend ,
            # role, backstory, and goal are required inputs
            role=      '' ,
            backstory= '' ,
            goal=      '' , 

            use_system_prompt= True, # this flag should seperate system and user prompts, but is totally ignored
            system_template = r'{role}' ,
            prompt_template= r'{input}' , 
            #context="None" , # TBD if chat templates get fixed.
            tools=[] , #TBD
            verbose=False ,
            share_crew=False , # Disable telemetry. I think this only applies to crews, but crewai didn't complain.
            )

        # Grab the N most recent messages plus our new message
        messages = self.chat_history.get_context(self.settings['prev_chat_context'] + 1)
        
        #bugfix for crewai Agent system_template not working, manually insert system prompt
        messages = copy.copy(messages)
        messages.insert(-1, {'role':'system', 'content': self.settings['sys_prompt']} )
        print('Debug :' , messages)

        response = str(agent.kickoff(messages) ) # returns a "crewai.lite_agent_output" so convert to string
        
        return (self.llm_backend.model , response ) # return model name and response to add to chat history.


def main():
    app = OllamaGui()
    app.mainloop()


if __name__ == "__main__":
    main()