# currently, changing settins doesn't change the currently loaded model, you need to create a new window.

from gui.chat_window import ChatWindow as baseGUI
import tkinter as tk
from utils.llm_backend import get_llm_backend

class OllamaGui(baseGUI):
    def __init__(self):
        super().__init__()
        self.llm_backend = get_llm_backend(self.settings)
        self.protocol("WM_DELETE_WINDOW", self.exit)

        connectionStatus, errorMsg = self.llm_backend.test_LLM_connection(fix=True, previousAttempt=None)
        if connectionStatus:
            self.push_to_chat_window(r'Hello World!')
        else:
            self.push_to_chat_window(f'{errorMsg}')

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
        print(prompt)
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.INSERT, "\nUser:\n" + prompt + '\n')
        self.chat_history.yview(tk.END)
        self.chat_history.config(state=tk.DISABLED)
        self.user_prompt.delete('1.0', tk.END)
        self.chat_history.update_idletasks()

        try:
            response = self.llm_backend._send_command(prompt)
        except FileNotFoundError:
            errorMsg = "FileNotFoundError\nAre you sure your prefix is set correctly?\nIs Ollama installed?"
            print(errorMsg)
            self.push_to_chat_window(errorMsg)
            return 1
        except Exception:
            self.llm_backend.test_LLM_connection(fix=True, previousAttempt=None)

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