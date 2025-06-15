Refactor the FastAPI application according to these requirements:

1. **Top-Level Application**

   * Create a `web.py` that defines:

     * `app = FastAPI(lifespan=lifespan)`
     * Session middleware, static files mount, Jinja2 setup, `get_db`, and `get_current_user` exactly as today.
     * A root router that includes:

       * A GET `/` route for the homepage that lists conversations.
       * All conversation-related routes mounted under `/conversations` via an `APIRouter`.

2. **Conversations Module**

   * Create a package `conversations/` containing:

     * **`routers.py`** (or `web.py`): defines an `APIRouter(prefix="/conversations")` with routes for:

       * `GET /` (list and show active conversation)
       * `GET /{conv_id}` (view a specific conversation)
       * `POST /{conv_id}/message` (add a user message)
       * `GET /{conv_id}/stream` (stream agent response)
       * `POST /new` (start a new conversation)
       * `GET /search` (search conversations)
     * **`middleware.py`**: export async functions that encapsulate **all** database and LLM logic for conversations:

       * `get_conversations(db, user) -> list[Conversation]`
       * `get_conversation(db, user, conv_id) -> Conversation | None`
       * `create_conversation(db, user) -> Conversation`
       * `save_user_message(db, conv_id, text) -> Message`
       * `stream_agent_response(db, conv_id, user_msg_id) -> AsyncGenerator[str, None]`
       * `search_conversations(db, user, query) -> list[Conversation]`
     * Each route in `routers.py` should:

       * Depend on `get_db` and `get_current_user`.
       * Call its corresponding function in `middleware.py`.
       * Render the same templates or return the same streaming/event formats as today.
       * Import and use `expand_tokens` and `stream_tokens` only inside middleware functions.

3. **Preserve Async Patterns**

   * All `async def` and `await` usage, dependency injection, HTTP signatures, templates, and streaming behavior must remain identical.

4. **Routing Composition**

   * In the top‐level `web.py`, import and include the conversations router:

     ```python
     from conversations.routers import router as conversations_router
     app.include_router(conversations_router)
     ```

Deliver a single, cohesive code refactoring plan as a prompt: no scaffolding commentary, just a clear, imperative specification of what the agent must implement.
