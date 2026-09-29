'''
ToDo: make it work, make it right, make it fast
- Now that we have a deticated module for chat history (conversation_handler.py) we should re-implement saving and loading conversations.
- Integrate crewai
  - multi-step reasoning / role based reasoning and automated tool use
- Implement attaching files or RAG folders.
  - Defered in favor of crewai as that may affect how we do things
- build settings window from backend?
    - Add torch_dtype to settings menu for transformers pipeline (e.g. float32, 16, 8 or 4)
    - Allow quantized models with bitsandbytes.

Bugs:
- "Send on Enter" is saved to startup settings, but doesn't activate send on enter on new start.
- Changing settings doesn't change the currently loaded model, you need to create a new window or restart.
    - Work around: Server is no longer started when window starts. Added "Start Server" command to File menu.
    - #bug/low_priority/mem_leak if two GUIs are open, closing one doesn't unload the model from GPU when using transformers pipeline, memory is cleared when all windows are closed.
        - This issues was exacerbated by Spyder. The window started by Spyder doesn't unload memory until Spyder is closed, but new windows DO clear their memory when closed.
        - Starting a server twice from the same window doubles memory usage, but doesn't release previous allocation until closed.
        - Simple work around, close previous window before starting new server. If you accidently double start a server, close the window.
- use accelerate to split large models between gpu and cpu
    - validated using Phi-4-Mini-Instruct and Llama-3.2-3B-Instruct on limited memory device.
    - #bug/low_priority/incompatible_model microsoft/DialoGPT-small seems to work,
      but google/gemma-3-1b-it only runs on CPU currently as the GPU version requires trition
      and triton is only availible on linux. This is an odd bug where the backend "loads properly" but fails during runtime.
- #bug/low_priority/incompatible_model , Gemma3 throws a *** jinja2.exceptions.TemplateError if the history STARTS with an assistant message
    - (Conversation roles must alternate user/assistant/user/assistant/...) , hotfix applied in llm_backend.manage_chat_history,
    but I am not sure how this will interact with RAG.
    My assumption is we have to reveal the tools in the system prompt with some one shot examples, then answer the assistant as the "user". Crewai may help handle this for us.
'''
from gui.chat_window import ChatWindow as baseGUI
import tkinter as tk
from utils.llm_backend import get_llm_backend
from utils.llm_backend import LLMConnectionError
from utils.llm_backend import PlaceholderLLM

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


    def process_prompt(self, prompt):
        '''Send a prompt to the LLM model and Return the model name and response.'''
        # TODO implement history context
        # TODO ensure system prompt is always in prompt if not empty
        return (self.llm_backend.model , self.llm_backend.call(self.chat_history.history) )


def main():
    app = OllamaGui()
    app.mainloop()


if __name__ == "__main__":
    main()