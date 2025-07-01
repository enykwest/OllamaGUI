'''
Bugs / ToDo: make it work, make it right, make it fast
- Currently, changing settings doesn't change the currently loaded model, you need to create a new window or restart.
- use accelerate to split large models between gpu and cpu
    - debuging now
    - microsoft/DialoGPT-small seems to work, but google/gemma-3-1b-it only runs on CPU currently as the GPU version requires trition
        and triton is only availible on linux. This is an odd bug where the backend "loads properly" but fails during runtime.
- build settings window from backend?
- probably need to implement "nograd" or "eval" somewhere
'''
from gui.chat_window import ChatWindow as baseGUI
import tkinter as tk
from utils.llm_backend import get_llm_backend
from utils.llm_backend import LLMConnectionError
from utils.llm_backend import PlaceholderLLM

class OllamaGui(baseGUI):
    def __init__(self):
        super().__init__()
        try:
            self.llm_backend = get_llm_backend(self.settings)
            self.protocol("WM_DELETE_WINDOW", self.exit)
    
            connectionStatus, errorMsg = self.llm_backend.test_LLM_connection(fix=True, previousAttempt=None)
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

    def push_to_chat_window(self, text):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.INSERT, "\nANNOUNCMENT:\n" + text + '\n')
        self.chat_history.yview(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def send_prompt(self):
        prompt = self.user_prompt.get("1.0", tk.END)
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.INSERT, "\nUser:\n" + prompt + '\n')
        self.chat_history.yview(tk.END)
        self.chat_history.config(state=tk.DISABLED)
        self.user_prompt.delete('1.0', tk.END)
        self.chat_history.update_idletasks()

        response = self.llm_backend._send_command(prompt)

        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.INSERT, response)
        self.chat_history.yview(tk.END)
        self.chat_history.config(state=tk.DISABLED)
        return 0

def main():
    app = OllamaGui()
    app.mainloop()

if __name__ == "__main__":
    main()