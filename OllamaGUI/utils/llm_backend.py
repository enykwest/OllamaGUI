import subprocess
from warnings import warn


class LLMConnectionError(Exception):
    pass

# needs more work
def get_llm_backend(settings):
    try:
        server_type = settings["server_type"]
        model = settings["model"]
        return server_dict[server_type](model=model, settings=settings)
    except OSError as e:
        print(f"OSError: {e}.\n This can happen if you are" +
              " trying to access a gated repo on HuggingFace" +
              " using the Transformers pipeline. " +
              "Try logging in first."
              )
        print(r"https://huggingface.co/docs/huggingface_hub/en/guides/cli#huggingface-cli-login")
        print(r"https://huggingface.co/docs/hub/security-tokens")
        print(r"Turn on the read permissions under repos")
        raise LLMConnectionError("OSError encountered while loading backend.")
    except Exception as e:
        raise LLMConnectionError(f"{e} encountered while loading backend.")

# dictionary to hold all server classes
server_dict = {}



#%% Server Classes
# Example for future extension:
# class OllamaDockerLLM:
#     ...
# server_dict["docker"] = OllamaDockerLLM


class PlaceholderLLM:
    def __init__(self, model=None, settings=None):
        self.model=model
        self.settings=settings
        pass
    
    def test_LLM_connection(self, fix, previousAttempt):
        return True , "Placeholder LLM"
    
    def _send_command(self, prompt):
        return "Placeholder: I am a placeholder for a real LLM. Please update your settings."
    
server_dict["placeholder"] = PlaceholderLLM



class OllamaBaremetalLLM:
    def __init__(self, model="gemma3:1b", settings=None):
        self.model = model
        if settings is not None:
            warn("settings are not yet implemented for OllamaBaremetalLLM")

    @property
    def prefix(self):
        return r'ollama run ' + self.model

    def _send_command(self, prompt, formatResponse=True, fix=True):
        prefix = self.prefix.split(" ")
        command = prefix + [prompt]
        print(command)
                
        try:
            response = subprocess.run(command, capture_output=True)
        except FileNotFoundError:
            # Subprocess will throw this error if it can't find the command
            # e.g.if Ollama isn't installed
            errorMsg = "FileNotFoundError\nAre you sure your prefix is set correctly?\nIs Ollama installed?"
            print(errorMsg)
            
            if formatResponse:
                return errorMsg 
            else:
                raise FileNotFoundError
        
        if not formatResponse:
            print(f"Response returncode: {response.returncode}")
            return response
        else:
            if response.returncode == 0: # if no errors
                response = str(response.stdout.decode())
                response = f"\n{self.model}:\n" + response + "\n"
                print(response)
            else:
                errorMessage = '\nOops! Something went wrong! Error Code: {}\n\n'.format(response.returncode)
                print(errorMessage)
                
                if fix:
                    connectionStatus, errorMsg = self.test_LLM_connection(fix=True, previousAttempt=response)
                    if connectionStatus:
                        # if fixed try again
                        response = self._send_command(prompt, formatResponse, fix=False)
                    else:
                        response = errorMessage + errorMsg
                else:
                    response = errorMessage
        
        return response


    def test_LLM_connection(self, fix, previousAttempt):
        '''
        Should be customized to each server type to test for and fix common errors.

        Parameters
        ----------
        fix : BOOL
            Should the function attempt to fix a broken connection?
        previousAttempt : TYPE
            The return of a previous _send_command.

        Returns
        -------
        connectionStatus : BOOL
            True if the connection has been re-established.
        errorMsg : STR
            Error message if connection cannot be re-established.

        '''
        connectionStatus = False
        errorMsg = ""
        try:
            if previousAttempt is None:
                response = self._send_command(r"hello", formatResponse=False, fix=False)
            else:
                response = previousAttempt
                
            if response.returncode == 0:
                connectionStatus = True
            elif fix:
                pass # Customize to each server type
        except FileNotFoundError:
            # This can happen if the command passed to subprocess doesn't exist
            # e.g.if Ollama isn't installed
            errorMsg = "FileNotFoundError\nAre you sure your prefix is set correctly?\nIs Ollama installed?"
            print(errorMsg)
        return (connectionStatus, errorMsg)
    
    def exit(self):
        pass # should be defined for each server type
        
# Register backend
server_dict["ollama"] = OllamaBaremetalLLM


class OllamaPodmanLLM(OllamaBaremetalLLM):
    def __init__(self, model="codellama", settings=None):
        self.model = model
        if settings is not None:
            warn("settings are not yet implemented for OllamaPodmanLLM")

    @property
    def prefix(self):
        return r'podman exec ollama ollama run ' + self.model

    # inherited    
    #def _send_command(self, prompt, formatResponse=True, fix=True):

    def test_LLM_connection(self, fix, previousAttempt):
        connectionStatus = False
        errorMsg = ""
        try:
            if previousAttempt is None:
                response = self._send_command(r"hello", formatResponse=False, fix=False)
            else:
                response = previousAttempt
                
            if response.returncode == 0:
                connectionStatus = True
            elif fix:
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
                print('Testing LLM again...\n\n')
                response = self._send_command(r"hello", formatResponse=False, fix=False)
                stderr = response.stderr.decode()
                
                if response.returncode == 0:
                    connectionStatus = True
                else:
                    print(stderr)
                    errorMsg = stderr
        except FileNotFoundError:
            errorMsg = "FileNotFoundError\nAre you sure your prefix is set correctly?\nIs Ollama installed?"
            print(errorMsg)
        return (connectionStatus, errorMsg)
    

    def start_server(self):
        command = r'podman machine start'
        return subprocess.run(command, capture_output=True)

    def stop_server(self):
        command = r'podman machine stop'
        return subprocess.run(command, capture_output=True)

    def start_ollama_container(self):
        command = r'podman start ollama'
        return subprocess.run(command, capture_output=True)

    def stop_ollama_container(self):
        command = r'podman stop ollama'
        return subprocess.run(command, capture_output=True)

    def exit(self):
        print('Stopping Container Service')
        try: 
            self.stop_server()
        except FileNotFoundError: # this can happen if podman isn't installed
            errorMsg = "FileNotFoundError\nAre you sure your prefix is set correctly?\nIs Ollama installed?"
            print(errorMsg)

# Register backend
server_dict["podman"] = OllamaPodmanLLM


from transformers import pipeline
import torch
class TransformersLLM:
    # Note that the default location for the model cache is: C:\Users\<USER>\.cache\huggingface\hub\<model--name>\snapshots
    def __init__(self, model="microsoft/DialoGPT-small", settings={}):
        
        self.model = model
        self.pipe = pipeline("text-generation", model=model, torch_dtype=torch.bfloat16)
        self.settings = settings # note, dictionaries are mutable!
        self.chat_history = []
        
        
    def _send_command(self, prompt, formatResponse=True, fix=True):
        # for details see: https://huggingface.co/google/gemma-3-1b-it?library=transformers
        messages = [
                    {"role": "user", "content": prompt},
                    ]
        
        response = self.pipe(self.chat_history + messages, # send whole chat history, not just most recent message
                             max_new_tokens=self.settings['max_new_tokens'],
                             )
        
        if formatResponse:
            response = response[0]['generated_text'][-1]
            self.chat_history += messages # append to end of history
            self.chat_history.append(response)
            self.manage_chat_history()
            response = response['role'].capitalize() + ": " + response['content'] +'\n'
            
        return response


    def manage_chat_history(self,):
        '''
        Clean and maintain the in memory chat history.
        
        Gemma3 throws a *** jinja2.exceptions.TemplateError: Conversation roles must alternate user/assistant/user/assistant/...
        if the history STARTS with an assistant message, so I am enforcing even histories only.

        Returns
        -------
        None.

        '''
        # Chat history should always be a positive number
        if self.settings['prev_chat_context'] < 2:
            self.settings['prev_chat_context'] = 2
        # gemma3 doesn't like odd histories
        if self.settings['prev_chat_context'] % 2 != 0:
            self.settings['prev_chat_context'] -= 1
            
        # add response to chat history, user prompt is included in response          
        while len(self.chat_history) > self.settings['prev_chat_context']:
            # remove oldest 2 messages
            # gemma3 has issues with odd numbers
            self.chat_history.pop(0)
            self.chat_history.pop(0)


    def test_LLM_connection(self, fix, previousAttempt):
        '''
        Should be customized to each server type to test for and fix common errors.

        Parameters
        ----------
        fix : BOOL
            Should the function attempt to fix a broken connection?
        previousAttempt : TYPE
            The return of a previous _send_command.

        Returns
        -------
        connectionStatus : BOOL
            True if the connection has been re-established.
        errorMsg : STR
            Error message if connection cannot be re-established.

        '''
        connectionStatus = False
        errorMsg = ""
        try:
            self._send_command(r"hello", formatResponse=False, fix=False)
            connectionStatus = True
        except:
            raise
        return (connectionStatus, errorMsg)
    
    def exit(self):
        pass # should be defined for each server type
        
# Register backend
server_dict["transformers"] = TransformersLLM

