import subprocess

# needs more work
def get_llm_backend(settings):
    try:
        server_type = settings["server_type"]
        model = settings["model"]
        return server_dict[server_type](model=model)
    except OSError as e:
        print(f"{e} , This can happen if you are" +
              " trying to access a gated repo on HuggingFace" +
              " using the Transformers pipeline. " +
              "Try logging in first."
              )
        print(r"https://huggingface.co/docs/huggingface_hub/en/guides/cli#huggingface-cli-login")
        print(r"https://huggingface.co/docs/hub/security-tokens")
        print(r"Turn on the read permissions under repos")
        raise # todo, return placeholder_llm so user can change the llm settings
    except Exception as e:
        raise # todo, return placeholder_llm so user can change the llm settings

    pass # todo, return placeholder_llm so user can change the llm settings

# dictionary to hold all server classes
server_dict = {}



#%% Server Classes
# Example for future extension:
# class OllamaDockerLLM:
#     ...
# server_dict["docker"] = OllamaDockerLLM






class OllamaBaremetalLLM:
    def __init__(self, model="gemma3:1b"):
        self.model = model

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
    def __init__(self, model="codellama"):
        self.model = model

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
    def __init__(self, model="microsoft/DialoGPT-small"):
        
        self.model = model
        self.pipe = pipeline("text-generation", model=model, torch_dtype=torch.bfloat16)


    # old
    def _send_command(self, prompt, formatResponse=True, fix=True):
        
        response = self.pipe(prompt, max_new_tokens=50,)
        
        if formatResponse:
            response = response[0]['generated_text']
        
        return response


    # new
    def _send_command(self, prompt, formatResponse=True, fix=True):
        # for details see: https://huggingface.co/google/gemma-3-1b-it?library=transformers
        messages = [
                    {"role": "user", "content": prompt},
                    ]
        response = self.pipe(messages, max_new_tokens=50,)
        
        if formatResponse:
            response = response[0]['generated_text'][-1]
            print(response['role']) # debug
            response = response['content']
            print(response) # debug
            
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
            self._send_command(r"hello", formatResponse=False, fix=False)
            connectionStatus = True
        except:
            raise
        return (connectionStatus, errorMsg)
    
    def exit(self):
        pass # should be defined for each server type
        
# Register backend
server_dict["transformers"] = TransformersLLM

