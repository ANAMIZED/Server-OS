---
name: multi-agent-workflow
description: Create and run multi-agent workflows on Server OS.
version: 0.1.0
license: Apache-2.0
tags: [server-os, multi-agent, orchestration]
---

# Multi-Agent Workflow Skill (Server OS)

## Workflow
1. `POST /v1/workflows` or MCP `create_workflow` with name, agents roles, goal, budget
2. Server OS creates specialists and runs sequential tasks
3. Inspect results and per-agent spend

## Rules
- Each specialist inherits a slice of the workflow budget
- All agents remain under the same policy and observability regime
