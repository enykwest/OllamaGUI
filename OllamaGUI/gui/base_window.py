# src/gui/base_window.py
'''
Deprecated file. I am keeping it because chat_window.py::ExampleChatWindow uses this
to demonstrate how to import a GUI and modify it.
'''

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import datetime
import os

def do_nothing():
    """Placeholder function for menu items"""
    pass

class BaseWindow(tk.Tk):
    """
    Base window class that provides common functionality for GUI applications:
    - File operations (new, open, save, save as)
    - Basic menu structure
    - Text display area
    - Input mechanism
    """
    def __init__(self):
        super().__init__()
        
        # Initialize filename with current date and time
        current_datetime = datetime.datetime.now()
        self.filename = f"Untitled-{current_datetime.strftime('%Y-%m-%d-%H%M%S')}.md"
        self.title(os.path.basename(self.filename))
        
        self.geometry("400x300")
        
        # Create the main content area
        self.create_widgets()
        
        # Create the menu bar
        self.create_menu()
    
    def create_widgets(self):
        """Create the basic widgets for the window"""
        # 1. Create a text widget for content display
        self.content_area = scrolledtext.ScrolledText(self, wrap="word", width=40, height=10)
        self.content_area.insert(tk.INSERT, 'Hello World!\n\n')
        self.content_area.pack(side="top", fill='both', expand=True, padx=5, pady=5)
        
        # 2. Create a frame for input controls
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(side="bottom", fill='x', padx=5, pady=5)
        
        # 3. Create an entry widget for the user to input text
        self.user_input = tk.Text(self.input_frame, height=5)
        self.user_input.pack(side='left', fill='x', expand=True)
        
        # 4. Create a button to submit
        self.submit_button = tk.Button(self.input_frame, text="Submit", command=self.handle_submit)
        self.submit_button.pack(side='right', padx=5)
    
    def create_menu(self):
        """Creates the menu bar and menu items"""
        # Creating the toplevel menu
        self.menu_bar = tk.Menu(self)
        
        # Creating the File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_window)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.destroy)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Creating the Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Undo", command=do_nothing)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=do_nothing)
        self.edit_menu.add_command(label="Copy", command=do_nothing)
        self.edit_menu.add_command(label="Paste", command=do_nothing)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        
        # Creating the Options menu
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.options_menu.add_command(label="Settings", command=do_nothing)
        self.menu_bar.add_cascade(label="Options", menu=self.options_menu)
        
        # Adding the menu bar to the window
        self.config(menu=self.menu_bar)
    
    def handle_submit(self):
        """Handle the submit button click - to be overridden by subclasses"""
        user_text = self.user_input.get("1.0", tk.END).strip()
        if user_text:
            self.content_area.insert(tk.END, f"Input: {user_text}\n\n")
            self.user_input.delete("1.0", tk.END)  # Clear the input field
    
    def new_window(self):
        """Create a new window - subclasses should override this"""
        new_window = self.__class__()  # Create instance of the same class
        new_window.mainloop()
    
    def open_file(self):
        """Open a file and load its contents"""
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
                    # Clear current content
                    self.content_area.delete("1.0", tk.END)
                    
                    # Read file contents safely as plain text
                    file_content = file.read()
                    
                    # Insert content
                    self.content_area.insert(tk.END, file_content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        """Save content to the current filename"""
        # If filename is still the default with date/time, prompt for save as
        if self.filename.startswith("Untitled-"):
            self.save_as()
        else:
            try:
                with open(self.filename, 'w', encoding='utf-8') as file:
                    file.write(self.content_area.get("1.0", tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def save_as(self):
        """Prompt user for filename and save content"""
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
                    file.write(self.content_area.get("1.0", tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

# For testing as standalone
if __name__ == "__main__":
    app = BaseWindow()
    app.mainloop()
