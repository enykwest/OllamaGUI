# Contributing to OllamaGUI

Thank you for your interest in contributing to OllamaGUI! This document outlines the architecture, philosophy, and guidelines that shape our development process.

## Project Philosophy

OllamaGUI is built on the principle of **modularity and simplicity**. We follow these core tenets:

### 1. Self-Contained Modules
Each module is a self-contained unit that handles one responsibility and only that responsibility:

- **`chat_window.py`** — Handles GUI creation and user interface logic only. Does not concern itself with LLM backends, task orchestration, or external systems.
- **`llm_backend.py`** — Handles starting, running, and stopping LLM hosts. Does not concern itself with GUI rendering, user interaction, or task execution.
- Other future modules follow the same pattern: one module, one concern.

This separation makes debugging, testing, and extending the codebase straightforward. A bug in the GUI does not require understanding LLM hosting; a bug in LLM hosting does not require understanding tkinter.

### 2. Main as the Integration Layer
**`main.py`** is the only place where modules are imported and connected together. It is responsible for:

- Importing all modules
- Wiring them together into a functional tool
- Coordinating initialization and shutdown
- Exposing the final application to the user

This design keeps module boundaries clear and makes the data flow of the entire application visible in one place.

### 3. The Zen of Python
We adhere to [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/). Key principles that guide our work:

- **Simple is better than complex.** Solve the problem at hand; don't over-engineer.
- **Explicit is better than implicit.** Code should clearly show its intent.
- **Readability counts.** Code is read more often than it is written.
- **Sparse is better than dense.** Space things out; don't cram logic together.
- **There should be one obvious way to do it.** Avoid multiple competing patterns in the same codebase.

Run `python -m this` to display the full Zen of Python.

---

## Contributing Guidelines

### Before You Start

1. **Understand the module you're changing.** Read the module's docstring and existing code to understand its single responsibility.
2. **Check if your change respects module boundaries.** If your change requires modifying two modules, ask yourself: is there a way to keep them separate? If not, the change may belong in a new module or in `main.py`.
3. **Verify your change doesn't break the philosophy.** Does it add unnecessary coupling? Does it make a module responsible for multiple concerns? If yes, reconsider the approach.

### Making Changes

#### Adding a Feature
1. Create a feature branch off `dev` (e.g., `feature/crew-integration`, `feature/persistent-history`).
2. Keep changes within a single module if possible. If multiple modules must change, coordinate the changes carefully and document the coupling in comments.
3. Write clear docstrings for new functions and classes.
4. Test your changes manually (and write unit tests if the change is complex).

#### Fixing a Bug
1. Create a bugfix branch off `dev` (e.g., `bugfix/settings-not-loading`, `bugfix/chat-history-display`).
2. Fix the bug in the module where it originated, not by patching another module.
3. Add a comment explaining why the bug occurred and how it's fixed.
4. Test the fix thoroughly.

#### Refactoring
1. Refactoring is welcome, but **preserve the module's public interface.** Other modules must not be aware of internal refactorings.
2. Keep refactorings small and focused. Large refactorings are easier to review and revert if needed.
3. Ensure all tests (manual or automated) still pass.

### Commit Messages

Write clear, concise commit messages with this structure:

```
Short, intent-focused summary (50 chars or less)

Detailed description of what was changed and why. Explain the problem you're
solving and the reasoning behind your approach.

Files Changed:
- module_name.py: description of changes
- another_module.py: description of changes
```

**Guidelines:**
- Group logically related file changes together in a single commit.
- Avoid dozens of tiny commits, but also avoid mixing unrelated changes in the same commit.
- Reference issues or design decisions when relevant (e.g., "Fixes #42").

### Pull Requests

1. **Reference an issue** if one exists (e.g., "Fixes #42").
2. **Describe what changed and why.** Link your change back to the module's responsibility and the project philosophy.
3. **Keep PRs focused.** One feature or fix per PR. Don't mix unrelated changes.
4. **Expect review.** Be prepared to explain your design choices and adjust if needed.

### Branching & Merging

- **Feature branches:** Branch off `dev` (e.g., `feature/crew-integration`, `feature/persistent-history`).
- **Bugfix branches:** Branch off `dev` (e.g., `bugfix/settings-not-loading`, `bugfix/chat-history-display`).
- **PR workflow:** Submit a PR from your feature/bugfix branch into `dev` for review and testing.
- **Releasing to main:** Merge stable, tested versions of `dev` into `main` for production releases.

---

## Architecture Example: Adding Crew Integration

To illustrate the philosophy, here's how Proposal 3 (Conversational Crew Director) would be integrated:

**Module Responsibilities:**
- `chat_window.py` — Unchanged. Still only renders chat UI and captures user input.
- `crew_orchestrator.py` (new) — Handles CrewAI task creation and execution. Does not import `chat_window.py`.
- `llm_backend.py` — Unchanged. Still only manages LLM hosts.
- `main.py` — Imports all three modules and wires them together:
  - User input from `chat_window` → passed to `crew_orchestrator`
  - `crew_orchestrator` uses `llm_backend` to execute crew tasks
  - Results from `crew_orchestrator` → displayed in `chat_window`

**Why this works:**
- `chat_window.py` remains simple and GUI-focused. It has no knowledge of CrewAI.
- `crew_orchestrator.py` is a cohesive unit for all crew-related logic.
- `llm_backend.py` still owns LLM host management.
- The integration logic lives in `main.py`, making dependencies and data flow visible.

---

## Questions?

If you have questions about the architecture or philosophy, open an issue or start a discussion. We're here to help newcomers understand the design and contribute effectively.

---

**Happy contributing!** 🚀
