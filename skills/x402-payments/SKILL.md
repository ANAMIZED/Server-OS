---
name: x402-payments
description: Work with Server OS micropayment (x402) capabilities for agents.
version: 0.1.0
license: Apache-2.0
tags: [server-os, x402, payments]
---

# x402 Payments Skill (Server OS)

## Workflow
1. Create agent with payment intent language and `payment` capability
2. Give a task that requires payment
3. Inspect traces and audit

## Rules
- `payment` is high-risk; requires explicit intent about pay/payment/spend
- Default is deterministic mock for offline verification
