#!/bin/sh
set -eu
cd "${APP_DIR:-/app}"
export PYTHONUNBUFFERED=1 SERVER_OS_LLM_MODE="${SERVER_OS_LLM_MODE:-mock}"
if [ -x /opt/venv/bin/python ]; then
  exec /opt/venv/bin/python -m server_os.mcp
fi
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python
if "$PY" -c "import server_os.mcp" 2>/dev/null; then
  exec "$PY" -m server_os.mcp
fi
VENV=/tmp/server-os-venv
[ -x "$VENV/bin/python" ] || { "$PY" -m venv "$VENV" && "$VENV/bin/pip" install --no-cache-dir .; }
exec "$VENV/bin/python" -m server_os.mcp
