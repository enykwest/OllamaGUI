# OllamaGUI
A TkInter based GUI for interacting with locally hosted LLMs.

## Development Status
Currently, we are in the process of integrating the `crewai` python module in order to implement advanced features such as "crews" and tool usage. As of right now there are four ways to connect to an LLM:
1. Automatically download and run a model directly from HuggingFace.co using the **Transformers Pipeline** backend. by specifying the "<channel>/<model-name>".
2. Automatically download and run a model via Ollama (installed separately) by using the **Ollama or Cloud Provider* backend. "ollama/<model-name>".
3. Connect to a cloud provider via the **Ollama or Cloud Provider* backend (untested, plus you must export the API key as an evironmental variable).
4. Manually download a model from HuggingFace.co and run it using the **Transformers Pipeline** backend by specifing the path. (good for offline computers)

The preliminary development that has been done to use Ollama hosted in Podman or docker will be abandoned in favor of supporting Generic OpenAI-compatible Endpoints by specifying the base_url.

# Installation

> [!note]
> **Super Easy Windows Setup**
> For Windows unfamiliar with python, windows batch files (`.bat`) are provided. These will setup your python environment for you, but currently install the CPU version of the Transformers Pipeline Setup .First install python by going to your search bar and typing `cmd` and launching "Command Prompt". A black terminal should pop-up. In the terminal type `python` and hit `enter`. The Microsoft store should pop-up and prompt you to install python. After that is done run `WindowsPythonSetup.bat` by double clicking it. If that works you're done! Double click `WindowsPythonLauncher.bat` to launch the GUI and proceed to [[#App Setup]].

I originally began with Ollama, then transitioned to Podman after encountering some bugs, and finally decided that the Transformers Pipeline was the best path forward to locally hosted LLMs. This app offers interfaces to all three, but I highly recommend using the [[#Transformers Pipeline Setup (Recommended)]] below.

No matter what you decide, this is a python app so you will need some installation of python. If you're **not** using the easy windows setup above, then I recommend using [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main). 

The only required (non-standard) packages are:
- pyyaml
- crewai
but the Transformers Pipeline has more requirements.

If you're **not** using the easy windows setup above, then I recommend using [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main). Windows batch files are provided for those as well, but sometimes windows can't find conda.

## Ollama Setup (not recommended or discouraged)

1. Install Python. The only required (non-standard) packages are:
  - pyyaml
  - crewai
2. Install [Ollama](https://ollama.com/), get it working from the command line, then proceed to [[#App Setup]].

This will probably become the recommended setup in the future with our crewai upgrades, but I haven't done enough testing to endorse it yet.

## Ollama via Podman & Docker Setup (Abandoned)

This feature outlived it's usefulness and was removed from this version of the code.
Future versions will support Docker and Podman via a Generic OpenAI-compatible Endpoints by specifying the base_url, effectively treating them as cloud providers.

## Transformers Pipeline Setup (Recommended):
If you want to use the Transformers Pipeline option you will need a python distribution and an environment with the following python modules:
- pytorch
- transformers
- pyyaml
- crewai

It is also recommended you install "**accelerate**" so large models can be split between GPU and CPU memory. In addition to letting you use larger models, it will also help prevent system crashes if you accidently load a model that is too large. All of these modules can be found on pip or conda-forge, but if you want to use your GPU make sure you install a cuda build (conda users may need to check the pytorch and nvidia channels for cuda builds). Conda should automatically install the proper cuda-toolkit, but pip users may need to do that separately.

(CPU Setup): A `environment.yml` file is provided for conda users and a `requirements.txt` for pip.

After you install the appropriate packages proceed to [[#App Setup]].

> [!WARNING]
> I have had BSOD issues with PASCAL architecture GPUs. It is unclear if I have a bad GPU or if the newer version of pytorch/transformers is incompatible with them.

# App Setup:

> [!note]
> **Super Easy Windows Setup**
> Windows users unfamiliar with python, and with no desire to learn, should use the Super Easy Windows Setup described in the [[#Installation]] section.

Until I get around to packaging things as a module or .exe you will have to start the program manually from the command line using the command `python main.py`. This is probably for the best because a lot of debug info is printed to the terminal.

Once you start the app you will be met with a simple chat interface. The first thing you should do is update `Options -> Settings`. Choose an appropriate Server Type (Recommended: Transformers Pipeline) and set your LLM Model. If you're connected to the internet, the application should automatically download the model when you start it (but this may take a while). If you're offline, you specify a file path to a downloaded model instead.

The program defaults to using the "microsoft/DialoGPT-small" LLM model because it is small and useful for debugging purposes. I recommend trying this model first. However it is pretty useless and sometimes **rude**. I take no responsibility for what it (or any other LLM!) says to you. You can find other models at HuggingFace.co. I really like the phi4 family of models.

> [!warning]
> Some of the HuggingFace models require the user to login and agree to their ToS. For full details see their website, but I have tried to include the relevant links in an informational announcement when this error is encountered.
>
> ALSO, there is a known bug when trying to use Google/Gemma type models on GPUs. There are currently no plans to fix this. Use your CPU or try another model.

After you change your settings, be sure to click `Save Changes`. These settings are saved in `OllamaGUI_StartupSettings.yaml` and will be automatically loaded the next time you start the program. You can edit this file manually using any text editor. If you want to return to the default settings, simply delete the file.

Finally, start your session by choosing `File -> Start Server`. Type in the chat bar at the bottom and click `Send` to prompt the LLM. Your message, and the LLM's response, should appear in the chat history above. **Depending on how large your model is and the performance of your system this may take a while.** When you're done, simply `x` out of the window or choose `File -> Exit` and the server will be shut down. For your convenience you can save and load chats using the file menu, but currently the LLM will forget everything you spoke about even though you (the human) can see the chat history. Have some grace and remind the LLM what you were talking about.

>[!note]
> We are currently in a backend transition. The Ollama server is currently **not** automatically started or shutdown.

As a reminder, don't forget that training Artificial Intelligence (AI) on public data without owner consent is copyright infringement! In addition, since AI is unable to extrapolate (only interpolate) they are basically plagiarism engines!

Happy Chatting!

## Improving Performance
The best way to improve the responses to your prompts is to use a better model. However, there are some things you can do locally to improve your experience. **Be sure you monitor your local memory usage and CPU/GPU load as you make these changes** so you don't crash your system!

1. When using the **Transformers Pipeline**, every time you open a new window and click `Start Server` you are starting a NEW server, which consumes memory on your machine. Accordingly, close your previous chat window before starting the new server. This shouldn't be an issue for Ollama type servers unless you are querying different models.
2. When using the **Transformers Pipeline**, `prev_chat_context` sets the length of the chat history maintained by the LLM. When set to zero this means the LLM has no idea what the last message or response was. Increasing this value gives the LLM more context, but also increases memory usage and response time. Set this to "-1" to always send the full chat history.  
3. When using the **Transformers Pipeline**, In Settings, `max_new_tokens` limits how many characters the LLM is allowed to generate. With small values you may see it's response get cut off. Increasing this number will allow it to blather on longer, but also increase memory usage and increase your wait time. If you want to keep this number low for performance reasons, try asking the LLM to "Be Concise" or "limit your response to 140 characters". If you have `prev_chat_context` turned on, you can say "Your message was truncated, please continue where you left off".

>[!note]
> We are currently in a backend transition. `prev_chat_context` and `max_new_tokens` do not function in this version.

### Notes on GPUs
GPUs are confusing beasts that sometimes work like magic and other times crash your computer. Below are some notes (mostly for myself) regarding getting up and running with GPUs.
- Despite what I said earlier, splitting models between your GPU memory and CPU memory is a terrible idea. Often the time spent copying memory between the two devices is so slow that you are better off NOT using your GPU at all, instead run in CPU only mode. Accordingly, for best *speed* choose models that fit completely fit into GPU memory. 
- For best performance (or to destabilize your system due to an unforeseen bug) update your GPU drivers.
- If you have a NVIDIA graphics card, you can check your GPU driver version and architecture with `nvidia-smi`.
  - The information will help you install the right version of pytorch, as the "build number" should include the word `cuda` and a number that matches your driver. For example, if you have Cuda version 11.7 you could run `conda install pytorch>=1="*cuda11.7*" -c pytorch` or `conda install pytorch>=1="*cuda117*" -c conda-forge` ...maybe
