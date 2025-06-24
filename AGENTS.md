## Refactor Bob and Bobbing – Embedding, Chunking, and Retriever Components**

---

### **Part 1: Update Bobbing Metadata Handling and Chunking**

* **Document Source Metadata:**
  In the bobbing utility, store **only the document file name** as the document source in the chunk metadata—**do not include the full path**.

* **Doc-Set Metadata:**
  Add a `"doc-set"` metadata field to every chunk.

  * Default value: **empty string** (`""`), never `null` or `None`.
  * No further use or logic for `doc-set` is required in this change; it’s only to be set and stored for future use.

* **Chunk Size and Overlap:**

  * **chunk\_size** and **chunk\_overlap** must be **configurable parameters** in the `[bobbing]` section of `default-bobbing-config.toml`.
  * The bobbing utility must read these parameters from the config file and apply them when chunking documents for embedding.
  * Provide clear, sensible defaults if these values are not specified.

---

### **Part 2: Refactor Retriever Configuration, Componentization, and Retrieval Parameters**

* **Retriever Naming and IDs:**
  As with agent sections, **retriever components must use IDs in their configuration section names**, following the format:

  ```
  [retriever.id]
  ```

  * (e.g., `[retriever.default]`, `[retriever.my_retriever]`)

* **Multiple Retrievers:**
  Support the **possibility** of multiple retriever components, each with its own config section and ID.

  * For this refactoring, **implement only one retriever type** (but structure the code so more can be easily added).

* **Agent Section Reference:**
  In an agent’s config section, a retriever is referenced by its ID using the parameter:

  ```
  retriever = "retriever.id"
  ```

  * (Do **not** use `@`—this is a direct ID lookup, not a variable reference.)

* **Number of Chunks to Retrieve:**

  * Add a **num\_chunks** (or `top_k`) parameter to the `[retriever.id]` config section.
  * The retriever component must use this parameter to control how many chunks/results are returned from the vector database for each query.
  * Ensure this parameter is read from the config and passed appropriately in retrieval logic.

* **Rename All “Retrieval” to “Retriever”:**
  In both configuration and code, **replace all instances of “retrieval” with “retriever”** for clarity and consistency.


* Adjust the default-bob-config.toml and documentation to reflect the changes
---

### **Additional Implementation Guidance**

* Do **not** implement any advanced usage or logic for `doc-set` at this stage—just set and store it.
* Ensure all config and class/component naming matches the new “retriever” convention.
* Maintain compatibility with LangChain best practices for chunking and embedding.
* Deliver clean, well-commented code with updated config templates reflecting these changes.


