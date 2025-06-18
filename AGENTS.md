# Prompt: Implement UI and Memory Enhancements for Bob Portal

**Objective:**
Update the Bob Portal UI and back-end to add multi-agent selection, proper conversation memory handling (based on recent messages), and a rename conversation feature. See the steps and details below.

---

## 1. Agent Selector in Message Form (Front-end)

* **Location:** Home template, within the message form section (see example block below).
* **Change:**

  * Add a **button or pull-down menu** to the left side of the message input box for agent selection.
  * Use pre-configured agent names (e.g., “Bob”, “Tutor”) as mock values.
  * The selection should be visually present but does not need to affect message routing or logic yet—**purely a UI mockup for now**.
  * Match styling/placement as shown in `design/bog-portal.png`.

  ```html
  <form ...>
    <!-- [Add agent selector button/dropdown here] -->
    <input ... />
    <button ...>Send</button>
  </form>
  ```

---

## 2. Per-Conversation Memory as Latest N Messages

* **Concept:**
  Memory for a conversation is **not a separate database field**. Instead, it is composed of the latest N messages belonging to that conversation. These are used as conversational context (history) when sending prompts to the LLM.
* **Implementation Steps:**

  1. **Configurable N:**

     * The number N (e.g., N=20) determines how many of the most recent messages are included in the context window for the LLM.
     * For now, hardcode N to a reasonable value (e.g., 20), but structure code so it can be easily made configurable.
  2. **Fetching History:**

     * When preparing the input for the LLM, **query the last N messages** for the active conversation, ordered by timestamp.
     * Construct the LLM prompt or message context using these messages, maintaining their chronological order.
  3. **Passing to LLM:**

     * Ensure that only these N messages (not all history, nor global messages) are passed as the conversational context to the LLM API.
     * Update any related message processing, serialization, or context-building logic.
  4. **No Separate Memory Field:**

     * Do **not** add or use a memory field in the conversation model—memory is always dynamically constructed from existing message history.

---

## 3. Conversation Rename Feature (UI & API)

* **UI:**

  * In the conversation menu/list (usually on the left), add a **rename button** for each conversation.
  * When clicked, show a modal/popup with:

    * A text input pre-filled with the current name
    * “OK” and “Cancel” buttons
* **Backend/API:**

  * On “OK,” call an endpoint to update the conversation’s name in the database.
  * On success, update the UI.
  * On “Cancel,” simply close the popup.
  * Implement error handling as needed.

---

## General Notes

* Follow existing UI/UX conventions; refer to `design/bog-portal.png` for style and layout.
* Clearly label any UI elements or logic that are mock/stub with `TODO` comments.
* Minimal tests to cover changes are recommended.
