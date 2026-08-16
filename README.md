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

Single-file operator console — offline mock provider, policy, budgets, graph, terminal, **12 golden evals**.

**Canonical file (full engine):** `web/server-os.html` (~82 KB)

```bash
# from a complete local checkout of this repo
python -m http.server 8088 --directory web
# open http://127.0.0.1:8088/server-os.html
```

Or Chrome → **File → Open File…** → select `web/server-os.html`.

| Surface | Notes |
|---------|--------|
| Kernel + queue + triggers | `sos up` / `sos down` |
| 7 agent manifests | assistant, researcher, ops, coder, triage, thrifty, cartographer |
| Policy + grants + audit | fail-closed tools, shell approval, HTTP deny-by-default |
| Cost ledger + kill switch | living proof via `thrifty` |
| Knowledge graph | cartographer gardens orphan notes |
| Terminal | CLI-parity verbs (`sos run`, `sos ledger`, `sos eval`, …) |
| **Golden evals** | **12 cases** — tools, policy, approvals, autonomy, budget kill |

**Acceptance (web):** open the file → **OS** tab → **Golden evals → run** → expect **12/12 passed**.

The HTML engine is **DOM-free below the UI** so the eval suite exercises the same path as interactive use. Python Server OS remains the production deployment target.

> Note: if `web/server-os.html` on the remote shows only a short instruction page, use a full local copy of the control plane (the complete single-file engine). Payload limits on the GitHub Contents API can block uploading the full ~82 KB blob in one shot; the README contract still holds for any complete checkout that includes the full file.

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

**Web parity check (manual, ~30s):** open full `web/server-os.html` → run **Golden evals** → 12/12.

## Design principles

1. Least privilege by construction (capabilities from intent)
2. Cost is a first-class resource
3. Observable by default
4. Fail closed
5. Deployable with zero tribal knowledge

## License

Apache-2.0
