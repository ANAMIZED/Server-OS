"""Observability: traces, simple metrics, structured logging helpers."""

from __future__ import annotations

from typing import Any

import structlog

from server_os.kernel.models import TraceEvent, new_id

log = structlog.get_logger()


class Tracer:
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []
        self.metrics: dict[str, float] = {
            "agents_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "policy_denials": 0,
            "tool_calls": 0,
            "llm_calls": 0,
            "total_spend_usd": 0.0,
        }

    def record(
        self,
        agent_id: str,
        kind: str,
        message: str,
        task_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> TraceEvent:
        event = TraceEvent(
            id=new_id("tr_"),
            agent_id=agent_id,
            task_id=task_id,
            kind=kind,
            message=message,
            data=data or {},
        )
        self.events.append(event)
        log.info(message, agent_id=agent_id, task_id=task_id, kind=kind, **(data or {}))
        return event

    def inc(self, key: str, amount: float = 1.0) -> None:
        self.metrics[key] = self.metrics.get(key, 0.0) + amount

    def for_agent(self, agent_id: str) -> list[dict[str, Any]]:
        return [e.model_dump(mode="json") for e in self.events if e.agent_id == agent_id]

    def dump_metrics(self) -> dict[str, float]:
        return dict(self.metrics)
