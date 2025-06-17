Here is a **clear, step-by-step prompt** to instruct a code generation agent to implement your requirements, focusing on clarity, ordering, and precision. This is written in a style directly consumable by an advanced code agent (e.g., GitHub Copilot Agents, OpenAI Code Interpreter, or similar “Codecs” agent).

---

# Prompt: Implement UI and Memory Enhancements for Bob Portal

**Overview:**
Update the Bob Portal front-end and back-end to add multi-agent selection, per-conversation memory, and conversation renaming. Follow the detailed steps below. Use the design in `design/bog-portal.png` for UI reference where needed.

---

## 1. Add Agent Selector to Message Form (Front-end)

* **Target File:** Home template (where the message input form is defined).

* **Context:**
  You will find this block:

  ```html
  <form hx-post="/{{ active_conversation.id }}/message" hx-target="#messages" hx-swap="beforeend" hx-on="htmx:afterRequest:this.reset()" class="fixed bottom-0 left-64 right-0 bg-[#f7f8fa] px-12 py-4 flex gap-2 z-10">
      <input type="text" name="text" placeholder="Message Bob..." class="flex-1 px-4 py-3 rounded-xl bg-[#f1f2f4] border-none focus:ring-0 text-[#121416] text-base" />
      <button type="submit" class="bg-[#dce8f3] text-[#121416] px-6 py-2 rounded-full font-semibold text-sm">Send</button>
  </form>
  ```

* **Required Change:**

  * On the left side of the message input box, add a **button or dropdown** to select from different pre-configured agents.
  * This should appear visually as a button or pull-down, **before** the text input field.
  * The menu should **not trigger any functionality yet**—use mock values (e.g., “Default”, “Tutor”) and make it non-interactive (for now just selects agent visually, no logic).
  * Follow the UI style and spacing in `design/bog-portal.png` as closely as possible.

---

## 2. Implement Per-Conversation Memory (Back-end)

* **Requirement:**
  Each conversation instance must have its own memory, i.e., a memory object or structure attached to each conversation.
* **Changes:**

  1. **Data Model:**

     * Ensure that the Conversation model has an associated memory field or mechanism (can be a JSON column, a related table, or similar structure).
     * The memory should persist conversation history or other relevant memory states.
  2. **Message Passing:**

     * When sending a message to the LLM (large language model), **inject only the memory relevant to the active conversation** (not global or cross-conversation memory).
     * Update any logic where the LLM is called to use the conversation’s memory loop/structure.
     * Ensure proper read/write/update for this memory at each user interaction (message sent/received).
  3. **Migration:**

     * If a migration is required, create a migration script for the new memory field.

---

## 3. Conversation Rename Feature (UI and API)

* **Left-side Menu Change:**

  * In the conversation list/menu, add a **button next to each conversation to rename** it.
  * When clicked, display a pop-up/modal allowing the user to edit the conversation name.
  * The modal should have:

    * A text input (pre-filled with the current conversation name)
    * “OK” and “Cancel” buttons

* **Front-end/Back-end Integration:**

  * On “OK”:

    * Call a **service endpoint** to update the conversation’s name in the database.
    * On success, update the UI to reflect the new name.
  * On “Cancel”:

    * Close the modal without making changes.
  * Implement all necessary endpoints, API logic, and error handling.

---

## General Notes

* Maintain existing styles and component structures.
* All new UI elements must match the look and feel of the existing portal (reference `design/bog-portal.png`).
* For any code that is “mock” or placeholder, clearly mark as such with a TODO comment.
* Ensure all new features are covered by minimal tests.

---

**End of prompt.**
