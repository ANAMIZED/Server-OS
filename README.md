# Server OS

[![CI](https://github.com/ANAMIZED/server-os/actions/workflows/ci.yml/badge.svg)](https://github.com/ANAMIZED/server-os/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-server-purple.svg)](src/server_os/mcp/)

**Autonomous Agentic Operating System**

Server OS is a production-oriented runtime and control plane for fleets of AI agents.
It treats agents as first-class processes with OS-like primitives: scheduling, memory, capabilities, isolation, resource accounting, governance, and observability.

A senior engineer who has never seen this repository can, using **only** the source code and this `README.md`:

1. Deploy the entire system (single command)
2. Exercise every major feature
3. Verify end-to-end correctness via automated checks

No prior context, design docs, or tribal knowledge required.

## Quick Start

```bash
docker compose up --build
# another terminal
bash scripts/verify.sh
```

- API: http://localhost:8080
- Dashboard: http://localhost:8080/dashboard
- OpenAPI: http://localhost:8080/docs

Default mode is **offline mock LLM** (deterministic, free). Set `SERVER_OS_LLM_MODE=openai` + `OPENAI_API_KEY` for real models.

## Web control plane (zero install)

Open the single-file operator console — no build, no backend, no API keys:

**File:** [`web/server-os.html`](web/server-os.html)

```bash
# from repo root
python -m http.server 8088 --directory web
# then open http://127.0.0.1:8088/server-os.html
```

Or open `web/server-os.html` directly in Chrome (**File → Open File**).

| What you get | Notes |
|--------------|--------|
| Kernel + queue + triggers | `sos up` / `sos down` |
| 7 agent manifests | assistant, researcher, ops, coder, triage, thrifty, cartographer |
| Policy + grants + audit | fail-closed tools, shell approval, HTTP deny-by-default |
| Cost ledger + kill switch | living proof via `thrifty` + expensive mock model |
| Knowledge graph | cartographer gardens orphan notes |
| In-browser terminal | same verbs as the Python CLI (`sos run`, `sos ledger`, …) |
| **Golden evals** | **12 cases** — tools, policy, approvals, autonomy, budget kill |

**Acceptance (web):** open the file → **OS** tab → **Golden evals → run** → expect **12/12 passed**.

This HTML engine is intentionally **DOM-free below the UI** so the same runtime path is exercised by the eval suite. It is the portable reference for the Server OS mental model. The Python deployment remains the production target (isolation, real models, multi-tenant ops).

Preview without cloning:  
https://htmlpreview.github.io/?https://raw.githubusercontent.com/ANAMIZED/server-os/main/web/server-os.html

## Surfaces

| Surface | Entry |
|---------|-------|
| **Web control plane** | `web/server-os.html` (offline, self-verifying) |
| REST API | `python -c "from server_os.main import run; run()"` |
| CLI | `server-os status` / `server-os agents ...` |
| MCP Server | `server-os-mcp` |
| SDK | `from server_os.sdk import ServerOSClient` |
| Skills | `skills/*/SKILL.md` |
| AGENTS.md | Coding-agent contract at repo root |

## Verify contract

```bash
bash scripts/verify.sh
```

Covers API, cost, governance, multi-agent workflows, SDK, CLI, MCP, skills, and AGENTS.md. **16 checks. All must pass.**

**Web parity check (manual, ~30s):** open `web/server-os.html` → run **Golden evals** → 12/12.

## Design principles

1. Least privilege by construction (capabilities from intent)
2. Cost is a first-class resource
3. Observable by default
4. Fail closed
5. Deployable with zero tribal knowledge

## License

Apache-2.0
