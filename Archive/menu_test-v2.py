import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import datetime
import os

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
        
        # Initialize filename with current date and time
        current_datetime = datetime.datetime.now()
        self.filename = f"Untitled-{current_datetime.strftime('%Y-%m-%d-%H%M%S')}.md"
        self.title(self.filename)
        
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
        
        # Creating the File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_window)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Creating the Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo (TBD)", command=do_nothing)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut (TBD)", command=do_nothing)
        edit_menu.add_command(label="Copy (TBD)", command=do_nothing)
        edit_menu.add_command(label="Paste (TBD)", command=do_nothing)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Creating the Options menu
        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(label="Context", command=do_nothing)
        menu_bar.add_cascade(label="Options", menu=options_menu)
        
        # Adding the menu bar to the window
        self.config(menu=menu_bar)

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
#%% Start Program
if __name__ == "__main__":
    chatWindow = ChatWindow()
    chatWindow.mainloop()
