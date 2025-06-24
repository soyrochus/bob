# Technical User Guide

This guide describes the structure of Bob and how to extend it with new agents.

## Application Structure

- **bob.web** – FastAPI application with template rendering.
- **bob.conversations** – Database models and conversation middleware.
- **bob.llm** – Provider module wrapping the OpenAI API.
- **bob.agents** – Implements agent classes and a dynamic registry. New agents
  subclass `BaseAgent` and are instantiated based on the configuration.
- **bob.tasks** – Abstract background task interface with Redis and SQLite
  implementations.
- **bob.token_expander** – Replaces component tokens in messages before they are
  rendered.
- **bob.shared** – Utility helpers for templates and database sessions.
- **bobbing.cli** – Command line tool for managing vector databases.

## Configuration

Settings are read from environment variables in `bob.settings`. Add your OpenAI key in a `.env` file or environment variable. The vector database used by `BobAgent` and `TutorAgent` persists in the `chroma` directory.

## Bobbing CLI

The `bobbing` command manages vector databases used for retrieval augmented
generation. Run `bobbing vectordb create` to initialize a new database or
`bobbing vectordb add FILES...` to add documents. Configuration is read from
`bobbing.toml` in the current directory or your home folder.

## Extending Agents

1. Create a subclass of `BaseAgent` implementing `stream`.
2. Add a `[agents.ID]` section in `bob-config.toml`.
   - Set `agent_type` to the class name if it differs from `ID`.
   - Optionally set `home_selector` to show the agent in the UI.
3. The frontend passes the chosen `ID` back to the backend which retrieves the
   instance from the registry.
