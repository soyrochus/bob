Implement the following dynamic agent instantiation and selection mechanism using the provided configuration pattern:

### 1. **Agent Configuration Parsing**

* Agent definitions reside under `[agents.ID]` sections in `config.toml`.

  * The `ID` (after `agents.`) is the unique agent identifier.
* Within each agent config:

  * If `agent_type` is set, it denotes the class/type to instantiate.
  * If `agent_type` is **not** set, **use the agent's ID as the type**.
    ***This behavior must be documented clearly in code.***
  * If `home_selector` is present, its value will be used as the label in the frontend agent selector.

### 2. **Dynamic Agent Instantiation and Caching**

* On startup (or config reload), **parse all `[agents.*]` sections**.
* For each agent:

  * Instantiate the correct agent class, determined by `agent_type` or, if absent, by ID.
  * Cache the instantiated agents in a **global registry** keyed by agent ID.
  * Ensure that each agent is instantiated only once and reused throughout the application.
* Remove hardcoded instantiation logic (e.g., no `if id == "bob": ...` in `get_agent`).
  The code should be fully data-driven based on config.

### 3. **Frontend Selector Logic**

* **Agents shown in the frontend selector** are those with a `home_selector` value set.

  * For each agent with `home_selector`, present a tuple:

    * `(ID, home_selector)`
      *Example: `("bob", "Maverick")`.*
* The **ID** is used internally and for backend API calls.
  The **home\_selector** value is shown as the visible label in the UI.
* Agents without `home_selector` are instantiated and available internally but **not shown in the frontend selector**.

### 4. **Behavioral Requirements**

* If `home_selector` is omitted, the agent should not be included in the frontend selector, but should still be instantiated and available via API if needed.
* All agent lookups and operations must go through the global registry, using the ID.
* If agent configuration is changed at runtime, update the registry and refresh the frontend selector as needed.

### 5. **Documentation and Example**

* **Document in code**:

  * How agent instantiation resolves class/type via `agent_type` or ID fallback.
  * The purpose and usage of `home_selector`.
* **Example TOML snippet:**

  ```toml
  [agents.default]
  agent_type = "default"
  llm = "openai"
  openai_api_key = "@openai_api_key"

  [agents.bob]
  agent_type = "bob"
  home_selector = "Maverick"
  llm = "openai"
  # ...

  [agents.tutor]
  # agent_type omitted; class 'tutor' will be used
  # no home_selector; will not appear in frontend selector

  [agents.coach]
  agent_type = "tutor"
  home_selector = "Coach"
  # ...
  ```

---

### **Summary of Steps**

* Parse `[agents.*]` in config.
* For each, determine `agent_type` (or ID), instantiate, cache in registry.
* Build frontend selector list as `[(ID, home_selector)]` for agents where `home_selector` exists.
* Ensure code and config are thoroughly documented.

