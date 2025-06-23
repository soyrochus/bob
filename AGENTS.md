## Instruction Prompt for Extending LLM Provider Model with Agent Selector

### Context

The system currently has an LLM provider model in `LLM.py` based on OpenAI, and a frontend select box (select tag with "agent" name) in the send bar (home.html temlate), currently offering "default" and "tutor" as choices. The backend logic for processing messages is handled in the `stream_agent_response` function in the middleware. You want to extend this so that:

* The provider model supports **multiple agent implementations**.
* Agent selection is dynamic based on user input from the frontend (the agent selector).
* The provider model becomes modular, supporting different agent strategies without breaking the existing "default" (OpenAI) behavior.

### Required Changes

1. **Frontend: Agent Selector**

   * Change the agent selector box values to: `default`, `Bob`, and `tutor`.
   * Ensure that the **selected value** is sent with every backend request as an agent selection parameter.

2. **Backend: Middleware/stream_agent_response**

   * In `stream_agent_response`, receive the agent selector value with each request.
   * Use this value to **dynamically select the corresponding agent implementation**.

3. **Backend: LLM Provider Model Refactor**

   * **Do NOT replace** the current OpenAI LLM provider. Instead, refactor the provider logic to support **multiple agent types** via a common interface or strategy pattern.
   * Implement three agent classes (or strategies):

     * **DefaultAgent**: Uses the current OpenAI LLM provider implementation (no changes to this path).
     * **BobAgent**:

       * Uses the same LLM provider as DefaultAgent.
       * Adds a RAG (Retrieval Augmented Generation) connector based on a local vector database (initially Chroma, via LangChain).
       * On receiving a prompt:

         1. Query the vector database for relevant context using LangChain.
         2. Combine retrieved context with the original prompt.
         3. Send the composed prompt to the LLM provider and return the response.
       * The configuration for Chroma should be separated for future customization.
     * **TutorAgent**:

       * For now, implement TutorAgent as an alias/wrapper for BobAgent (same logic).
       * Expose as a separate implementation to be extended later.

4. **Design/Implementation Principles**

   * **Provider Model** should be extensible; new agents should be easy to add.
   * Use a **factory** or **strategy pattern** to select the agent implementation based on the selector value.
   * All agent classes must conform to a shared interface or abstract base (e.g., `.generate(prompt)`).
   * Separate all configuration parameters (e.g., vector DB connection details) from core logic for maintainability.

5. **Testing/Documentation**

   * Add comments explaining agent selection and extension points for future agents.
   * Briefly document how new agent types can be registered and selected.

---

### Example Implementation Outline


```python
# Abstract interface for agents
class BaseAgent:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError()

# Default agent - current OpenAI LLM logic
class DefaultAgent(BaseAgent):
    def generate(self, prompt: str) -> str:
        # Current implementation
        ...

# Bob agent - RAG-enabled
class BobAgent(BaseAgent):
    def __init__(self, llm_provider, vector_db):
        self.llm = llm_provider
        self.vector_db = vector_db

    def generate(self, prompt: str) -> str:
        context = self.vector_db.query(prompt)
        composed_prompt = f"{context}\n{prompt}"
        return self.llm.generate(composed_prompt)

# Tutor agent - initially same as BobAgent
class TutorAgent(BobAgent):
    pass

# Agent factory
def get_agent(agent_selector: str):
    if agent_selector == "default":
        return DefaultAgent()
    elif agent_selector == "Bob":
        return BobAgent(llm_provider, chroma_vector_db)
    elif agent_selector == "tutor":
        return TutorAgent(llm_provider, chroma_vector_db)
    else:
        raise ValueError("Unknown agent selector")
```

6. Create a full documentation ser in the docs folder. The current index.md is created and maintained by MkDocs. Create a user manual based on the information you can retrieve. Then add
the TEchnical User Guide, explaining the way the site is structured, configured, API etc. 

Link to the docs directory from README and preset the documentation in a proper and readable way. 

## Deliverables

**Update the codebase so that agent selection and routing are handled as above. Do not break current functionality; "default" must behave exactly as it does now.**

** Create the documentation site as specified





