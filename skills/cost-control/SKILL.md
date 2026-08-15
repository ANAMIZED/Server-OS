---
name: cost-control
description: Enforce and inspect token/dollar budgets for Server OS agents. Use when the user asks about agent spend, budgets, cost ledgers, or wants to prevent runaway token usage.
version: 0.1.0
license: Apache-2.0
tags: [server-os, cost, budget, tokens]
---

# Cost Control Skill (Server OS)

## When to use
- Checking agent or fleet spend
- Setting or verifying budgets
- Investigating high token usage

## Workflow
1. List agents via API or MCP `list_agents`
2. Inspect cost ledger via `GET /v1/cost/ledger` or MCP `get_cost_ledger`
3. Always set explicit `budget_usd` at agent creation

## Rules
- Never create an agent without a budget
- Prefer cheaper models when quality allows
- Budget exhaustion is a hard stop
