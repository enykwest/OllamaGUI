# src/main.py
from gui.chat_window import ChatWindow as baseGUI
import tkinter as tk #Debug, this code should be moved to utils


# Add Backend to ChatWindow
import subprocess

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
        connectionStatus , errorMsg = self.test_LLM_connection(fix=True)
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


    #%% Define backed / interface / debug functions
    #TODO move these to a seperate backend script
    def _send_command(self, prompt, formatResponse=True):
        # Format message
        prefix = self.prefix.split(" ")
        command = prefix + [prompt]
        print(command) # debug
        
        # send prompt and capture response
        response = subprocess.run(command, capture_output=True)

        # Handle errors and return answer
        if response.returncode != 0:
            errorMessage = '\nOops! Something went wrong! Error Code: {}\n\n'.format(response.returncode)
            print(errorMessage) # test_LLM_connection() should print additional info
            # see if LLM service is running and fix it if possible
            #errorMessage += self.test_LLM_connection()  # RECURSION BUG!               
            response = errorMessage
        elif formatResponse:        
            # decode byte response
            response = str(response.stdout.decode()) # str is probably overkill, but I suspect safer 
            response = "\nOllama:\n" + response +"\n"
            print(response) #debug
        else:
            pass
 
        return response


    # old version 1, bad form, recursion issues
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
        
        try:
        
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
        
        except FileNotFoundError:
            # One way to generate this error is to try and run the script
            # on a computer that doesn't have ollama/docker/podman
            # ...ask me how I know...
            errorMsg = "FileNotFoundError . Are you sure your prefix is set correctly? Is Ollama installed?"

        
        return errorMsg
    
    
    
    def test_LLM_connection(self, fix):
        '''
        Test connection to LLM and attempt to fix it.
        
        connectionStatus = True # success , connected to LLM
        connectionStatus = False # failure, NOT connected to LLM, default return
        
        '''
        connectionStatus = False # default return, failed connection
        errorMsg = ""
        
        try:
            response = self._send_command(r"hello", formatResponse=False)
                
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
                print(stderr)
                
                if response.returncode == 0: # no error, all good
                    connectionStatus = True # success
        
        except FileNotFoundError:
            # One way to generate this error is to try and run the script
            # on a computer that doesn't have ollama/docker/podman
            # ...ask me how I know...
            errorMsg = "FileNotFoundError . Are you sure your prefix is set correctly? Is Ollama installed?"
            print(errorMsg)
            #connectionStatus = False # default connectionStatus is False
        
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
