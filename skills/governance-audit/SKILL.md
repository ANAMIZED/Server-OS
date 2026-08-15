---
name: governance-audit
description: Inspect Server OS policy decisions, capability grants, and the audit log.
version: 0.1.0
license: Apache-2.0
tags: [server-os, governance, policy, audit, security]
---

# Governance & Audit Skill (Server OS)

## When to use
- An agent action was blocked
- Reviewing allowed tools
- Compliance audit trail

## Workflow
1. Fetch audit log: `GET /v1/audit` or MCP `get_audit_log`
2. Look for `decision: "deny"` entries
3. Inspect agent intent and capabilities

## Rules
- Fail-closed: missing capability stops the action
- High-risk tools require explicit intent language
