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

    # Placeholder function for new features
    @staticmethod
    def do_nothing():
        print("Placeholder Function Activated")
    
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
        #file_menu.add_command(label="Exit", command=self.destroy) # Default behavior
        file_menu.add_command(label="Exit", command=self.exit)
        # Uncomment to redirect the "X" button from self.destroy to self.exit
        #self.protocol("WM_DELETE_WINDOW", self.exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Creating the Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo (TBD)", command=self.do_nothing)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut (TBD)", command=self.do_nothing)
        edit_menu.add_command(label="Copy (TBD)", command=self.do_nothing)
        edit_menu.add_command(label="Paste (TBD)", command=self.do_nothing)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Creating the Options menu
        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(label="Context", command=self.do_nothing)
        menu_bar.add_cascade(label="Options", menu=options_menu)
        
        # Adding the menu bar to the window
        self.config(menu=menu_bar)


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


# the "." is require if used as a module but breaks thing if tested alone.
if __name__ == "__main__":
    from base_window import BaseWindow
else:
    from .base_window import BaseWindow
class ExampleChatWindow(BaseWindow):
    """
    An example window for chat applications demonstrating that class inheritance
    from another file (base_window.py::BaseWindow) and how to add chat-specific functionality.
    """
    def __init__(self):
        super().__init__()
        self.title("Example Chat Application")
        
        # Customize the window for chat purposes
        self.customize_interface()
        
        # Add chat-specific menu items
        self.add_chat_menu_items()
    
    def customize_interface(self):
        """Customize the interface for chat functionality"""
        # Change labels and text
        self.content_area.delete("1.0", tk.END)
        self.content_area.insert(tk.END, "Chat History:\n\n")
        
        # Rename the submit button
        self.submit_button.config(text="Send")
    
    def add_chat_menu_items(self):
        """Add chat-specific menu items"""
        # Add a Chat menu to the menu bar
        self.chat_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.chat_menu.add_command(label="Clear Chat", command=self.clear_chat)
        self.chat_menu.add_command(label="Export Chat", command=self.export_chat)
        self.chat_menu.add_separator()
        self.chat_menu.add_command(label="Settings", command=self.show_settings)
        
        # Insert the Chat menu between File and Edit
        self.menu_bar.insert_cascade(1, label="Chat", menu=self.chat_menu)
        
        # Add additional items to the File menu
        self.file_menu.insert_command(2, label="Import Chat", command=self.import_chat)
        
        # Add additional items to the Options menu
        self.options_menu.add_command(label="Chat Preferences", command=self.show_chat_preferences)
    
    def handle_submit(self):
        """Override the submit handler for chat functionality"""
        message = self.user_input.get("1.0", tk.END).strip()
        if message:
            # Format as a chat message
            self.content_area.insert(tk.END, f"You: {message}\n\n")
            self.user_input.delete("1.0", tk.END)  # Clear the input field
            
            # Here you would typically process the message and add bot response
            self.simulate_response(message)
    
    def simulate_response(self, message):
        """Simulate a chat response (placeholder for actual chat logic)"""
        # In a real chat app, you would process the message and get a response
        self.content_area.insert(tk.END, f"Bot: I received your message: \"{message}\"\n\n")
    
    def clear_chat(self):
        """Clear the chat history"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.content_area.delete("1.0", tk.END)
            self.content_area.insert(tk.END, "Chat History:\n\n")
    
    def export_chat(self):
        """Export chat history to a file"""
        # Reuse the save_as method but with a different title
        self.save_as()
    
    def import_chat(self):
        """Import chat from a file"""
        # Similar to open_file but with chat-specific processing
        self.open_file()
    
    def show_settings(self):
        """Show chat settings dialog"""
        messagebox.showinfo("Settings", "Chat settings dialog would appear here.")
    
    def show_chat_preferences(self):
        """Show chat preferences dialog"""
        messagebox.showinfo("Chat Preferences", "Chat preferences dialog would appear here.")


#%% Start Program for standalone testing
if __name__ == "__main__":
    chatWindow = ChatWindow()
    chatWindow.mainloop()

    # Inheritance Example
    app = ExampleChatWindow()
    app.mainloop()
