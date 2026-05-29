# AGENTS.md

## Project Overview

Flask app serving three AI agents via WeChat group chat. Built on **deepagents** (wraps LangGraph + LangChain) with Redis (checkpointer/cache/locks/scheduler) and PostgreSQL (long-term memory). All user-facing strings and docstrings are in Chinese (Hong Kong insurance/financial services context).

## Running

```bash
docker compose up -d --build          # Full stack (recommended)

# Local dev (requires Redis + PostgreSQL running + .env)
pip install -r requirements.txt
python app.py                         # Flask on port 5000

python ngrok_launcher.py              # Expose via ngrok (needs NGROK_AUTHTOKEN)
curl http://localhost:5000/health     # Health check
```

Docker uses **gunicorn** (`--workers 1 --timeout 300`), not `python app.py`.

No test framework, linter, typechecker, or formatter is configured.

## Architecture

```
app.py                              # Flask entrypoint, routes, Redis message cache + distributed locks
AssistantAgent/
  agent.py                          # Main agent — tools=[send_message, schedule_message_delayed, get_current_time, get_information], subagents=[appointment_subagent]
  tools/                            # LangChain @tool functions with Pydantic schemas
    client_tool.py                  # match_client, create_client, update_client
    user_tool.py                    # search_users
    appointment_tool.py             # create_appointment, update_appointment
    policy_tool.py                  # search_companies, search_products, create_policy, update_policy
    send_message.py                 # send_message (uses ToolRuntime for group context)
    schedule_message.py             # schedule_message_delayed (APScheduler + Redis; uses ToolRuntime)
    get_current_time.py             # get_current_time (on main agent, not subagent)
    get_information.py              # get_information (on main agent, not subagent — queries by ID)
  subagents/
    appointment_subagent.py         # Owns all business CRUD tools; main agent delegates to it
  skills/
    appointment/                    # Filesystem-based deepagents skills (write denied by FilesystemPermission)
GreatGroupAgent/
  agent.py                          # tools=[create_group, get_current_time]
  tools/create_group.py             # create_group (uses ToolRuntime for group context)
  tools/get_current_time.py
LicenseAssistant/                   # Directory is LicenseAssistant, class is LicenseAssistantAgent
  agent.py                          # tools=[retrieve_knowledge, send_wedrive_file, send_message]
  tools/
    retrieve_knowledge.py           # RAG search over ChromaDB (insurance exam knowledge base)
    send_wedrive_file.py            # Push WeDrive files to group (uses ToolRuntime)
    send_message.py                 # send_message (uses ToolRuntime, separate from AssistantAgent's)
  skills/onboarding/
Data_process/                       # ChromaDB vector store + data processing scripts; mounted as Docker volume
utils/                              # reply_message, send_image, get_image_type, sanitize_namespace
```

**Agent routing** (`app.py` `assistant_message()`):
- group name contains "预备" → LicenseAssistantAgent
- group name contains "support" (case-insensitive) → GreatGroupAgent
- all others → AssistantAgent

**Delegation pattern**: The main AssistantAgent has `send_message`, `schedule_message_delayed`, `get_current_time`, and `get_information` as direct tools. All business CRUD (client, policy, appointment, user search) is delegated to the `appointment_agent` subagent. Do not add business CRUD tools to the main agent — they belong on the subagent.

**Per-group state**:
- One LangGraph thread per group: `{app_name}_{group}`
- Redis lock per group prevents concurrent agent invocations (300s timeout, 300s block)
- Messages cached in Redis until bot is @-mentioned, then combined and sent to agent
- All three agents set `recursion_limit: 50` on invoke

## Tool Convention

Each tool file follows this pattern:
1. **Pydantic input schemas** — `BaseModel` classes with `Field(...)` for required, `Field(default=...)` for optional
2. **`@tool(args_schema=SchemaClass)`** decorator on the function
3. **Function signature: `**kwargs`** — LangChain validates via Pydantic schema, then passes fields as kwargs
4. **`tools/__init__.py`** re-exports all tools; agent/subagent imports them as a list

Key rules:
- `UpdateXxxInput` extends `CreateXxxInput`, overriding required fields to `Optional`
- Bool fields that default to `False` (e.g., `prepaid_premium`) need special payload handling — `if v` would drop them
- List fields with `min_length=1` for required, `default_factory=list` for optional
- Fixed values (e.g., `status=1, process=0` in create_appointment) go in payload directly, not in input schema
- Time fields use `pattern=r"^$|^\d{4}-\d{2}-\d{2}$"` for validation, converted to Unix timestamp in function body
- Tools that need group context use `ToolRuntime` parameter (e.g., `send_message`, `schedule_message_delayed`, `create_group`, `send_wedrive_file`)

## Environment

Required `.env` variables: `API_MODEL`, `API_BASE`, `API_KEY`, `REDIS_URL`, `POSTGRES_URL`, `AA_ROBOT_ID`, `GGA_ROBOT_ID`, `LA_ROBOT_ID`, `ORGANIZATION_URL`, `ORGANIZATION_KEY`, `ORG_CODE`, `PORT`

For LicenseAssistant RAG (optional — falls back to `API_BASE`/`API_KEY`): `EMBEDDING_API_BASE`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`

For ngrok: `NGROK_AUTHTOKEN`
For test_agent.py: `APP_URL` (defaults to `http://localhost:5000`)

Docker Compose internal URLs use service names (`redis`, `postgres`), not `localhost`.

Dockerfile uses Python 3.14-slim.

## Gotchas

- `reply_message` in `utils/` is only called by `app.py` in the error handler — the success-path call is commented out. Agents send replies via their `send_message` tool, not via `reply_message`
- `# %%` cell markers throughout — files are developed with VS Code interactive windows
- `test_agent.py` is a manual interactive CLI client (sends real HTTP requests to the Flask app; uses `APP_URL` env var), not an automated test suite
- Skills have `FilesystemPermission(operations=["write"], paths=["/skills/**"], mode="deny")` — the agent cannot write to skills at runtime
- Gunicorn runs with `--workers 1` — concurrent requests are handled by Flask threading, not multiple worker processes
- `Data_process/chroma_db` is mounted as a Docker volume (`./Data_process/chroma_db:/app/Data_process/chroma_db`) — persists across container restarts
- Each agent has its own `send_message` tool with a hardcoded robot ID env var (`AA_ROBOT_ID`, `LA_ROBOT_ID`, etc.) — they are not interchangeable
