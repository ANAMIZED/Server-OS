"""Cost controller — first-class resource accounting for tokens and dollars."""

from __future__ import annotations

from typing import Any

from server_os.kernel.models import CostEntry, new_id

MODEL_PRICES: dict[str, dict[str, float]] = {
    "mock-gpt": {"in": 0.10, "out": 0.40},
    "gpt-4o-mini": {"in": 0.15, "out": 0.60},
    "gpt-4o": {"in": 2.50, "out": 10.00},
    "default": {"in": 1.00, "out": 3.00},
}


class CostController:
    def __init__(self) -> None:
        self.ledger: list[CostEntry] = []

    def estimate(self, model: str, tokens_in: int, tokens_out: int) -> float:
        prices = MODEL_PRICES.get(model, MODEL_PRICES["default"])
        return (tokens_in / 1_000_000) * prices["in"] + (tokens_out / 1_000_000) * prices["out"]

    def charge(self, agent_id: str, model: str, tokens_in: int, tokens_out: int, task_id: str | None = None) -> CostEntry:
        usd = self.estimate(model, tokens_in, tokens_out)
        entry = CostEntry(id=new_id("cost_"), agent_id=agent_id, task_id=task_id, model=model, tokens_in=tokens_in, tokens_out=tokens_out, usd=usd)
        self.ledger.append(entry)
        return entry

    def total_for_agent(self, agent_id: str) -> float:
        return sum(e.usd for e in self.ledger if e.agent_id == agent_id)

    def can_afford(self, remaining_budget: float, model: str, tokens_in: int, tokens_out: int) -> bool:
        return self.estimate(model, tokens_in, tokens_out) <= remaining_budget + 1e-9

    def dump(self) -> list[dict[str, Any]]:
        return [e.model_dump(mode="json") for e in self.ledger]
