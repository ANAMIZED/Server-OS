# Server OS

[![CI](https://github.com/ANAMIZED/server-os/actions/workflows/ci.yml/badge.svg)](https://github.com/ANAMIZED/server-os/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-server-purple.svg)](src/server_os/mcp/)

**Autonomous Agentic Operating System** — agents as first-class processes with cost control, governance, observability, MCP, SDK, CLI, and skills. Fail-closed. Verified end-to-end.

A senior engineer who has never seen this repository can, using **only** the source code and this `README.md`:

1. Deploy the entire system (single command)
2. Exercise every major feature
3. Verify end-to-end correctness via automated checks

No prior context or tribal knowledge required.

**[Support Agentic OS Kernels ($99)](https://buy.stripe.com/test_3cI6oH74HgS4fFDe27bAs02)** · **[Public Goods Support](https://donate.stripe.com/test_28E8wP60D9pC9hf1flbAs00)**

*Related:* [OpenGOS](https://github.com/ANAMIZED/OpenGOS) · [LRSI](https://github.com/ANAMIZED/LRSI) · [agenticarb](https://github.com/ANAMIZED/agenticarb) · [x402-cloudflare-starter](https://github.com/ANAMIZED/x402-cloudflare-starter)

---

## 🚀 Web Control Plane (Hero Demo — Zero Install)

**Canonical file:** [`web/server-os.html`](web/server-os.html) (~82 KB)

Open locally:

```bash
python -m http.server 8088 --directory web
# http://127.0.0.1:8088/server-os.html
```

Or Chrome → **File → Open File…** → `web/server-os.html`.

**Acceptance:** open the file → **OS** tab → **Golden evals → run** → **12/12 passed**.

Offline mock provider, policy, budgets, graph, terminal, and 12 golden evals. The HTML engine is DOM-free below the UI so the eval suite exercises the same path as interactive use.

---

## Quick Start (Production Runtime)

```bash
docker compose up --build
# another terminal
bash scripts/verify.sh
```

- API: http://localhost:8080
- Dashboard: http://localhost:8080/dashboard
- OpenAPI: http://localhost:8080/docs

Default mode is **offline mock LLM** (deterministic, free). Set `SERVER_OS_LLM_MODE=openai` + `OPENAI_API_KEY` for real models.

---

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
