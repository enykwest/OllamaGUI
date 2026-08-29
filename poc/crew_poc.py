"""
CrewAI Proof of Concept

Demonstrates a simple multi-agent workflow using CrewAI:
- Researcher agent gathers information
- Writer agent creates content based on research
- Editor agent validates quality

Uses a mock LLM backend (hardcoded responses) to avoid external dependencies.

Usage:
    python -m poc.crew_poc
"""
#%% Import Modules %%#
from typing import Any, Dict, List
from crewai import Agent, Crew, Task, BaseLLM


#%% Define Classes %%#

# Define custom mock llm class for testing purposes
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
            "Thought: This is a hard-coded response from a mock LLM.\nFinal Answer: Agent call to LLM succeeded."
        ]
        # private counter
        self._call_count: int = 0


    # Original Template
    def call(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Main execution hook that intercepts crew prompts and returns text.

        NOTE:
        Updated 8/29/2026
        When overloading the call method, remember that messages are formated like so:
        [{'role': 'system', 'content': 'You are <agent role>. <agent backstory>.\nYour personal goal is: <agent goal>', 'cache_breakpoint': True},
         {'role': 'user', 'content': "\nCurrent Task: " + <task description> + "\n\nThis is the expected criteria for your final answer: " + <task expected_outcome> + "\nyou MUST return the actual complete content as the final answer, not a summary.\n\nThis is the context you're working with:\n" + <task context> + "\n\nProvide your complete response:", 'cache_breakpoint': True}]
        """
        #print(messages) # debug
        if self._call_count >= len(self.responses):
            return 'Final Answer: No more mock responses configured in mock LLM.'
        
        response = self.responses[self._call_count] # fetch pre-written response
        self._call_count += 1
        return response
    
    
class researchLLM(MockLLM):
    "hardcoded mock LLM for researcher"

    def _init__(self):
        super.__init__()
        self.responses: List[str] = [
            "Thought: I have gathered all the information on the topics and identified key findings.\nFinal Answer: Agent call to LLM succeeded."
        ]

    
class writerLLM(MockLLM):
    "hardcoded mock LLM for researcher"

    def _init__(self):
        super.__init__()
        self.responses: List[str] = [
            "Thought: I have createe clear, engaging content based on research.\nFinal Answer: Agent call to LLM succeeded."
        ]


class editorLLM(MockLLM):
    "hardcoded mock LLM for researcher"

    def _init__(self):
        super.__init__()
        self.responses: List[str] = [
            "Thought: I have validated the content quality and provided feedback.\nFinal Answer: Agent call to LLM succeeded."
        ]


class CrewPOC:
    """
    Proof of concept for CrewAI integration.
    Demonstrates agent creation, task definition, and crew execution.
    """

    def __init__(self):
        """Initialize the POC with a dummy LLM."""
        #self.llm = MockLLM() # for this test we have transitioned to individual LLMs for each role 
        self.agents = {}
        self.tasks = {}
        self.crew = None

    def create_agents(self) -> None:
        """
        Create three agents with different roles.
        """
        self.agents["researcher"] = Agent(
            role="Researcher",
            goal="Gather information on topics and identify key findings.",
            backstory="An experienced researcher skilled at analysis.",
            llm=researchLLM(),
            verbose=False,
        )

        self.agents["writer"] = Agent(
            role="Writer",
            goal="Create clear, engaging content based on research.",
            backstory="A skilled writer who crafts compelling narratives.",
            llm=writerLLM(),
            verbose=False,
        )

        self.agents["editor"] = Agent(
            role="Editor",
            goal="Validate content quality and provide feedback.",
            backstory="A meticulous editor with high quality standards.",
            llm=editorLLM(),
            verbose=False,
        )

    def create_tasks(self) -> None:
        """
        Create tasks for each agent with proper dependencies.
        """
        self.tasks["research"] = Task(
            description="Research the topic 'Future of AI' and compile findings.",
            expected_output="Key findings on AI trends and implications.",
            agent=self.agents["researcher"],
        )

        self.tasks["write"] = Task(
            description="Write an article based on the research findings.",
            expected_output="A well-written article with clear structure.",
            agent=self.agents["writer"],
            context=[self.tasks["research"]],
        )

        self.tasks["review"] = Task(
            description="Review the article for quality and clarity.",
            expected_output="Feedback and quality assessment.",
            agent=self.agents["editor"],
            context=[self.tasks["write"]],
        )

    def create_crew(self) -> None:
        """
        Assemble the crew from agents and tasks.
        """
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            verbose=True,
        )

    def execute(self) -> str:
        """
        Execute the crew workflow.

        Returns:
            The final result from crew execution
        """
        if self.crew is None:
            raise RuntimeError("Crew not initialized. Call create_agents(), create_tasks(), and create_crew() first.")

        return self.crew.kickoff()

    def run(self) -> None:
        """
        Full POC execution: create agents, tasks, crew, and execute.
        """
        print("\n" + "="*70)
        print("CrewAI Proof of Concept")
        print("="*70 + "\n")

        print("[1] Creating agents...")
        self.create_agents()
        print(f"    Created {len(self.agents)} agents\n")

        print("[2] Creating tasks...")
        self.create_tasks()
        print(f"    Created {len(self.tasks)} tasks\n")

        print("[3] Assembling crew...")
        self.create_crew()
        print("    Crew ready\n")

        print("[4] Executing workflow...\n")
        print("-"*70)
        try:
            result = self.execute()
            print("-"*70)
            print("\n[RESULT]\n")
            print(result)
            print("\n" + "="*70)
            print("Proof of Concept Completed")
            print("="*70 + "\n")
        except Exception as e:
            print(f"\n[ERROR] {e}")
            raise


if __name__ == "__main__":
    poc = CrewPOC()
    poc.run()
