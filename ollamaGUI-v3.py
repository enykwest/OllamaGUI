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
from tkinter import scrolledtext
import subprocess
#import ollamaGUIbackend #TODO write this
"""
maybe change ollamaGUIbackend to ollamaMain?
We can create another GUI class that inherits from this GUI class, but adds the backend methods
"""

#%% Define Classes
class ChatWindow(tk.Tk):
    """
    Custom class that builds a GUI interface for Ollama and other self hosted LLMs.
    """
    def __init__(self):
        super().__init__()
        self.title("Simple Chat")
        self.geometry("400x300")
        
        # Create a label widget for the chat window
        self.chat_history = scrolledtext.ScrolledText(self, wrap="word", width=40, height=10)
        self.chat_history.insert(tk.INSERT, 'Hello World!\n\n')
        self.chat_history.pack(side="top", fill='both', expand=True, padx = 5, pady = 5)
        
        # Create a button to send the message
        self.send_button = tk.Button(self, text="Send")
        self.send_button.pack(side='right', padx = 5, pady = 5)
        # Add the command to the button
        self.send_button["command"] = self.send_prompt
        
        # Create an entry widget for the user to input their message
        self.user_prompt = tk.Text(self, height=5,)
        self.user_prompt.pack(side='left', fill='x', expand=True, padx = 5, pady = 5)

        self.model = "codellama" # or whichever model
        self.server_type = "podman" # or docker
        
        # LLM server related things
        # ensure the widget has updated
        self.update_idletasks()
        # close all servers when Xed out
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Check if LLM service is running and start/fix it if possible
        self.test_LLM_connection()
        
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

chatWindow = ChatWindow()
chatWindow.mainloop()
