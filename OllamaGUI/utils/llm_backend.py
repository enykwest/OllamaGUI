import subprocess

def get_llm_backend(settings):
    try:
        server_type = settings["server_type"]
        model = settings["model"]
        return get_llm_backend.servers[server_type](model=model)
    except Exception:
        # Fallback to Podman if any error occurs (missing key or unknown server_type)
        return get_llm_backend.servers["podman"](model="codellama")

get_llm_backend.servers = {}

class LLMConnectionError(Exception):
    pass

class OllamaPodmanLLM:
    def __init__(self, model="codellama"):
        self.model = model
        self.server_type = "podman"

    @property
    def prefix(self):
        return self.server_type + r' exec ollama ollama run ' + self.model

    def _send_command(self, prompt, formatResponse=True, fix=True):
        prefix = self.prefix.split(" ")
        command = prefix + [prompt]
        print(command)
        response = subprocess.run(command, capture_output=True)
        if response.returncode != 0:
            errorMessage = '\nOops! Something went wrong! Error Code: {}\n\n'.format(response.returncode)
            print(errorMessage)
            if fix:
                connectionStatus, errorMsg = self.test_LLM_connection(fix=True, previousAttempt=response)
                if connectionStatus:
                    response = self._send_command(prompt, formatResponse, fix=False)
                else:
                    response = errorMessage + errorMsg
            else:
                response = errorMessage
        elif formatResponse:
            response = str(response.stdout.decode())
            response = "\nOllama:\n" + response + "\n"
            print(response)
        return response

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
        command = self.server_type + r' start ollama'
        return subprocess.run(command, capture_output=True)

    def stop_ollama_container(self):
        command = self.server_type + r' stop ollama'
        return subprocess.run(command, capture_output=True)

    def exit(self):
        print('Stopping Container Service')
        self.stop_server()

# Register backends
get_llm_backend.servers["podman"] = OllamaPodmanLLM

# Example for future extension:
# class OllamaDockerLLM:
#     ...
# get_llm_backend.servers["docker"] = OllamaDockerLLM