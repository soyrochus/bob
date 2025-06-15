# Changes to Bob

You are a senior software engineer with deep expertise in Python, FastAPI, Jinja2, async programming, Redis, and SQLAlchemy. Your have the following tasks:

## Refactor the main portal home template

Above the chat panel you will find the folowing panel, with the first one as:

```html
<!-- Main Content -->
  <main class="flex flex-col flex-1">
    <section class="p-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <a href="#" class="bg-white border border-[#dde1e3] rounded-xl p-4 flex flex-col items-center hover:shadow transition">
        <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuANYJc-qk0BJuZbr9NrdoX1mJ-5TmWYZZI-noJamwmbHZUCdg9SX7R3ZRyNTPygERvxim4BnzAjHtIQ5gP4-JZAmGA8G4pX3EEuZ74-aeJZKgTWgcki7KKhtq2dijzNlw3lQaJBM9j0NGczk-R_sxuVyYL4XpFx-hnjpcmSpIk-odcANNIuM-SvU_oQvTkKstSsqoF6sb9mAZQ_pQsK83KcoLHVjrFIWeRlfDvmrxry9s4f4Yx8xyB6h6I-pZiVZnLILwfS09dLh6Y" class="w-12 h-12 rounded-lg mb-2 object-cover" />
        <span class="font-semibold text-sm text-[#121416] mb-1">Onboarding Guide</span>
        <span class="text-xs text-[#6a7681] text-center">Step-by-step instructions to get started.</span>
      </a>
```

Replace this with a Jinja2 for-in statement and get the data for the panels from a home-panels.json file in the root of the project. 

## **Abstract the LLM layer**: Rename and refactor `ChatGPT.py` into a generic `llm.py` module that exposes the same functions (e.g. `generate_text`, `stream_tokens`) as its public protocol, but hides all OpenAI‐specific logic behind an interface. Keep the current OpenAI implementation as one concrete class, but design the module so that adding future providers (e.g. Anthropic, Gemini) requires only a new subclass that implements the same methods.

## **Unify configuration**: Remove all hard‐coded settings and disparate calls to `load.env` in `main.py` and `ChatGPT.py`. Create a single `settings.py` (or equivalent) that reads from a `.env` file via python‐dotenv or Pydantic’s `BaseSettings`, and exposes all application configuration—database URLs, API keys, LLM parameters, web server settings, etc.—through one cohesive settings object imported wherever needed. Use environment variables for the actual values, but ensure every module (FastAPI app, LLM implementation, database layer) pulls its configuration from this centralized settings module.


## Implement two concrete subclasses of a `TaskManager` interface: `RedisTasksManager` and `SingletonTasksManager`.

Requirements:

TaskManager serves as the unified abstraction layer for launching and tracking asynchronous “agent” jobs: its enqueue(payload) method submits a new task to the underlying queueing system (e.g. Redis, SQLite, Cloud Tasks) and returns a JobResponse with a unique job_id and initial PENDING status, while its status(job_id) method retrieves the current state—PENDING, RUNNING, SUCCESS, or FAILED—and, when available, the task’s result or error details, ensuring that callers can uniformly start jobs and poll for their outcomes regardless of the concrete backend implementation.

1. **General**
   - Both managers must implement:
     ```python
     async def enqueue(self, payload: dict) -> JobResponse
     async def status(self, job_id: str) -> JobResponse
     ```
   - Use the shared `models.StatusEnum` and `models.JobResponse` from `models.py`.
   - Do not inline any database or Redis connection configuration—pull all connection strings, credentials, and settings from environment variables or a single configuration object.

2. **RedisTasksManager**
   - Use `aioredis` (or `redis.asyncio`) to connect to Redis.
   - Queueing:
     - Enqueue: push a JSON‐serialized task payload onto a Redis list (e.g. `LPUSH tasks_queue`).
     - Generate `job_id` as a UUID4.
     - Store initial status `PENDING` in a Redis hash: `HSET jobs:{job_id} status PENDING`.
   - Status:
     - Read hash `jobs:{job_id}` and return `JobResponse` with `status`, and if present `result` or `error`.
   - Assume a separate worker process is popping from `tasks_queue`, processing tasks, and writing back to the same hash.

3. **SingletonTasksManager**
   - Use a local **SQLite** database as a persistent queue table.
   - Use **SQLAlchemy** only; all DB setup (engine URL, echo flag, pool settings) must come from a single external config (e.g. `settings.DATABASE_URL`).
   - Define a table `sqlite_tasks` with columns:
     - `id` (UUID primary key),
     - `payload` (JSON),
     - `status` (string),
     - `result` (JSON, nullable),
     - `error` (string, nullable),
     - `created_at` (timestamp),
     - `updated_at` (timestamp).
   - Enqueue:
     - Create a new row with `PENDING` status and return `job_id`.
   - Status:
     - Query the row by `id` and return its fields in a `JobResponse`.
   - This manager runs entirely **in-process**; you can assume a background thread or coroutine periodically pulls and processes tasks from this table, but its implementation is out of scope.

4. **Error handling & edge cases**
   - If `status()` is called for a non-existent `job_id`, return `FAILED` with `error="Job not found"`.
   - Catch and wrap any unexpected exceptions during Redis or DB operations into a `FAILED` `JobResponse.error`.

5. **Code organization**
   - Place Redis logic in `redis_manager.py` and SQLite logic in `sqlite_manager.py`.
   - Import only from standard library, `redis.asyncio`, `sqlalchemy[asyncio]`, and your own `models.py` and `task_manager.py`.
   - Do not hard-code any connection strings—read from `os.getenv` or from a shared `settings.py`.

Generate all necessary import statements, class definitions, and async methods, ready to drop into a FastAPI project. Strive for clear, idiomatic Python 3.11+ code with type hints throughout.
````
