"""In-memory + disk-backed process table / OS state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from server_os.config import settings
from server_os.kernel.models import AgentProcess, Task, Workflow, utcnow


class ProcessTable:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.root = (data_dir or settings.data_dir) / "state"
        self.root.mkdir(parents=True, exist_ok=True)
        self.agents: dict[str, AgentProcess] = {}
        self.tasks: dict[str, Task] = {}
        self.workflows: dict[str, Workflow] = {}
        self._load()

    def _path(self, name: str) -> Path:
        return self.root / f"{name}.json"

    def _load(self) -> None:
        for name, cls, bucket in [
            ("agents", AgentProcess, self.agents),
            ("tasks", Task, self.tasks),
            ("workflows", Workflow, self.workflows),
        ]:
            p = self._path(name)
            if p.exists():
                raw = json.loads(p.read_text())
                for item in raw:
                    obj = cls.model_validate(item)
                    bucket[obj.id] = obj

    def save(self) -> None:
        self._path("agents").write_text(
            json.dumps([a.model_dump(mode="json") for a in self.agents.values()], indent=2)
        )
        self._path("tasks").write_text(
            json.dumps([t.model_dump(mode="json") for t in self.tasks.values()], indent=2)
        )
        self._path("workflows").write_text(
            json.dumps([w.model_dump(mode="json") for w in self.workflows.values()], indent=2)
        )

    def create_agent(self, agent: AgentProcess) -> AgentProcess:
        self.agents[agent.id] = agent
        self.save()
        return agent

    def get_agent(self, agent_id: str) -> AgentProcess | None:
        return self.agents.get(agent_id)

    def list_agents(self) -> list[AgentProcess]:
        return list(self.agents.values())

    def create_task(self, task: Task) -> Task:
        self.tasks[task.id] = task
        self.save()
        return task

    def update_task(self, task: Task) -> None:
        task.updated_at = utcnow()
        self.tasks[task.id] = task
        if task.agent_id in self.agents:
            self.agents[task.agent_id].updated_at = utcnow()
        self.save()

    def create_workflow(self, wf: Workflow) -> Workflow:
        self.workflows[wf.id] = wf
        self.save()
        return wf
