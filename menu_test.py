import tkinter as tk
from tkinter import scrolledtext

#%% Define Functions
def do_nothing():
    """Placeholder function for menu items"""
    pass

#%% Define Classes
class ChatWindow(tk.Tk):
    """
    Custom class that builds a GUI interface for Ollama and other self hosted LLMs.
    """
    def __init__(self):
        super().__init__()
        self.title("Simple Chat")
        self.geometry("400x300")
        
        # 1. Create a label widget for the chat window
        self.chat_history = scrolledtext.ScrolledText(self, wrap="word", width=40, height=10)
        self.chat_history.insert(tk.INSERT, 'Hello World!\n\n')
        self.chat_history.pack(side="top", fill='both', expand=True, padx=5, pady=5)
        
        # 2. Create a button to send the message
        self.send_button = tk.Button(self, text="Send")
        self.send_button.pack(side='right', padx=5, pady=5)
        # Add the command to the button
        self.send_button["command"] = self.send_prompt
        
        # 3. Create an entry widget for the user to input their message
        self.user_prompt = tk.Text(self, height=5)
        self.user_prompt.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        # Create the menu bar
        self.create_menu()
    
    # Add the create_menu method
    def create_menu(self):
        """Creates the menu bar and menu items"""
        # Creating the toplevel menu
        menu_bar = tk.Menu(self)
        
        # Creating a sub-menu (tearoff=0 removes the dashed line to detach the menu)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New (TBD)", command=do_nothing)
        file_menu.add_command(label="Open (TBD)", command=do_nothing)
        file_menu.add_command(label="Save (TBD)", command=do_nothing)
        file_menu.add_separator()
        file_menu.add_command(label="Exit (TBD)", command=self.quit)
        menu_bar.add_cascade(label="File (TBD)", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo (TBD)", command=do_nothing)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut (TBD)", command=do_nothing)
        edit_menu.add_command(label="Copy (TBD)", command=do_nothing)
        edit_menu.add_command(label="Paste (TBD)", command=do_nothing)
        menu_bar.add_cascade(label="Edit (TBD)", menu=edit_menu)
        
        # Adding the menu bar to the window
        self.config(menu=menu_bar)

    # Add the missing send_prompt method
    def send_prompt(self):
        """Get the user's message and add it to the chat history"""
        user_message = self.user_prompt.get("1.0", tk.END).strip()
        if user_message:
            self.chat_history.insert(tk.END, f"You: {user_message}\n\n")
            self.user_prompt.delete("1.0", tk.END)  # Clear the input field
#%% Start Program
if __name__ == "__main__":
    chatWindow = ChatWindow()
    chatWindow.mainloop()
