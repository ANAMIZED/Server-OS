# Contributing to Server OS

## The contract

1. `bash scripts/verify.sh` must pass
2. Policy remains fail-closed
3. Cost is first-class (metered before LLM calls)
4. Capabilities stay least-privilege
5. Mock LLM path stays deterministic and offline-capable

Read `AGENTS.md` before changing code.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
bash scripts/verify.sh
```

## PRs

- Small, focused changes
- Describe why / what / how verified
- Update README, AGENTS.md, or skills when public surfaces change
