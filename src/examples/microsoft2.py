# https://huggingface.co/microsoft/DialoGPT-small
# you might not need all of these but this was the enviornment
# conda install python>3 ipython  transformers pytorch::pytorch accelerate gguf -c conda-forge
# Also see:
# - https://huggingface.co/learn/llm-course/chapter1/1
# - https://huggingface.co/microsoft
# - https://huggingface.co/google/gemma-3-1b-it

from transformers import pipeline
import torch

#pipe = pipeline("text-generation", model="google/gemma-3-1b-it", device="cuda", torch_dtype=torch.bfloat16)
#pipe = pipeline("text-generation", model="microsoft/DialoGPT-small", device="cuda", torch_dtype=torch.bfloat16)
pipe = pipeline("text-generation", model="microsoft/DialoGPT-small", torch_dtype=torch.bfloat16)

print()
print(pipe.tokenizer.chat_template)
print()


#%%

# adopted from Gemma3 example, so this might not work for other models
messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Write a poem on Hugging Face, the company"
        },
]

output2 = pipe(messages, max_new_tokens=50)
print()
print(type(output2))
print()
print(output2)
