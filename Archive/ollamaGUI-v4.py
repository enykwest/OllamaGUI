# -*- coding: utf-8 -*-
"""
GUI to talk with ollama hosted in docker
TODO: 
    - send chat history to a markdown file
    - seperate into GUI and backend scripts
    - add error handling for docker (errors are only for podman currently)
    - integrate into obsidian?

Notes:
- podman machine init
- podman machine start
- podman (or docker) run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
- podman start ollama
- <run interface>
- podman stop ollama
- podman machine stop


Demo GUI: https://www.pythonguis.com/tutorials/create-ui-with-tkinter-pack-layout-manager/

"""
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import datetime
import os
import subprocess
#import ollamaGUIbackend #TODO write this
"""
maybe change ollamaGUIbackend to ollamaMain?
We can create another GUI class that inherits from this GUI class, but adds the backend methods
"""

# Placeholder function for new features
def do_nothing():
    print("ok, ok, I won't...")


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
        self.chat_history.pack(side="top", fill='both', expand=True, padx = 5, pady = 5)
        
        # 2. Create a button to send the message
        self.send_button = tk.Button(self, text="Send")
        self.send_button.pack(side='right', padx = 5, pady = 5)
        # Add the command to the button
        self.send_button["command"] = self.send_prompt
        
        # 3. Create an entry widget for the user to input their message
        self.user_prompt = tk.Text(self, height=5,)
        self.user_prompt.pack(side='left', fill='x', expand=True, padx = 5, pady = 5)

        # 4. Create the drop-down menu
        self.create_menu()

        
        # Default Settings
        self.model = "codellama" # or whichever model
        self.server_type = "podman" # or docker
        
        # 5. LLM server related things
        # ensure the widget has updated
        self.update_idletasks()
        # close all servers when Xed out
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Check if LLM service is running and start/fix it if possible
        self.test_LLM_connection()


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


    #%% Ollama Related methods/properties
    @property
    def prefix(self):
        prefix = self.server_type + r' exec ollama ollama run ' + self.model
        
        return prefix

        
    def on_close(self):
        print('Stopping Container Service and Closing GUI\n\n')
        self.stop_server()
        self.destroy()

    
    def send_prompt(self):
        """
        This command handles the frontend GUI tasks
        related to sending and receiving prompts.
        
        See _send_command for interacting with the LLM server.
        """
        
        # Get the prompt from the user
        prompt = self.user_prompt.get("1.0" , tk.END)
        print(prompt) # debug
        
        # Send the prompt to the chat window
        self.chat_history.config(state=tk.NORMAL) # enable changing text
        self.chat_history.insert(tk.INSERT, "User:\n" + prompt + '\n') # insert prompt
        self.chat_history.yview(tk.END) # scroll to bottom
        self.chat_history.config(state=tk.DISABLED) # disable changing text
        
        # Clear the entry widget
        self.user_prompt.delete('1.0', tk.END)
        
        # send prompt to LLM
        self.chat_history.update_idletasks()  # ensure the widget has updated before continuing
        response = self._send_command(prompt) #
        #TODO update to streaming & define in backend script
        
        # Send LLM response to chat window
        self.chat_history.config(state=tk.NORMAL) # enable changing text
        self.chat_history.insert(tk.INSERT, response)
        self.chat_history.yview(tk.END) # scroll to bottom
        self.chat_history.config(state=tk.DISABLED) # disable changing text
        
        return 0

        
    # Define backed / interface / debug functions
    #TODO move these to a seperate backend script
    def _send_command(self, prompt, formatResponse=True):
        # Format message
        prefix = self.prefix.split(" ")
        command = prefix + [prompt]
        print(command) # debug
        
        # send prompt and capture response
        response = subprocess.run(command, capture_output=True)
        
        if formatResponse:
            # Handle errors and return answer
            if response.returncode != 0:
                errorMessage = '\nOops! Something went wrong! Error Code: {}\n\n'.format(response.returncode)
                print(errorMessage) # test_LLM_connection() should print additional info
                # see if LLM service is running and fix it if possible
                errorMessage += self.test_LLM_connection()                
                response = errorMessage
            elif formatResponse:        
                # decode byte response
                response = str(response.stdout.decode()) # str is probably overkill, but I suspect safer 
                response = "\nOllama:\n" + response +"\n"
                print(response) #debug
        else:
            pass
            
        return response
       
        
    def test_LLM_connection(self, response=None, fix=True):
        '''
        Test connection to LLM and attempt to fix it.
        '''
        errorMsg = str()#variable to keep cumulative errors

        def cumError(response, preMsg='', postMsg='', fix=fix, printt=True):
            '''
            Helper code to accumulate error messages into one string
            '''
            errorMsg = '' #variable to keep cumulative errors
            
            if response.returncode == 0: # no error, all good
                errorMsg += 'No errors detected\n\n'
            else:
                errorMsg += response.stderr.decode() +'\n\n' 
                if fix:
                    errorMsg += 'Attempting to fix...\n\n'
            
            errorMsg = preMsg +errorMsg +postMsg # concat
            if printt:
                print(errorMsg)
            return errorMsg
        
        
        if response is None:
            response = self._send_command(r"hello", formatResponse=False)
            errorMsg += cumError(response, preMsg='Testing Connection...\n\n')
        else:
            errorMsg += cumError(response)
            
            
        #TODO Errors are only for podman currently
        if response.returncode == 0: # no error, all good
            pass
        elif fix: # if there is an error, try to debug
            stderr = response.stderr.decode()
            #errorMsg += stderr # already done above with cumError
            if r"container state improper" in stderr:
                response = self.start_ollama_container()
                errorMsg += cumError(response, preMsg='Trying to start Ollama container...\n\n')
                
            elif r"unable to connect to Podman socket" in stderr:
                response = self.start_server()
                errorMsg += cumError(response, preMsg='Trying to start container service...\n\n')
                response = self.start_ollama_container()
                errorMsg += cumError(response, preMsg='Trying to start Ollama container...\n\n')
         
            # Trying again
            response = self._send_command(r"hello", formatResponse=False)
            errorMsg += cumError(response, preMsg='Testing LLM again...\n\n')
        
        return errorMsg
            
        
    def start_server(self):
        if self.server_type == 'podman':
            command = r'podman machine start'
        elif self.server_type == 'docker':
            pass #command = r'docker start' # TODO
        
        return subprocess.run(command, capture_output=True)
    
    
    def stop_server(self):
        if self.server_type == 'podman':
            command = r'podman machine stop'
        elif self.server_type == 'docker':
            pass #command = r'docker start' # TODO
        
        return subprocess.run(command, capture_output=True)

    
    def start_ollama_container(self):
        command = self.server_type + r' start ollama'
        
        return subprocess.run(command, capture_output=True)

    
    def stop_ollama_container(self):
        command = self.server_type + r' stop ollama'
        
        return subprocess.run(command, capture_output=True)
        
            
#%% Start Program
if __name__ == "__main__":
    chatWindow = ChatWindow()    
    chatWindow.mainloop()
