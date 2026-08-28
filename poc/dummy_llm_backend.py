from typing import Optional, List, Dict, Any
from crewai.llm import LLM

class DummyLLM(LLM):
    """A lightweight mock LLM for testing CrewAI without external API calls or LangChain."""
    
    model: str = "dummy-model"
    responses: Dict[str, str] = {
        "researcher": "Mock Research: Found key trends in AI, automation, and remote work.",
        "writer": "Mock Article: AI is transforming modern workflows efficiently.",
        "reviewer": "Mock Edit: Approved. The article looks polished and clear.",
        "default": "Mock Response: Task completed successfully."
    }

    def call(
        self,
        messages: List[Dict[str, str]],
        callbacks: Optional[List[Any]] = None,
        **kwargs: Any
    ) -> str:
        """CrewAI calls `call()` with a list of message dictionaries."""
        # Convert full context to lowercase string to match keywords
        full_text = " ".join([m.get("content", "") for m in messages]).lower()
        
        for key, response in self.responses.items():
            if key in full_text:
                return response
                
        return self.responses["default"]
