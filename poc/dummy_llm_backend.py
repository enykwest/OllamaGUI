"""
Dummy LLM Backend for CrewAI Proof of Concept

Simulates an LLM by yielding hardcoded responses for different agent roles.
Used to test CrewAI crew creation and task execution without a real LLM host.
"""

import time
from typing import Generator


class DummyLLM:
    """
    Simulates an LLM with hardcoded responses for different agent roles.
    """

    def __init__(self):
        """Initialize the dummy LLM."""
        self.responses = {
            "researcher": "I found that this topic has three main areas: theory, practice, and future direction. "
                         "Research indicates strong potential in all three areas.",
            "writer": "I've crafted a clear, well-structured article covering the research findings. "
                     "The narrative flows logically and is accessible to the target audience.",
            "reviewer": "The work is solid and well-organized. The research is thorough and the writing is clear. "
                       "Ready for publication with minor polish.",
        }

    def call(self, agent_role: str = "default") -> Generator[str, None, None]:
        """
        Yield tokens for the given agent role, simulating streaming LLM output.

        Args:
            agent_role: The role of the agent calling the LLM

        Yields:
            Individual tokens to simulate streaming
        """
        response = self.responses.get(agent_role, self.responses["researcher"])
        
        # Yield tokens with slight delay to simulate streaming
        for token in response.split():
            yield token + " "
            time.sleep(0.03)
