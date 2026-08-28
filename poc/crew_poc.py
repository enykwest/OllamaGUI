"""
CrewAI Proof of Concept

Demonstrates a simple multi-agent workflow using CrewAI:
- Researcher agent gathers information
- Writer agent creates content
- Reviewer agent validates quality

Uses a dummy LLM backend (hardcoded responses) to avoid external dependencies.

Usage:
    python poc/crew_poc.py
"""

from crewai import Agent, Task, Crew
from dummy_llm_backend import DummyLLM


class CrewPOC:
    """
    Proof of concept for CrewAI integration.
    Demonstrates agent creation, task definition, and crew execution.
    """

    def __init__(self):
        """Initialize the POC with a dummy LLM."""
        self.llm = DummyLLM()
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
            llm=self.llm,
        )

        self.agents["writer"] = Agent(
            role="Writer",
            goal="Create clear, engaging content based on research.",
            backstory="A skilled writer who crafts compelling narratives.",
            llm=self.llm,
        )

        self.agents["reviewer"] = Agent(
            role="Reviewer",
            goal="Validate content quality and provide feedback.",
            backstory="A meticulous editor with high quality standards.",
            llm=self.llm,
        )

    def create_tasks(self) -> None:
        """
        Create tasks for each agent.
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
        )

        self.tasks["review"] = Task(
            description="Review the article for quality and clarity.",
            expected_output="Feedback and quality assessment.",
            agent=self.agents["reviewer"],
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
