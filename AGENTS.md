# AGENTS.md

## Project Overview

Flask app serving two AI agents (AssistantAgent, GreatGroupAgent) via WeChat group chat. Built on **deepagents** (wraps LangGraph + LangChain) with Redis (checkpointer/cache/locks) and PostgreSQL (long-term memory). All user-facing strings and docstrings are in Chinese (Hong Kong insurance/financial services context).

## Running

```bash
docker compose up -d --build          # Full stack (recommended)

# Local dev (requires Redis + PostgreSQL running + .env)
pip install -r requirements.txt
python app.py                         # Flask on port 5000

python ngrok_launcher.py              # Expose via ngrok (needs NGROK_AUTHTOKEN)
curl http://localhost:5000/health     # Health check
```

No test framework, linter, typechecker, or formatter is configured.

## Architecture

```
app.py                              # Flask entrypoint, routes, Redis message cache + distributed locks
AssistantAgent/
  agent.py                          # Main agent — tools=[send_message, schedule_message_delayed], subagents=[appointment_subagent]
  tools/                            # LangChain @tool functions with Pydantic schemas
    client_tool.py                  # match_client, create_client, update_client
    user_tool.py                    # search_users
    appointment_tool.py             # create_appointment, update_appointment
    policy_tool.py                  # search_companies, search_products, create_policy, update_policy
    send_message.py                 # send_message (uses ToolRuntime for group context)
    schedule_message.py             # schedule_message_delayed (APScheduler + Redis; uses ToolRuntime)
  subagents/
    appointment_subagent.py         # Owns all business CRUD tools; main agent delegates to it
  skills/                           # Filesystem-based deepagents skills (write denied by FilesystemPermission)
    collect-appointment-info/
GreatGroupAgent/
  agent.py                          # tools=[create_group]
  tools/create_group.py             # create_group (uses ToolRuntime for group context)
utils/                              # reply_message, send_image, get_image_type (all active)
```

**Agent routing** (`app.py:66`): group names containing "support" → GreatGroupAgent; all others → AssistantAgent.

**Delegation pattern**: The main AssistantAgent only has `send_message` and `schedule_message_delayed` as direct tools. All business CRUD (client, policy, appointment, user search) is delegated to the `appointment_agent` subagent. Do not add business tools to the main agent — they belong on the subagent.

**Per-group state**:
- One LangGraph thread per group: `{app_name}_{group}`
- Redis lock per group prevents concurrent agent invocations (120s timeout, 60s block)
- Messages cached in Redis until bot is @-mentioned, then combined and sent to agent
- AssistantAgent sets `recursion_limit: 15` on invoke; GreatGroupAgent uses the default

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
- Tools that need group context use `ToolRuntime` parameter (e.g., `send_message`, `schedule_message_delayed`, `create_group`)

## Environment

Required `.env` variables: `API_MODEL`, `API_BASE`, `API_KEY`, `REDIS_URL`, `POSTGRES_URL`, `AA_ROBOT_ID`, `GGA_ROBOT_ID`, `ORGANIZATION_URL`, `ORGANIZATION_KEY`, `ORG_CODE`, `PORT`

For ngrok: `NGROK_AUTHTOKEN`

Docker Compose internal URLs use service names (`redis`, `postgres`), not `localhost`.

Dockerfile uses Python 3.14-slim.

## Gotchas

- `reply_message` in `utils/` is called directly by `app.py` after the agent responds — it is not a LangChain tool and is always active
- `# %%` cell markers throughout — files are developed with VS Code interactive windows
- `test_agent.py` is a manual interactive CLI client (sends real HTTP requests to the Flask app; uses `APP_URL` env var), not an automated test suite
- Skills have `FilesystemPermission(operations=["write"], paths=["/skills/**"], mode="deny")` — the agent cannot write to skills at runtime
