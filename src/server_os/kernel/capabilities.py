"""Capability-based access control.

Agents never receive ambient authority. Every tool or resource access
must be covered by a capability that was synthesized from the agent's
declared intent + active policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from server_os.kernel.models import Capability


@dataclass
class CapabilityToken:
    """Opaque capability token held by an agent process."""

    name: str
    resource: str  # e.g. "tool:web_search" or "ns:shared.research"
    actions: set[str] = field(default_factory=lambda: {"invoke"})
    metadata: dict[str, Any] = field(default_factory=dict)

    def allows(self, action: str = "invoke") -> bool:
        return action in self.actions or "*" in self.actions


class CapabilityRegistry:
    """Maps capability names to concrete tools / resources."""

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}
        self._descriptions: dict[str, str] = {}

    def register(self, name: str, handler: Any, description: str = "") -> None:
        self._tools[name] = handler
        self._descriptions[name] = description or getattr(handler, "__doc__", "") or name

    def get(self, name: str) -> Any | None:
        return self._tools.get(name)

    def describe(self, name: str) -> str:
        return self._descriptions.get(name, name)

    def list_available(self) -> list[str]:
        return sorted(self._tools.keys())

    def synthesize(self, requested: list[str]) -> list[CapabilityToken]:
        """Create capability tokens only for registered tools the agent asked for."""
        tokens: list[CapabilityToken] = []
        for name in requested:
            if name in self._tools:
                tokens.append(
                    CapabilityToken(
                        name=name,
                        resource=f"tool:{name}",
                        actions={"invoke"},
                    )
                )
        return tokens
