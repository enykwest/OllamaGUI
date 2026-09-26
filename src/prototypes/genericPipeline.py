
# conda install python>3 ipython transformers pytorch -c conda-forge
# Also see:
# - https://huggingface.co/meta-llama/CodeLlama-7b-hf
# - https://huggingface.co/docs/transformers/main/en/conversations
# - https://huggingface.co/docs/transformers/main/en/chat_templating
# - https://huggingface.co/learn/llm-course/chapter1/1
# - https://huggingface.co/microsoft
# - https://huggingface.co/google/gemma-3-1b-it

from transformers import pipeline
import torch

#pipe = pipeline("text-generation", model="google/gemma-3-1b-it", device="cuda", torch_dtype=torch.bfloat16)
#pipe = pipeline("text-generation", model="microsoft/DialoGPT-small", device="cuda", torch_dtype=torch.bfloat16)
#pipe = pipeline("text-generation", model="microsoft/DialoGPT-small", torch_dtype=torch.bfloat16)

# generic pipline
pipe = pipeline("text-generation")

# adopted from Gemma3 example, so this might not work for other models
messages = [
    [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."},]
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "Write a poem on Hugging Face, the company"},]
        },
    ],
]

output = pipe(messages, max_new_tokens=50)
print()
print(type(output))
print()
print(output)
