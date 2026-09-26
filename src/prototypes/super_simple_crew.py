"""
A Self contained proof-of-concept python script for running crewai
"""

from typing import Any, Dict, List
from crewai import Agent, Crew, Task, BaseLLM

# 1. Define custom mock llm class for testing purposes
class MockLLM(BaseLLM):
    """
    A custom LLM for testing CrewAI pipelines.

    It adds crewai / pydantic required attributes and returns pre-programmed, ReAct formatted, responses when queried.

    DESIGN NOTE & COMPLIANCE WARNING:
    We inherit from BaseLLM instead of LLM as the higher level LLM class is essentially a quick-select
    for various pre-programmed LLM interfaces to common services (e.g. Ollama, openai, anthropic, etc.)
    Here we are building a new LLM service from scratch, so we drop down to BaseLLM to avoid the added pre-programmed complexity.
    """

    def __init__(self, **data: Any):
        """
        Initilize Mock LLM.
        """

        # Explicitly guarantee the 'model' field is populated in the construction payload before initilizing super
        data.setdefault("model", "mock-llm-for-testing")
        super().__init__(**data)

        # The responses attribute holds the conversation history
        # for this mock LLM we hard code responses and return them in order
        self.responses: List[str] = [
            "Thought: I need to write a short summary.\nFinal Answer: Crew execution succeeded."
        ]
        # private counter
        self._call_count: int = 0


    def call(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Main execution hook that intercepts crew prompts and returns text.
        """
        if self._call_count >= len(self.responses):
            return 'Final Answer: No more mock responses configured. Ending "Thinking".'
        
        response = self.responses[self._call_count] # fetch pre-written response
        self._call_count += 1
        return response


# 2. Define a function to setup and run a simple crewai crew using our mock llm
def test_crew_with_mock_llm():
    # 2. Instantiate your mock smoothly with no positional or keyword args
    mock_llm = MockLLM()

    # 3. Supply the valid object straight to your Agent
    agent = Agent(
        role="Writer",
        goal="Generate content",
        backstory="Content generator",
        llm=mock_llm,
        verbose=False # set to True to enable reporting of this agent's activites in the terminal, redunant if crew is verbose
    )

    task = Task(
        description="Write a short summary.",
        expected_output="Summary text.",
        agent=agent
    )

    # Turn memory off to skip background vector-store initialization setups
    crew = Crew(
        agents=[agent], 
        tasks=[task], 
        memory=False, 
        verbose=True # set to True to enable reporting of ALL crew activites in the terminal
    )
    
    result = crew.kickoff()

    assert "Crew execution succeeded." in str(result)
    # print(result) redundant if crew is verbose

if __name__ == "__main__":
    test_crew_with_mock_llm()
