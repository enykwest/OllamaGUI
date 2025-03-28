# -*- coding: utf-8 -*-
"""
GUI to talk with ollama hosted in docker
- TODO: Figure out how to wrap text into window.
    Ollama response includes linebreaks (\n)
- TODO: re-write as a class


Demo GUI: https://www.pythonguis.com/tutorials/create-ui-with-tkinter-pack-layout-manager/

"""
import tkinter as tk
import subprocess

root = tk.Tk()
root.title("Simple Chat")
root.geometry("400x300")

# Create a label widget for the chat window
chat_window = tk.Label(root, text="Hello, Top!")
chat_window.pack(side="top", fill='both', expand=True)


# Create an entry widget for the user to input their message
user_prompt = tk.Entry(root)
user_prompt.pack(side='left', fill='x', expand=True)

# Create a button to send the message
send_button = tk.Button(root, text="Send")
send_button.pack(side='right')


# Add a command to the button that will store
# the user's input in the variable "user_prompt"
# and display it in the chat window
def send_message(tkentry, target):
    # Get user prompt from input box
    prompt = tkentry.get()
    #TODO implement safeguards? e.g. replace ' with ", and set as raw?
    print(prompt) # debug
    
    # format prompt for Docker ollama
    prefix = r'docker exec ollama ollama run codellama "'
    
    # format prompt for Podman ollama
    prefix = r'podman exec ollama ollama run codellama "'
    
    command = prefix + prompt +'"'
    command = command.split(' ')
    print(command) # debug

    # send prompt and capture response
    response = subprocess.run(command, capture_output=True)
    if response.returncode != 0:
        print('Oops! Something went wrong! Error Code: {}'.format(response.returncode))
    
    # format prompt for conversation history
    response = str(response.stdout.decode()) # str is probably overkill, but I suspect safer 
    response = "User:\n" + prompt + "\n\nOllama:\n" + response
    
    #debug
    print(response)
    
    chat_window.config(text=response)
    user_prompt.delete(0, tk.END)
    return 0

# Add the command to the button
send_button["command"] = lambda: send_message(user_prompt, None)

root.mainloop()
