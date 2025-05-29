import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import datetime
import os
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
    # Inheritance Example
    app = ExampleChatWindow()
    app.mainloop()
