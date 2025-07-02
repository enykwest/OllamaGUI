# src/gui/chat_window.py
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import datetime
import os
import yaml
# one possible solution for new windows
import subprocess
import sys

#%% Define Classes
class ChatWindow(tk.Tk):
    """
    Custom class that builds a GUI interface for Ollama and other self hosted LLMs.
    """
    #TODO there is a bug where settings don't load properly in new windows
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
        self.menu_bar_options = {
            "File": {
                "Start Server": self.do_nothing,
                "New": self.new_window,
                "Open": self.open_file,
                "Save": self.save_file,
                "Save As": self.save_as,
                "---": None,  # Separator
                "Exit": self.destroy,
            },
            "Options": {
                "Settings": self.open_settings_window,
            },
        }

        # Create the menu bar
        self.create_menu()
        
        # load startup settings
        # settings / presets are saved as yaml files / python dictionaries
        # default settings
        self.settings = {
            "model": "microsoft/DialoGPT-small",
            "server_type": "placeholder",
            "max_new_tokens": 10,
            "prev_chat_context": 2,
        }
        try:
            self.load_settings(self.STARTUP_SETTINGS_FILE)
        except Exception as e:
            print(f"Exception {e} encountered opening startup settings file {self.STARTUP_SETTINGS_FILE}. Using default settings.")
            # use default settings instead



    # Placeholder function for new features
    @staticmethod
    def do_nothing():
        print("Placeholder Function Activated")
        
    @property
    def STARTUP_SETTINGS_FILE(self):
        return "OllamaGUI_StartupSettings.yaml"


    def load_settings(self, filepath):
        with open(filepath, "r") as f:
            loaded = yaml.safe_load(f)
            self.settings.update(loaded)


    def save_settings(self, filepath):
        with open(filepath, "w") as f:
            yaml.dump(self.settings, f)


    def open_settings_window(self):
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.grab_set()

        # Parent frame for horizontal layout
        server_and_tokens_frame = ttk.Frame(settings_win)
        server_and_tokens_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Server Type Frame (left)
        server_frame = ttk.LabelFrame(server_and_tokens_frame, text="Server Type")
        server_frame.pack(side="left", fill="y", expand=True)
        
        server_types = [
            ("Ollama", "ollama"),
            ("Ollama via Podman", "podman"),
            ("Ollama via Docker", "docker"),
            ("Transformers Pipeline", "transformers"),
        ]
        server_var = tk.StringVar(value=self.settings.get("server_type", "podman"))

        for label, value in server_types:
            ttk.Radiobutton(server_frame, text=label, variable=server_var, value=value).pack(anchor="w", padx=5, pady=2)

        
        # Tokens/Context frame (right)
        tokens_frame = ttk.LabelFrame(server_and_tokens_frame, text="Generation Settings")
        tokens_frame.pack(side="left", fill="y", padx=(10,0))
        
        # max_new_tokens
        ttk.Label(tokens_frame, text="max_new_tokens:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        max_new_tokens_var = tk.IntVar(value=self.settings.get("max_new_tokens", 10))
        max_new_tokens_entry = ttk.Entry(tokens_frame, textvariable=max_new_tokens_var, width=10)
        max_new_tokens_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # prev_chat_context
        ttk.Label(tokens_frame, text="prev_chat_context:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        prev_chat_context_var = tk.IntVar(value=self.settings.get("prev_chat_context", 1))
        prev_chat_context_entry = ttk.Entry(tokens_frame, textvariable=prev_chat_context_var, width=10)
        prev_chat_context_entry.grid(row=1, column=1, padx=5, pady=5)


        # LLM Model
        model_frame = ttk.Frame(settings_win)
        model_frame.pack(fill="x", padx=10, pady=(5, 10))
        ttk.Label(model_frame, text="LLM Model:").pack(side="left", padx=(0, 8))
        model_var = tk.StringVar(value=self.settings.get("model", "codellama"))
        model_entry = ttk.Entry(model_frame, textvariable=model_var, width=30)
        model_entry.pack(side="left", fill="x", expand=True)

        ### Buttons
        # Define Button effects
        def load_preset():
            path = filedialog.askopenfilename(
                title="Load Preset",
                filetypes=[("YAML files", "*.yaml;*.yml"), ("All files", "*.*")]
            )
            if path:
                try:
                    self.load_settings(path)
                    server_var.set(self.settings.get("server_type", "podman"))
                    model_var.set(self.settings.get("model", "codellama"))
                    messagebox.showinfo("Preset Loaded", f"Preset loaded from {os.path.basename(path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load preset: {e}")
                    
        def save_preset():
            path = filedialog.asksaveasfilename(
                title="Save Preset",
                defaultextension=".yaml",
                filetypes=[("YAML files", "*.yaml;*.yml"), ("All files", "*.*")]
            )
            if path:
                try:
                    temp_settings = {
                        "server_type": server_var.get(),
                        "model": model_var.get()
                    }
                    with open(path, "w") as f:
                        yaml.dump(temp_settings, f)
                    messagebox.showinfo("Preset Saved", f"Preset saved as {os.path.basename(path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save preset: {e}")
        
        def save_changes():
            self.settings["server_type"] = server_var.get()
            self.settings["model"] = model_var.get()
            self.settings["max_new_tokens"] = max_new_tokens_var.get()
            self.settings["prev_chat_context"] = prev_chat_context_var.get()
            self.save_settings(self.STARTUP_SETTINGS_FILE)
            messagebox.showinfo("Settings Saved", "Settings have been saved.")
            settings_win.destroy()
        
        # Create Buttons
        button_frame = ttk.Frame(settings_win)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        # Button order: "Load Preset", "Save Preset", "Save Changes", "Cancel"
        ttk.Button(button_frame, text="Load Preset", command=load_preset).pack(side="left", padx=(0,5))
        ttk.Button(button_frame, text="Save Preset", command=save_preset).pack(side="left", padx=(0,5))
        ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side="left", padx=(5,0))
        ttk.Button(button_frame, text="Cancel", command=settings_win.destroy).pack(side="left")


    def create_widgets(self):
        # 1. Create a label widget for the chat window
        self.chat_history = scrolledtext.ScrolledText(self, wrap="word", width=40, height=10)
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
        """
        Create a new menu object from self.menu_bar_options and update the window.

        To edit the menu functionality,
        FIRST edit self.menu_bar_options
        (either manually or with the helper functions add_menu_item and remove_menu_item)
        THEN call this function to re-initialize the menus.

        e.g.
        self.menu_bar_options['File']['Start Server'] = self.start_server # edit menu dictionary
        self.create_menu() # re-initilize menu bar
        """
        self.menu_bar = tk.Menu(self)
        for top_menu, submenu_dict in self.menu_bar_options.items():
            menu = tk.Menu(self.menu_bar, tearoff=0)
            self._add_menu_items(menu, submenu_dict)
            self.menu_bar.add_cascade(label=top_menu, menu=menu)
        self.config(menu=self.menu_bar)
        
        
    def _add_menu_items(self, menu, items_dict):
        for label, action in items_dict.items():
            if label == "---":
                menu.add_separator()
            elif callable(action):
                menu.add_command(label=label, command=action)
            elif isinstance(action, dict):
                submenu = tk.Menu(menu, tearoff=0)
                self._add_menu_items(submenu, action)
                menu.add_cascade(label=label, menu=submenu)


    def add_menu_item(self, action, *fullpath):
        """
        Add a menu item at the specified nested path.
        Usage: add_menu_item(action, 'Menu', 'Submenu', ... , 'List Item Label')
        The action is the python function you want to execute when the list item is selected.
        
        e.g. add_menu_item( self.do_nothing, "File", "Settings", "Do Nothing")
        """
        if not fullpath:
            raise ValueError("You must provide at least one menu label.")
        
        submenu = self.menu_bar_options
        for label in fullpath[:-1]:
            submenu = submenu.setdefault(label, {}) # create key if it doesn't exist, else do nothing
        submenu[fullpath[-1]] = action
        
        
    def remove_menu_item(self, *fullpath):
        """
        Remove a menu item at the specified nested path.
        Usage: remove_menu_item('Menu', 'Submenu', ... , 'Item')
        The last element in fullpath is the item's label.
        """
        if not fullpath:
            raise ValueError("You must provide at least one menu label.")
        submenu = self.menu_bar_options
        for label in fullpath[:-1]:
            submenu = submenu.get(label)
            if not isinstance(submenu, dict):
                return  # Path doesn't exist
        submenu.pop(fullpath[-1], None)
        
        
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
    
    # old
    @classmethod
    def new_window(cls):
        """Create a new chat window"""
        #new_chat = ChatWindow()
        new_chat = cls() #.__init__()
        new_chat.mainloop()
    # new
    def new_window(self):
        subprocess.Popen([sys.executable, sys.argv[0]])
    
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

