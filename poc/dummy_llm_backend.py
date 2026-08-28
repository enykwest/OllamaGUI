"""
Dummy LLM Backend for CrewAI Proof of Concept

Simulates an LLM with hardcoded responses for different agent roles.
Implements LangChain's LLM interface for CrewAI compatibility.
"""

from langchain.llms.base import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Any


class DummyLLM(LLM):
    """
    Simulates an LLM with hardcoded responses for different agent roles.
    Implements LangChain's LLM interface for CrewAI compatibility.
    """

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "dummy"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Run the LLM on the given prompt.
        Returns a hardcoded response based on agent role.

        Args:
            prompt: The input prompt
            stop: Stop words (ignored)
            run_manager: Callback manager (ignored)
            **kwargs: Additional kwargs

        Returns:
            Hardcoded response string
        """
        # Extract agent role from kwargs, default to "researcher"
        agent_role = kwargs.get("agent_role", "researcher")

        responses = {
            "researcher": "I found that this topic has three main areas: theory, practice, and future direction. "
                         "Research indicates strong potential in all three areas.",
            "writer": "I've crafted a clear, well-structured article covering the research findings. "
                     "The narrative flows logically and is accessible to the target audience.",
            "reviewer": "The work is solid and well-organized. The research is thorough and the writing is clear. "
                       "Ready for publication with minor polish.",
        }

        return responses.get(agent_role, responses["researcher"])
