# Technical User Guide

This guide describes the structure of Bob and how to extend it with new agents.

## Application Structure

- **bob.web** – FastAPI application with template rendering.
- **bob.conversations** – Database models and conversation middleware.
- **bob.llm** – Provider module wrapping the OpenAI API.
- **bob.agents** – Implements `DefaultAgent`, `BobAgent` and `TutorAgent`. New agents should subclass `BaseAgent` and implement the `stream` method.

## Configuration

Settings are read from environment variables in `bob.settings`. Add your OpenAI key in a `.env` file or environment variable. The vector database used by `BobAgent` and `TutorAgent` persists in the `chroma` directory.

## Extending Agents

1. Create a subclass of `BaseAgent` implementing `stream`.
2. Register the agent in `get_agent`.
3. The selected agent name is provided by the frontend and passed through the router to the middleware.
