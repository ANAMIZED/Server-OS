---
name: discovery-distribution
description: Run the discovery → synthesis → build → verify → elite-package → distribute loop to turn domain insight into a multi-surface, verified GitHub product. Use when productizing an idea, packaging agentic systems, or raising a repo to elite open-source standards before launch.
version: 0.1.0
license: Apache-2.0
tags: [discovery, distribution, productize, packaging, agents, skills, github]
---

# Discovery & Distribution Skill

## When to use

- User has a domain insight and wants a shippable product, not a prototype
- Building multi-surface systems (API, CLI, SDK, MCP, skills)
- Need elite packaging before public launch
- Dogfooding: creating or updating this package itself

## Process (six stages)

1. **Discovery** — demand, gaps, standards
2. **Synthesis** — product identity, surfaces, acceptance contract
3. **Build** — kernel then surfaces; every surface has an entrypoint
4. **Verify** — one script; stranger can run it; offline/mock preferred
5. **Elite package** — LICENSE, README, SECURITY, CONTRIBUTING, CoC, CHANGELOG, CI, templates
6. **Distribute** — public repo + install this skill into consumer trees

Full detail: https://github.com/ANAMIZED/discovery-distribution (PLAYBOOK.md, AGENTS.md).

## Hard rules

- Fail closed on distribute: no public push without LICENSE + README + verify green
- Own repo is source of truth; consumer repos get a local copy of this skill
- Prefer one acceptance command over tribal knowledge
- When building the package itself, dogfood: the repo must pass its own `scripts/verify.sh`

## Outputs checklist

- [ ] Discovery notes
- [ ] Synthesis (vision + surfaces + acceptance)
- [ ] Build complete for declared surfaces
- [ ] `scripts/verify.sh` green
- [ ] Elite community + CI files
- [ ] Public GitHub repo
- [ ] Skill present for agents in consumer trees
