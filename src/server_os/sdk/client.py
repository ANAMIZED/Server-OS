"""Server OS Python SDK — thin typed client over the REST API."""

from __future__ import annotations

from typing import Any

import httpx

from server_os.kernel.models import AgentCreate, AgentProcess, Task, WorkflowCreate


class ServerOSClient:
    """Synchronous client for Server OS."""

    def __init__(self, base_url: str = "http://localhost:8080", timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ServerOSClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def health(self) -> dict[str, Any]:
        r = self._client.get("/health")
        r.raise_for_status()
        return r.json()

    def metrics(self) -> dict[str, float]:
        r = self._client.get("/metrics")
        r.raise_for_status()
        return r.json()

    def create_agent(self, body: AgentCreate | dict[str, Any]) -> AgentProcess:
        payload = body.model_dump() if isinstance(body, AgentCreate) else body
        r = self._client.post("/v1/agents", json=payload)
        r.raise_for_status()
        return AgentProcess.model_validate(r.json())

    def list_agents(self) -> list[AgentProcess]:
        r = self._client.get("/v1/agents")
        r.raise_for_status()
        return [AgentProcess.model_validate(a) for a in r.json()]

    def get_agent(self, agent_id: str) -> AgentProcess:
        r = self._client.get(f"/v1/agents/{agent_id}")
        r.raise_for_status()
        return AgentProcess.model_validate(r.json())

    def run_task(self, agent_id: str, goal: str) -> Task:
        r = self._client.post(f"/v1/agents/{agent_id}/tasks", json={"goal": goal})
        r.raise_for_status()
        return Task.model_validate(r.json())

    def agent_traces(self, agent_id: str) -> list[dict[str, Any]]:
        r = self._client.get(f"/v1/agents/{agent_id}/traces")
        r.raise_for_status()
        return r.json()

    def cost_ledger(self) -> list[dict[str, Any]]:
        r = self._client.get("/v1/cost/ledger")
        r.raise_for_status()
        return r.json()

    def audit_log(self) -> list[dict[str, Any]]:
        r = self._client.get("/v1/audit")
        r.raise_for_status()
        return r.json()

    def create_workflow(self, body: WorkflowCreate | dict[str, Any]) -> dict[str, Any]:
        payload = body.model_dump() if isinstance(body, WorkflowCreate) else body
        r = self._client.post("/v1/workflows", json=payload)
        r.raise_for_status()
        return r.json()
