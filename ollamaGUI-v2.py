# -*- coding: utf-8 -*-
"""
GUI to talk with ollama hosted in docker
TODO: 
    - re-write as a class
    - allow for multi line input
    - send chat history to a markdown file
    
    
    
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

root = tk.Tk()
root.title("Simple Chat")
root.geometry("400x300")

# Create a label widget for the chat window
#chat_history = tk.Label(root, text="Hello, Top!")
chat_history = scrolledtext.ScrolledText(root, wrap="word",
                                         width=40, height=10,
                                         )
chat_history.insert(tk.INSERT, 'Hello World!\n\n')
chat_history.pack(side="top", fill='both', expand=True, padx = 5, pady = 5)


# Create a button to send the message
send_button = tk.Button(root, text="Send",)
send_button.pack(side='right', padx = 5, pady = 5)

# Create an entry widget for the user to input their message
#user_prompt = tk.Entry(root)
user_prompt = tk.Text(root, height=5,)
user_prompt.pack(side='left', fill='x', expand=True, padx = 5, pady = 5)



# Add a command to the button that will store
# the user's input in the variable "user_prompt"
# and display it in the chat window
def send_message(tkentry, target):
    # Get user prompt from input box
    #TODO re-write GUI to use class methods/interface so we can change widgets without issue
    #prompt = tkentry.get() # for entry box
    prompt = tkentry.get("1.0" , tk.END)
    
    #TODO implement safeguards? e.g. replace ' with ", and set as raw?
    print(prompt) # debug
    
    # format prompt for Docker ollama
    prefix = r'docker exec ollama ollama run codellama'
    
    # format prompt for Podman ollama
    prefix = r'podman exec ollama ollama run codellama'
    
    #command = prefix + prompt +'"'
    #command = command.split(' ')
    
    prefix = prefix.split(" ")
    command = prefix + [prompt]
    
    print(command) # debug

    # send prompt and capture response
    response = subprocess.run(command, capture_output=True)
    if response.returncode != 0:
        print('Oops! Something went wrong! Error Code: {}'.format(response.returncode))
    
    # format prompt for conversation history
    response = str(response.stdout.decode()) # str is probably overkill, but I suspect safer 
    response = "User:\n" + prompt + "\n\nOllama:\n" + response +"\n"
    
    #debug
    print(response)
    
    #chat_history.config(text=response)
    chat_history.insert(tk.INSERT, response)
    chat_history.yview(tk.END)
    #user_prompt.delete(0, tk.END)
    user_prompt.delete("1.0", tk.END)
    return 0

# Add the command to the button
send_button["command"] = lambda: send_message(user_prompt, None)

root.mainloop()
