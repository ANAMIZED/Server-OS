"""Policy engine — fail-closed governance for agent actions."""

from __future__ import annotations

from typing import Any

from server_os.kernel.models import AgentProcess, AuditRecord, new_id


class PolicyEngine:
    """Simple but strict policy engine.

    Rules enforced:
    - Tool must be in the agent's capability list
    - Action must not exceed remaining budget (checked by caller via CostController)
    - Certain high-risk tools require explicit intent language
    """

    HIGH_RISK = {"code_exec", "file_write", "payment", "http"}

    def __init__(self) -> None:
        self.audit_log: list[AuditRecord] = []

    def check_tool(
        self,
        agent: AgentProcess,
        tool_name: str,
        task_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        """Return (allowed, reason). Always records an audit entry."""
        allowed = tool_name in agent.capabilities
        reason = (
            "capability granted"
            if allowed
            else f"tool '{tool_name}' not in agent capabilities {agent.capabilities}"
        )

        if allowed and tool_name in self.HIGH_RISK:
            intent_l = agent.intent.lower()
            if tool_name == "code_exec" and "code" not in intent_l and "execute" not in intent_l:
                allowed = False
                reason = "high-risk tool 'code_exec' requires explicit intent language about code/execution"
            elif tool_name == "payment" and "pay" not in intent_l and "payment" not in intent_l and "spend" not in intent_l:
                allowed = False
                reason = "high-risk tool 'payment' requires explicit intent language about payment/spend"

        record = AuditRecord(
            id=new_id("aud_"),
            agent_id=agent.id,
            task_id=task_id,
            decision="allow" if allowed else "deny",
            reason=reason,
            action=f"tool:{tool_name}",
            data=extra or {},
        )
        self.audit_log.append(record)
        return allowed, reason

    def check_budget(
        self,
        agent: AgentProcess,
        estimated_usd: float,
        task_id: str | None = None,
    ) -> tuple[bool, str]:
        remaining = agent.remaining_budget()
        allowed = estimated_usd <= remaining + 1e-9
        reason = (
            f"budget ok (need ${estimated_usd:.6f}, remaining ${remaining:.6f})"
            if allowed
            else f"budget exceeded (need ${estimated_usd:.6f}, remaining ${remaining:.6f})"
        )
        record = AuditRecord(
            id=new_id("aud_"),
            agent_id=agent.id,
            task_id=task_id,
            decision="allow" if allowed else "deny",
            reason=reason,
            action="budget_check",
            data={"estimated_usd": estimated_usd, "remaining": remaining},
        )
        self.audit_log.append(record)
        return allowed, reason

    def dump(self) -> list[dict[str, Any]]:
        return [r.model_dump(mode="json") for r in self.audit_log]
