# Glama admin — Server-OS

If Glama has no listing yet, Add Server for github.com/ANAMIZED/Server-OS then claim via glama.json maintainers: ANAMIZED.

Glama generates FROM debian:trixie-slim.

1. Sync Server. Pinned SHA empty.
2. Python version: 3.12
3. Build steps:

```json
["apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv && python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir ."]
```

4. CMD arguments:

```json
["/opt/venv/bin/python", "-m", "server_os.mcp"]
```

Fallback: `["sh", "scripts/glama-stdio.sh"]`

5. Env schema: `{\"type\":\"object\",\"properties\":{},\"required\":[]}`
6. Placeholders: `{}`
Do not CMD server-os-api.
