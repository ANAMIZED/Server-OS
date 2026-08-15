"""Built-in tools available to agents (subject to capabilities)."""

from __future__ import annotations

import json
from typing import Any

from server_os.kernel.memory import MemoryStore


class BuiltinTools:
    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory

    def web_search(self, query: str) -> dict[str, Any]:
        """Mock web search — deterministic for verification."""
        known = {
            "capital of france": {
                "results": [
                    {"title": "Paris - Wikipedia", "snippet": "Paris is the capital and most populous city of France."},
                    {"title": "France.gov", "snippet": "The capital of France is Paris."},
                ]
            },
            "agentic operating system": {
                "results": [
                    {"title": "AgenticOS paper", "snippet": "Intent-oriented secure OS architecture for autonomous AI agents (2026)."},
                    {"title": "Make.com guide", "snippet": "An agentic OS coordinates multiple agents with memory, tools and oversight."},
                ]
            },
        }
        q = query.lower().strip()
        for key, val in known.items():
            if key in q:
                return {"query": query, "results": val["results"], "source": "mock"}
        return {
            "query": query,
            "results": [{"title": "Mock Result", "snippet": f"Simulated search result for: {query}"}],
            "source": "mock",
        }

    def memory_read(self, namespace: str, key: str) -> Any:
        return self.memory.get(namespace, key)

    def memory_write(self, namespace: str, key: str, value: Any) -> dict[str, str]:
        self.memory.set(namespace, key, value)
        return {"status": "ok", "namespace": namespace, "key": key}

    def code_exec(self, code: str) -> dict[str, Any]:
        """Extremely limited, sandboxed eval for demo only."""
        allowed_globals = {"__builtins__": {}}
        try:
            result = eval(code, allowed_globals, {})  # noqa: S307
            return {"ok": True, "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def file_read(self, path: str) -> dict[str, Any]:
        from pathlib import Path
        from server_os.config import settings

        base = settings.data_dir / "sandbox"
        base.mkdir(parents=True, exist_ok=True)
        target = (base / path).resolve()
        if not str(target).startswith(str(base.resolve())):
            return {"ok": False, "error": "path escapes sandbox"}
        if not target.exists():
            return {"ok": False, "error": "not found"}
        return {"ok": True, "content": target.read_text()[:4000]}

    def file_write(self, path: str, content: str) -> dict[str, Any]:
        from pathlib import Path
        from server_os.config import settings

        base = settings.data_dir / "sandbox"
        base.mkdir(parents=True, exist_ok=True)
        target = (base / path).resolve()
        if not str(target).startswith(str(base.resolve())):
            return {"ok": False, "error": "path escapes sandbox"}
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return {"ok": True, "path": str(path)}

    def payment(self, amount_usd: float, recipient: str, memo: str = "") -> dict[str, Any]:
        """Mock x402-style payment."""
        return {
            "ok": True,
            "protocol": "x402-mock",
            "amount_usd": amount_usd,
            "recipient": recipient,
            "memo": memo,
            "tx_id": f"mock_tx_{hash((amount_usd, recipient)) & 0xFFFFFFFF:08x}",
        }

    def http_get(self, url: str) -> dict[str, Any]:
        """Mock HTTP — can return 402 for premium URLs."""
        if "paywalled" in url or "premium" in url:
            return {
                "status": 402,
                "headers": {"PAYMENT-REQUIRED": "x402-mock;amount=0.01;asset=USDC"},
                "body": {"error": "payment required", "price_usd": 0.01},
            }
        return {"status": 200, "body": {"message": f"Mock response from {url}"}}


def register_builtins(registry, memory: MemoryStore) -> BuiltinTools:
    tools = BuiltinTools(memory)
    registry.register("web_search", tools.web_search, "Search the web (mock)")
    registry.register("memory_read", tools.memory_read, "Read from agent memory namespace")
    registry.register("memory_write", tools.memory_write, "Write to agent memory namespace")
    registry.register("code_exec", tools.code_exec, "Execute restricted Python expression")
    registry.register("file_read", tools.file_read, "Read file from sandbox")
    registry.register("file_write", tools.file_write, "Write file to sandbox")
    registry.register("payment", tools.payment, "Make a micropayment (x402 mock)")
    registry.register("http", tools.http_get, "HTTP GET (mock, can return 402)")
    return tools
