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
from crewai import BaseLLM, LLM, Agent
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
        #print('\n\nWTF\n\n') # debug 
        print(f"{e} encountered while loading backend.")
        raise LLMConnectionError(f"{e} encountered while loading backend.")

# dictionary to hold all server classes
server_dict = {}


def instantiate_cleanly(cls, data_dict):
    """Instantiate a class using only the dictionary keys it accepts."""
    sig = inspect.signature(cls)
    
    # Check if the class accepts arbitrary **kwargs
    has_var_kwargs = any(
        param.kind == inspect.Parameter.VAR_KEYWORD
        for param in sig.parameters.values()
    )
    
    if has_var_kwargs:
        # If **kwargs is accepted, pass the entire dictionary
        return cls(**data_dict)
    
    # Otherwise, filter dictionary keys against the accepted parameter names
    valid_keys = sig.parameters.keys()
    filtered_data = {k: v for k, v in data_dict.items() if k in valid_keys}
    
    return cls(**filtered_data)


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
        #print('Messages passed to LLM: ' , messages) # debug / prompt introspection
        # Crews expect a "Final Answer:"
        return "Final Answer: I am a placeholder for a real LLM. Please update your settings."


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
    #llm = LLM(model=model) # The other keywords appear to be descriptors as opposed to actual settings. More research is needed.
    # pytorch uses 'max_new_tokens' but openai uses 'max_completion_tokens', 'max_new_tokens' is legacy
    settings.update({'max_tokens':settings['max_new_tokens'], 'max_completion_tokens':settings['max_new_tokens'], })
    llm = instantiate_cleanly(LLM, settings)# testing
    #llm = LLM(model=model, max_tokens=10)

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
    
    # Attach the test method to llm
    llm.test_LLM_connection = test_LLM_connection

    return llm
server_dict["crewai_llm"] = CrewAI_LLM


# Transformers Backend
try:
    from transformers import pipeline
    import torch
    class TransformersLLM(BaseLLM):
        # Note that the default location for the model cache is: C:\Users\<USER>\.cache\huggingface\hub\<model--name>\snapshots
        def __init__(self, model="microsoft/DialoGPT-small", settings={}):
            
            # Crewai requirements
            data = {'model' : 'custom-llm'}
            super().__init__(**data)
            
            # Our Stuff
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
            #print(messages) # debug / prompt introspection
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

