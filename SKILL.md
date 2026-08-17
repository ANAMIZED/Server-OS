---
name: server-os
description: >-
  Autonomous Agentic Operating System — agents as first-class processes with
  cost control, governance, observability, MCP, SDK, CLI, and skills. Fail-closed.
  Use when building or operating agent runtimes that need budgets, capabilities,
  and verifiable end-to-end checks.
license: Apache-2.0
metadata:
  author: ANAMIZED
  repository: https://github.com/ANAMIZED/server-os
  version: "0.1.0"
  mcp: true
---

# Server OS Skill

## When to use

- Run agents as processes with cost and governance
- Need MCP + SDK + CLI surfaces on one runtime
- Require fail-closed, offline-verifiable agent infrastructure

## Run & verify

```bash
docker compose up --build
bash scripts/verify.sh
```

MCP entry: `server-os-mcp`

## Principles

1. Least privilege by construction
2. Cost is first-class
3. Observable by default
4. Fail closed
5. Deployable with zero tribal knowledge
