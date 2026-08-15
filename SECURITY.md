# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Report responsibly via a private GitHub security advisory.

Include description, reproduction steps, and impact (capability bypass, budget bypass, sandbox escape).

## Security model

- Agents receive capabilities, never ambient authority
- Policy engine is fail-closed
- High-risk tools require explicit intent language
- Default path is offline mock LLM
- File tools sandboxed under data directory
