# src/gui/chat_window.py
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import datetime
import os

#%% Define Classes
class ChatWindow(tk.Tk):
    """
    Custom class that builds a GUI interface for Ollama and other self hosted LLMs.
    """
    def __init__(self):
        super().__init__()
        
        # Initialize filename with current date and time
        current_datetime = datetime.datetime.now()
        self.filename = f"Untitled-{current_datetime.strftime('%Y-%m-%d-%H%M%S')}.md"
        self.title(self.filename)
        
        # Create the main content area
        self.geometry("400x300")
        self.create_widgets()

        # Set Menu bar options
        self.menu_bar_options = [
            ['File',
                ['New', self.new_window],
                ['Open', self.open_file],
                ['Save', self.save_file],
                ['Save As', self.save_as],
                ['---'],  # Separator
                ['Exit', self.destroy]
            ],
            ['Edit',
                ['Undo (TBD)', self.do_nothing],
                ['---'],
                ['Cut (TBD)', self.do_nothing],
                ['Copy (TBD)', self.do_nothing],
                ['Paste (TBD)', self.do_nothing]
            ],
            ['Options',
                ['Settings (TBD)', self.do_nothing]
            ]
        ]

        # Create the menu bar
        self.create_menu()


    # Placeholder function for new features
    @staticmethod
    def do_nothing():
        print("Placeholder Function Activated")
    

    def create_widgets(self):
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


    # Add the create_menu method
    def create_menu(self):
        """Creates the menu bar and menu items from self.menu_bar_options"""
        self.menu_bar = tk.Menu(self)
        
        def add_menu_items(menu, items):
            for item in items:
                if isinstance(item, list):
                    # Submenu or command
                    if len(item) == 2 and callable(item[1]):
                        menu.add_command(label=item[0], command=item[1])
                    elif len(item) > 1 and all(isinstance(sub, list) for sub in item[1:]):
                        # Nested submenu
                        submenu = tk.Menu(menu, tearoff=0)
                        add_menu_items(submenu, item[1:])
                        menu.add_cascade(label=item[0], menu=submenu)
                elif item == '---':
                    menu.add_separator()
        
        for menu_def in self.menu_bar_options:
            menu_label = menu_def[0]
            menu_items = menu_def[1:]
            new_menu = tk.Menu(self.menu_bar, tearoff=0)
            add_menu_items(new_menu, menu_items)
            self.menu_bar.add_cascade(label=menu_label, menu=new_menu)

        self.config(menu=self.menu_bar)


    def exit(self):
        '''Tells the program what to do when `File->Exit` is selected.'''
        self.destroy()
        

    # Add the missing send_prompt method
    def send_prompt(self):
        """Get the user's message and add it to the chat history"""
        user_message = self.user_prompt.get("1.0", tk.END).strip()
        if user_message:
            self.chat_history.insert(tk.END, f"You: {user_message}\n\n")
            self.user_prompt.delete("1.0", tk.END)  # Clear the input field
    
    def new_window(self):
        """Create a new chat window"""
        new_chat = ChatWindow()
        new_chat.mainloop()
    
    def open_file(self):
        """Open a file and load its contents into chat_history"""
        file_path = filedialog.askopenfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            # Update filename and title
            self.filename = file_path
            self.title(os.path.basename(self.filename))
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Clear current chat history
                    self.chat_history.delete("1.0", tk.END)
                    
                    # Read file contents safely as plain text
                    file_content = file.read()
                    
                    # Insert content into chat history
                    self.chat_history.insert(tk.END, file_content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        """Save chat history to the current filename"""
        # If filename is still the default with date/time, prompt for save as
        if self.filename.startswith("Untitled-"):
            self.save_as()
        else:
            try:
                with open(self.filename, 'w', encoding='utf-8') as file:
                    file.write(self.chat_history.get("1.0", tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def save_as(self):
        """Prompt user for filename and save chat history"""
        file_path = filedialog.asksaveasfilename(
            initialfile=self.filename,
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            # Update filename and title
            self.filename = file_path
            self.title(os.path.basename(self.filename))
            
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.chat_history.get("1.0", tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")


#%% Start Program for standalone testing
if __name__ == "__main__":
    chatWindow = ChatWindow()
    chatWindow.mainloop()

