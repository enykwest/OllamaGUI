'''
Holds all the code regarding the setup, querying, and shutdown of LLM models.

New LLMs are implemented as custom classes and are made availible to the user by adding them to the `server_dict` dictionary.
All LLM classes or functions should take in the model name (str) and a settings dictionary and return an LLM object.
The PlaceholderLLM serves as a minimally viable template for new LLMs.
Do not inherit from PlaceholderLLM, but be sure to implement all of the same methods.
Currently we inherit from Crewai's BaseLLM, which feels correct as we can always write our own BaseLLM class if needed.
'''

#%% Import Modules %%#
import subprocess
from warnings import warn
from crewai import BaseLLM, LLM
from typing import Any, Dict, List
import inspect

#%% Utilities %%#
class LLMConnectionError(Exception):
    pass


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
        print('\n\nWTF\n\n') # debug 
        print(f"{e} encountered while loading backend.")
        raise LLMConnectionError(f"{e} encountered while loading backend.")

# dictionary to hold all server classes
server_dict = {}



#%% Server Classes %%#
# Example for future extensions:
# class OllamaDockerLLM:
#     ...
# server_dict["docker"] = OllamaDockerLLM


class PlaceholderLLM(BaseLLM):
    def __init__(self, model='Placeholder', settings={}):
        '''
        The PlaceholderLLM serves as a minimally viable template for new LLMs.
        Do not inherit from PlaceholderLLM, but be sure to implement all of the methods
        '''
        self.model=model
        self.settings=settings

        # Explicitly guarantee the 'model' field is populated in the construction payload before initilizing super
        data = dict()
        data.setdefault('model', self.model)
        super().__init__(**data)
        pass
    
    
    def test_LLM_connection(self, fix, previousAttempt):
        '''
        A method to test if we sucessfully connected to the LLM or not.
        It should be customized to each server type to test for and fix common errors.

        Parameters
        ----------
        fix : BOOL
            Should the method attempt to fix a broken connection?
        previousAttempt : TYPE
            The return of a previous _send_command.

        Returns
        -------
        connectionStatus : BOOL
            True if the connection has been re-established.
        errorMsg : STR
            Error message if connection cannot be re-established.

        '''
        return True , "Placeholder LLM"
    
    
    # deprecated in lieu of call
    def _send_command(self, prompt):
        '''
        Take in a user prompt from the GUI , format it for ingestion into the LLM, send it to the LLM, and return the LLM's formated response to the GUI.
        '''

        return "I am a placeholder for a real LLM. Please update your settings."

    
    def call(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        '''
        Inheriting from crewai's BaseLLM and adding a call command is the simplest way to make custom crewai compatible backends.
        Adding to crews SUPPORTED_NATIVE_PROVIDERS for use with the LLM class would be superior, but require more introspection into how the crewai LLM class works.
        Sources:
        - BaseLLM URL: https://github.com/crewAIInc/crewAI/blob/main/lib/crewai/src/crewai/llms/base_llm.py
        - LLM URL: https://github.com/crewAIInc/crewAI/blob/main/lib/crewai/src/crewai/llm.py
        
        From BaseLLM,
        "Call the LLM with the given messages.
        Args:
            messages: Input messages for the LLM.
                      Can be a string or list of message dictionaries.
                      If string, it will be converted to a single user message.
                      If list, each dict must have 'role' and 'content' keys.
            tools: Optional list of tool schemas for function calling.
                  Each tool should define its name, description, and parameters.
            callbacks: Optional list of callback functions to be executed
                      during and after the LLM call.
            available_functions: Optional dict mapping function names to callables
                               that can be invoked by the LLM.
            from_task: Optional task caller to be used for the LLM call.
            from_agent: Optional agent caller to be used for the LLM call.
            response_model: Optional response model to be used for the LLM call.

        Returns:
            Either a text response from the LLM (str) or
            the result of a tool function call (Any).

        Raises:
            ValueError: If the messages format is invalid.
            TimeoutError: If the LLM request times out.
            RuntimeError: If the LLM request fails for other reasons.
        "
        '''
        # Crews expect a "Final Answer:"
        return "Final Answer: Placeholder: I am a placeholder for a real LLM. Please update your settings."


    def exit(self):
        '''
        Optional, execute any cleanup required to shut down the LLM and clear memory.
        This becomes important if you're frequently switching models
        '''
        pass
# Add PLaceholderLLM to dictionary of availible servers
server_dict["placeholder"] = PlaceholderLLM


def CrewAI_LLM(model, settings):
    '''Wrapper for CreawAI's LLM class. Adds required methods.'''
    # debug
    #llm = LLM('ollama/phi4-mini') # works
    #llm = LLM(model=model) # works

    # crewai must be behind the curve, max_new_tokens is the preferred flag as of 2026
    try:
        setting['max_tokens'] = settings['max_new_tokens']
    except:
        pass

    # Not all of our settings are compatible with crewai's LLM class an causes issues
    signature = inspect.signature(LLM)
    valid_keys = signature.parameters.keys()
    valid_settings = {key:value for (key, value) in settings.items() if key in valid_keys} 
    llm = LLM(**valid_settings)
    
    def test_LLM_connection(fix, previousAttempt):
        '''
        Customized to each server type to test for and fix common errors.

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
            response = llm.call(r"hello")
            connectionStatus = True
        except:
            pass # no attempt to fix the connection
        return (connectionStatus, errorMsg)
    
    # Attach method to llm
    llm.test_LLM_connection = test_LLM_connection

    #debug
    #llm.test_LLM_connection = lambda fix, previousAttempt: (True, "")

    return llm # debug
    #return LLM(model=model, **settings)
server_dict["crewai_llm"] = CrewAI_LLM


class OllamaBaremetalLLM(BaseLLM):
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
        Customized to each server type to test for and fix common errors.

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

    # Inheriting from crewai's BaseLLM and adding a call command is the simplest way to make custom crewai compatible backends
    def call(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        return "Final Answer: Placeholder: I am a placeholder for a real LLM. Please update your settings."
    
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


try:
    from transformers import pipeline
    import torch
    class TransformersLLM(BaseLLM):
        # Note that the default location for the model cache is: C:\Users\<USER>\.cache\huggingface\hub\<model--name>\snapshots
        def __init__(self, model="microsoft/DialoGPT-small", settings={}):
            
            self.model = model
            try: # init pipeline
                # Using `low_cpu_mem_usage=True` or a `device_map` requires Accelerate: `pip install accelerate`
                # device_map='auto' allows large models to be split between GPU and CPU memory as well as the hard disc
                import accelerate
                self.pipe = pipeline("text-generation", model=model, device_map='auto', torch_dtype=torch.bfloat16) # bfloat16 as a comprimise for size vs accuracy
            except ModuleNotFoundError:
                warn("accelerate module not found so only one device (CPU/GPU) will be utilized. System may crash if you try loading a model larger than your memory.")
                self.pipe = pipeline("text-generation", model=model, torch_dtype=torch.bfloat16)

            self.settings = settings # note, dictionaries are mutable!
            self.chat_history = []
            
            
        def _send_command(self, prompt, formatResponse=True, fix=True):
            # for details see:
            #  - https://huggingface.co/docs/transformers/en/chat_templating
            #  - https://huggingface.co/google/gemma-3-1b-it?library=transformers
            messages = [
                        {"role": "user", "content": prompt,},
                        ]
            
            system_prompt = [
                        {"role": "system", "content": self.settings["sys_prompt"],},
                        ]
            
            response = self.pipe(system_prompt + self.chat_history + messages, # send whole chat history, not just most recent message
                                 max_new_tokens=self.settings['max_new_tokens'],
                                 )
            
            if formatResponse:
                response = response[0]['generated_text'][-1]
                self.chat_history += messages # append to end of history
                self.chat_history.append(response)
                self.manage_chat_history()
                response = response['role'].capitalize() + ":\n" + response['content'] +'\n'
                
            return response
    
    
        def manage_chat_history(self,):
            '''
            Clean and maintain the in memory chat history.
            
            Gemma3 throws a "*** jinja2.exceptions.TemplateError: Conversation roles must alternate user/assistant/user/assistant/..."
            if the history STARTS with an assistant message, so I am enforcing even histories only.
    
            Returns
            -------
            None.
    
            '''
            # Chat history should always be a positive number
            if self.settings['prev_chat_context'] < 0:
                self.settings['prev_chat_context'] = 0
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
            # TODO implement fix/don't fix paths
            try:
                self._send_command(r"hello", formatResponse=False, fix=False)
                connectionStatus = True
            except Exception as e:
                print(e)
                errorMsg = e # don't try to fix the problem, just report it
            return (connectionStatus, errorMsg)


        # Inheriting from crewai's BaseLLM and adding a call command is the simplest way to make custom crewai compatible backends
        def call(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
            response = self.pipe(messages, # send whole chat history, not just most recent message
                                 max_new_tokens=self.settings['max_new_tokens'],
                                 )
            return response[0]['generated_text'][-1]['content']     


        def exit(self):
            pass # should be defined for each server type


except ImportError:
    class TransformersLLM(PlaceholderLLM):
        def _send_command(self, prompt):
            error_message="Placeholder: I am a placeholder for a real LLM. An ImportError occured. Make sure you have transformers, accelerate, and pytorch installed or change your LLM settings."
            print(error_message)
            return error_message 
        
# Register backend
server_dict["transformers"] = TransformersLLM

