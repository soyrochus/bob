##  Implement a Generic, Extensible Settings Protocol with TOML Support for Agent Configurations 

**Objective:**

Implement the following: 

Refactor the project’s configuration system to use a generic `Settings` protocol, allowing multiple implementations (starting with TOML) for hierarchical agent-specific settings. The goal is to make the config system robust, clear, and easily extensible to other formats (YAML, JSON, etc.) in the future, while supporting clean, per-agent configuration.

Obtaining the agent names in the home.html select tag (name=agent) from the Setting. So the agents are configurable
---

### **Requirements**

1. **Settings Protocol:**

   * Define a `SettingsProvider` protocol or abstract base with a single method: `load(path: str) -> dict`.
   * Implement a `TomlSettingsProvider` that loads configuration from a TOML file, supporting nested sections.

2. **Settings Class:**

   * Implement a `Settings` class that:

     * Loads configuration using a pluggable `SettingsProvider`.
     * By default, discovers the config file in environment variable: "bob_config_path" and if not set from the current dir (tries in order: `bob-config.toml`, `bobconfig.toml or `bob.toml`)
     * Supports easy access to a list of agent names and their respective parameters.
     * For each agent, exposes relevant settings, such as:

       * `llm` (for the LLM provider, required for all agents)
       * `vector_db_path` (optional, required for Bob and Tutor)
    for more: see the examlples
     * Cleanly handles missing agents or missing parameters with appropriate errors/defaults.

3. **TOML Example:**

   * Write a `bobbingconfig.toml` defining three agents:

     * **default:** LLM provider only.
     * **bob:** LLM provider and path to vector database.
     * **tutor:** LLM provider and path to vector database.

---

### **Example TOML Config (`bobbingconfig.toml`):**

```toml
[agents.default]
llm = "openai"
openai_api_key="XXXXX"

[agents.bob]
llm = "openai"
openai_api_key="XXXXX"
vector_db_type="Chroma"
vector_db_embedding="openai"
vector_db_embedding="openai"
vector_db_path = "./db/chroma"

[agents.tutor]
llm = "openai"
openai_api_key="XXXXX"
vector_db_type="Chroma"
vector_db_embedding="openai"
vector_db_path = "./db/chroma"```

---

### **Class Requirements:**

* **SettingsProvider Protocol:**

  * Has `load(path: str) -> dict`.

* **TomlSettingsProvider:**

  * Implements the above for TOML files.

* **Settings class:**

  * On construction, accepts a `SettingsProvider` and optional path.
  * Finds and loads the config file, storing the agent settings.
  * Provides:

    * `get_agent_names() -> List[str]`
    * `get_agent(name: str) -> dict`
    * `get_agent_param(name: str, param: str, default=None)`
  * Handles errors or missing configs gracefully.

* **Leave room for future YAML/JSON providers.**

---

### **Deliverables:**

* Python module with:

  * `SettingsProvider` protocol
  * `TomlSettingsProvider` implementation
  * `Settings` class with above requirements
* The example TOML config as above
* Minimal example usage in `__main__` or docstring



**Emphasize clarity and extensibility; avoid breaking changes to other parts of the codebase.**

# Obtaining the agent names in the home.html select tag (name=agent) from the Setting. 
Get from the new SettingsProvider implementation the agents names (with get_agent_names) and use this to show the list. Make the choice of the agent selection "sticky" (so once switched, the agent should be sticky on the session level)