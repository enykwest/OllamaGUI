# src/gui/chat_window.py
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import datetime
import os
import yaml

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
        try:
            self.load_settings(self.STARTUP_SETTINGS_FILE)
        except Exception as e:
            print(f"Exception {e} encountered opening startup settings file {self.STARTUP_SETTINGS_FILE}. Using default settings.")
            # use default settings instead
            self.settings = {
                "model": "codellama",
                "server_type": "podman"
            }
            
        return


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
            self.settings = loaded


    def save_settings(self, filepath):
        with open(filepath, "w") as f:
            yaml.dump(self.settings, f)


    def open_settings_window(self):
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.grab_set()

        # Server Type
        server_frame = ttk.LabelFrame(settings_win, text="Server Type")
        server_frame.pack(fill="x", padx=10, pady=(10, 5))

        server_types = [
            ("Ollama", "ollama"),
            ("Ollama via Podman", "podman"),
            ("Ollama via Docker", "docker"),
            ("Transformers Pipeline", "transformers"),
        ]
        server_var = tk.StringVar(value=self.settings.get("server_type", "podman"))

        for label, value in server_types:
            ttk.Radiobutton(server_frame, text=label, variable=server_var, value=value).pack(anchor="w", padx=5, pady=2)

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
        Usage: add_menu_item(action, 'Menu', 'Submenu', ... , 'Item')
        The last element in fullpath is the item's label.
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

