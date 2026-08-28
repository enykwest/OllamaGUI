from typing import Optional, List, Dict
from langchain_core.language_models.llms import LLM

class DummyLLM(LLM):
    """A minimal mock LLM for testing CrewAI flows without API calls."""
    
    # Map keywords/roles to hardcoded output strings
    responses: Dict[str, str] = {
        "researcher": "Mock Research: Found key trends in AI, automation, and remote work.",
        "writer": "Mock Article: AI is transforming modern workflows efficiently.",
        "editor": "Mock Edit: Approved. The article looks polished and clear.",
        "default": "Mock Response: Task completed successfully."
    }

    @property
    def _llm_type(self) -> str:
        return "dummy_llm"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[object] = None,
        **kwargs
    ) -> str:
        prompt_lower = prompt.lower()
        
        # Match prompt text to hardcoded role responses
        for key, response in self.responses.items():
            if key in prompt_lower:
                return response
                
        return self.responses["default"]
