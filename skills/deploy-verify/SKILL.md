---
name: deploy-verify
description: Deploy Server OS and run the official end-to-end verification suite.
version: 0.1.0
license: Apache-2.0
tags: [server-os, deploy, verify, docker]
---

# Deploy & Verify Skill (Server OS)

## Workflow
1. `docker compose up --build`
2. `curl -sf http://localhost:8080/health`
3. `bash scripts/verify.sh`
4. Expect ALL CHECKS PASSED

## Rules
- The verify script is the acceptance criterion
- Prefer mock LLM mode for CI and offline verification
