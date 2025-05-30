'''
A GUI interface for Ollama and other self hosted LLMs.
Originally written March 28, 2025 by Erik Nykwest
Copyright (c) 2025, MIT License
'''

# src/main.py
from gui.chat_window import ChatWindow as baseGUI
import tkinter as tk #Debug, this code should be moved to utils

# Add Backend to ChatWindow
import subprocess

### Define Errors
class LLMConnectionError(Exception):
    pass


### Define Classes
class OllamaGui(baseGUI):
    """
    Custom class that builds a GUI interface for Ollama and other self hosted LLMs.
    """
    def __init__(self):
        super().__init__()
        
        # Set Default Settings
        self.model = "codellama" # or whichever model
        self.server_type = "podman" # or docker
        
        # LLM server related things
        self.update_idletasks() # ensure the widget has updated
        # uncomment to close all servers when Xed out
        #self.protocol("WM_DELETE_WINDOW", self.exit)

        # Check if LLM service is running and start/fix it if possible
        connectionStatus , errorMsg = self.test_LLM_connection(fix=True, previousAttempt=None)
        if connectionStatus:
            self.push_to_chat_window(r'Hello World!')
        else:
            self.push_to_chat_window(f'{errorMsg}')


    #%% Ollama Related methods/properties
    @property
    def prefix(self):
        prefix = self.server_type + r' exec ollama ollama run ' + self.model
        
        return prefix

        
    def exit(self):
        '''Tells the program to close all servers when Xed out'''
        #TODO We should only close the server if ALL windows are closed
        # Perhaps we keep track of the number of open windows with a class variable?
        print('Stopping Container Service and Closing GUI\n\n')
        self.stop_server()
        self.destroy()

    def push_to_chat_window(self, text):
        # Send the text to the chat window
        self.chat_history.config(state=tk.NORMAL) # enable changing text
        self.chat_history.insert(tk.INSERT, "\nANNOUNCMENT:\n" + text + '\n') # insert text
        self.chat_history.yview(tk.END) # scroll to bottom
        self.chat_history.config(state=tk.DISABLED) # disable changing text

    # I feel like this should be folded into the baseGUI somehow
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
        self.chat_history.insert(tk.INSERT, "\nUser:\n" + prompt + '\n') # insert prompt
        self.chat_history.yview(tk.END) # scroll to bottom
        self.chat_history.config(state=tk.DISABLED) # disable changing text
        
        # Clear the entry widget
        self.user_prompt.delete('1.0', tk.END)
        
        # ensure the widget has updated before continuing
        self.chat_history.update_idletasks()  
        
        # send prompt to LLM
        try:
            response = self._send_command(prompt)
        except FileNotFoundError:
            errorMsg = "FileNotFoundError\nAre you sure your prefix is set correctly?\nIs Ollama installed?"
            print(errorMsg)
            self.push_to_chat_window(errorMsg)
            return 1
        except LLMConnectionError:
            self.test_LLM_connection(fix=True, previousAttempt=response)
        
        # Send LLM response to chat window
        self.chat_history.config(state=tk.NORMAL) # enable changing text
        self.chat_history.insert(tk.INSERT, response)
        self.chat_history.yview(tk.END) # scroll to bottom
        self.chat_history.config(state=tk.DISABLED) # disable changing text
        
        return 0


    #%% Define backed / interface / debug functions
    #TODO move these to a seperate backend script
    def _send_command(self, prompt, formatResponse=True):
        '''
        Send a command to the LLM. 

        Parameters
        ----------
        prompt : str
            Raw user input. Often a question or request to the LLM.
        formatResponse : bool, optional
            subprocess.run() returns a CompletedProcess object. If formatResponse
            is set to False, this function returns the raw CompletedProcess.
            Otherwise, a plain text response extracted, formated, and returned.
            The default is True.

        Returns
        -------
        response : str or subprocess.run CompletedProcess object
            subprocess.run() returns a CompletedProcess object. If formatResponse
            is set to False, this function returns the raw CompletedProcess.
            Otherwise, a plain text response extracted, formated, and returned.

        '''
        # Format message
        prefix = self.prefix.split(" ")
        command = prefix + [prompt]
        print(command) # debug
        
        # send prompt and capture response
        response = subprocess.run(command, capture_output=True)

        # Check for errors and return response
        if response.returncode != 0: # if there was an error
            raise LLMConnectionError
            #errorMessage = '\nOops! Something went wrong! Error Code: {}\n\n'.format(response.returncode)
            # We could also decode the stderr, but that should already be printed for us
            #print(errorMessage)
            # see if LLM service is running and fix it if possible
            #errorCode, errorMsg = self.test_LLM_connection(response) # DANGER! Possible recursion!        
            #response = errorMessage
        elif formatResponse:        
            # decode byte response
            response = str(response.stdout.decode()) # str is probably overkill, but I suspect safer 
            response = "\nOllama:\n" + response +"\n"
            print(response) #debug
        else:
            pass


        return response

    
    def test_LLM_connection(self, fix, previousAttempt):
        '''
        Test connection to LLM and attempt to fix it.
        
        connectionStatus = True # success , connected to LLM
        connectionStatus = False # failure, NOT connected to LLM, default return
        '''
        connectionStatus = False # default return, failed connection
        errorMsg = ""
        
        try:
            if previousAttempt is None:
                response = self._send_command(r"hello", formatResponse=False)
            else:
                response = previousAttempt
                
            #TODO Errors are only for podman currently
            if response.returncode == 0: # no error, all good
                connectionStatus = True # success
                
            elif fix: # if there is an error, try to debug
                stderr = response.stderr.decode()
                print(stderr)
                if r"container state improper" in stderr:
                    print('Trying to start Ollama container...\n\n')
                    response = self.start_ollama_container()
                    stderr = response.stderr.decode()
                    print(stderr)
                
                if r"unable to connect to Podman socket" in stderr:
                    print('Trying to start container service...\n\n')
                    response = self.start_server()
                    stderr = response.stderr.decode()
                    print(stderr)
                    
                    print('Trying to start Ollama container...\n\n')
                    response = self.start_ollama_container()
                    stderr = response.stderr.decode()
                    print(stderr)
             
                # Trying again
                print('Testing LLM again...\n\n')
                response = self._send_command(r"hello", formatResponse=False)
                stderr = response.stderr.decode()
                
                
                if response.returncode == 0: # no error, all good
                    connectionStatus = True # success
                else:
                    print(stderr)
                    errorMsg = stderr
                    
        
        except FileNotFoundError:
            # One way to generate this error is to try and run the script
            # on a computer that doesn't have ollama/docker/podman
            # ...ask me how I know...
            errorMsg = "FileNotFoundError\nAre you sure your prefix is set correctly?\nIs Ollama installed?"
            print(errorMsg)
            #connectionStatus = False # default
        
        return ( connectionStatus , errorMsg )
    
    


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
def main():
    """Main entry point for the application"""
    app = OllamaGui()
    app.mainloop()

if __name__ == "__main__":
    main()
