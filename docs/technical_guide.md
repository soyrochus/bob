# Technical User Guide

This guide describes the structure of Bob and how to extend it with new agents.

## Application Structure

- **bob.web** – FastAPI application with template rendering.
- **bob.conversations** – Database models and conversation middleware.
- **bob.llm** – Provider module wrapping the OpenAI API.
- **bob.agents** – Implements agent classes and a dynamic registry. New agents
  subclass `BaseAgent` and are instantiated based on the configuration.

## Configuration

Settings are read from environment variables in `bob.settings`. Add your OpenAI key in a `.env` file or environment variable. The vector database used by `BobAgent` and `TutorAgent` persists in the `chroma` directory.

## Extending Agents

1. Create a subclass of `BaseAgent` implementing `stream`.
2. Add a `[agents.ID]` section in `bob-config.toml`.
   - Set `agent_type` to the class name if it differs from `ID`.
   - Optionally set `home_selector` to show the agent in the UI.
3. The frontend passes the chosen `ID` back to the backend which retrieves the
   instance from the registry.
