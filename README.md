# OllamaGUI
A TkInter based GUI for interacting with locally hosted LLMs.
Currently, the most advanced usage of this app is to load a model from HuggingFace.co using the Transformers Pipeline. Preliminary development has been done to use Ollama (both bare metal and hosted in Podman) and requires you to first setup a podman machine called "ollama" with ollama installed so python can query the model using the shell command 'podman exec ollama ollama run <MODEL_NAME> <PROMPT>'

Ollama development is currently on hold in favor of improving the Transformers pipeline.

## Transformers Pipeline Setup (Recommended):
If you want to use the Transformers Pipeline option you will need the following python modules:
- pytorch
- transformers
- yaml

It is also recommended you install "accelerate" so large models can be split between GPU and CPU memory. In addition to letting you use larger models, it will also help prevent system crashes if you accidently load a model that is too large. All of these modules can be found on pip or conda-forge, but you may if you want to use conda and your GPU you may need to check the pytorch and nvidia channels. Also, Conda seems to default to the cpu only version, so specify a build number appropriate for your GPU with "cuda" in it.

> [!WARNING]
> I have had BSOD issues with PASCAL architecture GPUs. It is unclear if I have a bad GPU or if the newer version of pytorch/transformers is incompatible with them.

# Example Usage:

Until I get around to packaging things as a module or .exe you will have to start the program manually from the command line using the command `python main.py`. This is probably for the best because a lot of debug info is printed to the terminal.

Once you start the app you will be met with a simple chat interface. The first thing you should do is update `Options -> Settings`. Choose an appropriate Server Type (Recommended: Transformers Pipeline) and set your LLM Model. If you're connected to the internet, the server should automatically download the model when you start it (but this may take a while). If you're offline, you *should* be able to use a filepath model instead, but I haven't tested this yet. Ignore the other settings for now.

The program defaults to using the "microsoft/DialoGPT-small" LLM model because it is small and useful for debuging purposes. I recommend trying this model first. However it is pretty useless and sometimes RUDE. I take no responsibility for what it (or any other LLM!) says to you. You can find other models at HuggingFace.co.

> [!note]
> Some of the HuggingFace models require the user to login and agree to their ToS. For full details see their website, but I have tried to include the relevant links in an informational announcement when this error is encountered.
>
> ALSO, there is a known bug when trying to use Google/Gemma type models on GPUs. There are currently no plans to fix this. Use your CPU or try another model.

After you change your settings, be sure to click `Save Changes`. These settings are saved in `OllamaGUI_StartupSettings.yaml` and will be automatically loaded the next time you start the program. You can be edit this file manually using any text editor. If you want to return to the default settings, simply delete the file.

Finally, start your session by choosing `File -> Start Server`. Type in the chat bar at the bottom and click `Send` to prompt the LLM. Your message, and the LLM's response, should appear in the chat history above. **Depending on how large your model is and the performance of your system this may take a while.** When you're done, simple `x` out of the window of choose `File -> Exit` and the server will be shut down. For your convenience you can save and load chats using the file menu, but currently the LLM will forget everything you spoke about even though you (the human) can see the chat history. Have some grace and remind the LLM what you were talking about.

As a reminder, don't forget that training Artificial Intelligence (AI) on public data without owner consent is copyright infringement! In addition, since AI is unable to extrapolate (only interpolate) they are basically plagiarism engines!

Happy Chatting!

## Improving Performance
The best way to improve the answers to your prompts is to use a better model. However, there are some things you can do locally to improve your experience. **Be sure you monitor your local memory usage and CPU/GPU load as you make these changes** so you don't crash your system!

1. When using the **Transformers Pipeline**, every time you open a new window and click `Start Server` you are starting a NEW server, which consumes memory on your machine. Accordingly, close your previous chat window before starting the new server. This shouldn't be an issue for Ollama type servers.
2. When using the **Transformers Pipeline**, `prev_chat_context` sets the length of the chat history maintained by the LLM. When set to zero this means the LLM has no idea what the last message or response was. Increasing this value gives the LLM more context, but also increases memory usage and response time.  
3. When using the **Transformers Pipeline**, In Settings, `max_new_tokens` limits how many characters the LLM is allowed to generate. With small values you may see it's response get cut off. Increasing this number will allow it to blather on longer, but also increase memory usage and increase your wait time. If you want to keep this number low for performance reasons, try asking the LLM to "Be Concise". If you have `prev_chat_context` turned on, you can say "Your message was truncated, please continue where you left off".