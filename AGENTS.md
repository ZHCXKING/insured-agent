# AGENTS.md

## Project Overview

Flask app serving two AI agents (AssistantAgent, GreatGroupAgent) via WeChat group chat. Built on **deepagents** (wraps LangGraph + LangChain) with Redis (checkpointer/cache/locks) and PostgreSQL (long-term memory). All user-facing strings and docstrings are in Chinese (Hong Kong insurance/financial services context).

## Running

```bash
# Full stack (recommended)
docker compose up -d --build

# Local dev (requires Redis + PostgreSQL running + .env configured)
pip install -r requirements.txt
python app.py                    # Flask on port 5000

# Expose via ngrok
python ngrok_launcher.py

# Health check
curl http://localhost:5000/health
```

No test framework, linter, typechecker, or formatter is configured.

## Architecture

```
app.py                          # Flask entrypoint, routes, Redis message cache + distributed locks
AssistantAgent/
  agent.py                      # AssistantAgent class (deepagents setup)
  tools/                        # LangChain @tool functions with Pydantic schemas
    client_tool.py              # match_client, create_client, update_client
    user_tool.py                # search_users
    Appointment_tool.py         # create_appointment, update_appointment
    policy_tool.py              # search_companies, search_products, create_policy, update_policy
    send_message.py             # send_message (currently disabled — print only)
    schedule_message.py         # schedule_message_delayed (APScheduler + Redis; currently disabled)
  skills/                       # Filesystem-based deepagents skills (write denied)
  subagents/                    # Placeholder
GreatGroupAgent/
  agent.py                      # GreatGroupAgent class
  tools/create_group.py         # create_group (WeChat group creation)
utils/                          # reply_message (disabled), send_image (active), get_image_type
```

- One LangGraph thread per group: `{app_name}_{group}`
- Redis lock per group prevents concurrent agent invocations (120s timeout, 60s block)
- Messages cached in Redis until bot is @-mentioned, then combined and sent to agent

## Tool Convention

Each tool file follows this pattern:
1. **Pydantic input schemas** — `BaseModel` classes with `Field(...)` for required, `Field(default=...)` for optional
2. **`@tool(args_schema=SchemaClass)`** decorator on the function
3. **Function signature: `**kwargs`** — LangChain validates via Pydantic schema, then passes fields as kwargs
4. **`tools/__init__.py`** re-exports all tools; agent class imports them as a list

Key rules:
- `UpdateXxxInput` extends `CreateXxxInput`, overriding required fields to `Optional`
- Bool fields that default to `False` (e.g., `prepaid_premium`) need special payload handling — `if v` would drop them
- List fields with `min_length=1` for required, `default_factory=list` for optional
- Fixed values (e.g., `status=1, process=0, type=3` in create_appointment) go in payload directly, not in input schema
- Time fields use `pattern=r"^$|^\d{4}-\d{2}-\d{2}$"` for validation, converted to Unix timestamp in function body
- `Appointment_tool.py` is the legacy file — do not modify it; tools have been migrated to their own files

## Environment

Required `.env` variables: `API_MODEL`, `API_BASE`, `API_KEY`, `REDIS_URL`, `POSTGRES_URL`, `AA_ROBOT_ID`, `GGA_ROBOT_ID`, `ORGANIZATION_URL`, `ORGANIZATION_KEY`, `ORG_CODE`, `PORT`

Dockerfile uses Python 3.14-slim.

## Gotchas

- `send_message` and `schedule_message_delayed` are **disabled** (print only). `send_image` is active.
- `# %%` cell markers throughout — files are developed with VS Code interactive windows
- `test.py` at root is an unrelated PuLP experiment, not a project test
- `test_agent.py` is a manual interactive CLI client, not an automated test suite
- `Appointment_tool.py` contains stale plain-function definitions; the canonical tool implementations are in the individual `*_tool.py` files
