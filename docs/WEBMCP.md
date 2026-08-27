# WebMCP — Server OS

Page tools on `web/server-os.html` are a read-first front door.
Live REST (`/metrics`, `/v1/agents`, `/v1/cost/ledger`, `/v1/audit`) is used when this page is served from the FastAPI app.
Otherwise the page uses an in-memory mock and says so.

`create_agent` requires confirmation. `run_task` is intentionally not exposed on WebMCP (too easy to spend).
MCP + REST remain the system of record.
