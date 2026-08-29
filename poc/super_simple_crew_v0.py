from typing import Any, Dict, List
from crewai import Agent, Crew, Task, BaseLLM

# 1. Define your custom mock class with an explicit __init__ method
class CrewAIMockLLM(BaseLLM):
    """
    A custom LLM for testing CrewAI pipelines.

    DESIGN NOTE & COMPLIANCE WARNING:
    While 'Explicit is better than implicit' (Zen of Python), this class 
    inherits from a Pydantic v2 architecture (BaseLLM). Pydantic operates 
    as a structured schema parser rather than a vanilla Python object.

    Because of this:
    1. Attributes MUST be declared as top-level class type annotations 
       (e.g., `model: str = ...`). Defining properties via `self.x` inside 
       a standard vanilla `__init__` constructor will bypass Pydantic's 
       schema compiler and trigger validation failures.
    2. Private runtime trackers (like `_call_count`) must use a leading 
       underscore so Pydantic explicitly treats them as vanilla Python 
       state variables and excludes them from model parsing.
    """

    # pydantic compliant attributes
    model: str = "mock-testing-model"
    responses: List[str] = [
        "Thought: I need to write a short summary.\nFinal Answer: Fake LLM execution succeeded."
    ]
    _call_count: int = 0

    def __init__(self, **data: Any):
        # Explicitly guarantee 'model' is populated in the construction payload
        data.setdefault("model", "mock-testing-model")
        super().__init__(**data)

    def call(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Main execution hook that intercepts crew prompts and returns text.
        """
        if self._call_count >= len(self.responses):
            return "Final Answer: No more mock responses configured."
        
        response = self.responses[self._call_count]
        self._call_count += 1
        return response

def test_crew_with_fake_llm():
    # 2. Instantiate your mock smoothly with no positional or keyword args
    fake_llm = CrewAIMockLLM()

    # 3. Supply the valid object straight to your Agent
    agent = Agent(
        role="Writer",
        goal="Generate content",
        backstory="Content generator",
        llm=fake_llm,
        verbose=False
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
        verbose=False
    )
    
    result = crew.kickoff()

    assert "Fake LLM execution succeeded." in str(result)

if __name__ == "__main__":
    test_crew_with_fake_llm()
    print("FakeListLLM test passed successfully!")
