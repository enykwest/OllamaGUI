

'''
Functions and classes related to handling the chat history.
'''
from typing import Any, Dict, List

class ChatHistory:
    '''An abstraction class to encapsulate chat history managment and message context.
    Future plans are to connect with an SQL database or JSON to enable saving and loading chat histories.
    '''

    def __init__(self, history: List[Dict[str, str]] = [] ):
        self.history = history # openai compatible, crewai compatible

    
    def add_message(self, message: List[Dict[str, str]] | Dict[str, str]):
        if type(message) is list:
            self.history.extend(message)
        elif type(message) is dict:
            self.history.append(message)
        else:
            raise TypeError("Hint: The input value must be either List[Dict[str, str]] or Dict[str, str]).")


    # I ported this from the llm_backend, but in hindsight the chat history should never be deleted
    # The context should be managed in from  process_prompt in "main.py"
    # This could be useful in the future though for handling an SQL backend
    def manage_chat_history(self):
        '''
        Heartbeat maintence of the Chat History.

        Returns
        -------
        None.

        '''
        pass

        
        if False:
          # Chat history should always be a positive number
          if self.settings['prev_chat_context'] < 0:
              self.settings['prev_chat_context'] = 0
          # gemma3 doesn't like odd histories
          # Gemma3 throws a "*** jinja2.exceptions.TemplateError: Conversation roles must alternate user/assistant/user/assistant/..."
          # if the history STARTS with an assistant message, so I am enforcing even histories only.
          if self.settings['prev_chat_context'] % 2 != 0:
              self.settings['prev_chat_context'] -= 1
            
          # add response to chat history, user prompt is included in response          
          while len(self.chat_history) > self.settings['prev_chat_context']:
              # remove oldest 2 messages
              # gemma3 has issues with odd numbers
              self.history.pop(0)
              self.history.pop(0)


if __name__ == "__main__":
    pass
