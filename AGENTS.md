# AGENTS.md — Server OS

This file is the contract for any AI coding agent working on this repository.

## What this project is

Server OS is an Autonomous Agentic Operating System: a runtime and control plane that treats AI agents as first-class processes with scheduling, memory, capabilities, cost accounting, governance, observability, and x402 micropayments.

A senior engineer with only the source code and README.md must be able to deploy it, use every feature, and verify end-to-end via `scripts/verify.sh`.

## How to run & verify

```bash
docker compose up --build
bash scripts/verify.sh
```

Unit tests: `pytest -q`

WebMCP page: `web/server-os.html` (read-first tools; `create_agent` confirms). See `docs/WEBMCP.md`.

## Hard rules for agents

1. Never break the verify contract.
2. Fail closed.
3. Capabilities only — no ambient authority.
4. Cost is first-class — meter before every LLM call.
5. Keep the mock LLM deterministic.
6. Do not add external network calls to the default/mock path.
7. Prefer small, focused changes. Update README.md and AGENTS.md when public surfaces change.
8. Do not expose `run_task` on WebMCP.

## Surfaces that must stay working

REST API, CLI, MCP Server, SDK, Skills, verify.sh, WebMCP page layer.
