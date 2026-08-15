"""Core domain models for Server OS."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Capability(str, Enum):
    WEB_SEARCH = "web_search"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    CODE_EXEC = "code_exec"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    PAYMENT = "payment"
    HTTP = "http"


class AgentCreate(BaseModel):
    name: str
    intent: str
    budget_usd: float = 1.0
    model: str = "mock-gpt"
    capabilities: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentProcess(BaseModel):
    id: str = Field(default_factory=lambda: new_id("agt_"))
    name: str
    intent: str
    status: AgentStatus = AgentStatus.IDLE
    budget_usd: float
    spent_usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    model: str
    capabilities: list[str] = Field(default_factory=list)
    memory: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def remaining_budget(self) -> float:
        return max(0.0, self.budget_usd - self.spent_usd)


class Task(BaseModel):
    id: str = Field(default_factory=lambda: new_id("tsk_"))
    agent_id: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    steps: list[dict[str, Any]] = Field(default_factory=list)
    result: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    spent_usd: float = 0.0


class TraceEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("tr_"))
    agent_id: str
    task_id: str | None = None
    kind: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)


class AuditRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("aud_"))
    agent_id: str | None = None
    task_id: str | None = None
    decision: str
    reason: str
    action: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)


class CostEntry(BaseModel):
    id: str = Field(default_factory=lambda: new_id("cost_"))
    agent_id: str
    task_id: str | None = None
    model: str
    tokens_in: int
    tokens_out: int
    usd: float
    timestamp: datetime = Field(default_factory=utcnow)


class WorkflowCreate(BaseModel):
    name: str
    agents: list[str]
    goal: str
    budget_usd: float = 2.0


class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: new_id("wf_"))
    name: str
    goal: str
    agent_ids: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
