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


if __name__ == "__main__":
    pass
