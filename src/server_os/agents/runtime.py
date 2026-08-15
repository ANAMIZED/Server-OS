"""Agent runtime — the process that plans and executes steps under OS control."""

from __future__ import annotations

import json
from typing import Any

from server_os.cost.controller import CostController
from server_os.governance.policy import PolicyEngine
from server_os.kernel.capabilities import CapabilityRegistry
from server_os.kernel.memory import MemoryStore
from server_os.kernel.models import AgentProcess, AgentStatus, Task, TaskStatus
from server_os.observability.tracer import Tracer
from server_os.config import settings


class MockLLM:
    """Deterministic offline LLM for verification and demos."""

    def complete(self, system: str, messages: list[dict[str, str]], tools: list[str]) -> dict[str, Any]:
        last = messages[-1]["content"].lower() if messages else ""
        if "capital of france" in last or "capital of france" in system.lower():
            if "web_search" in tools:
                return {"type": "tool_call", "tool": "web_search", "args": {"query": "capital of France"}, "tokens_in": 120, "tokens_out": 40}
            return {"type": "final", "content": "The capital of France is Paris.", "tokens_in": 80, "tokens_out": 20}
        if "after search" in last or "results" in last:
            return {"type": "final", "content": "Based on the search results, the capital of France is Paris. Sources: Wikipedia and France.gov.", "tokens_in": 200, "tokens_out": 50}
        if "payment" in last or "pay for" in last:
            if "payment" in tools:
                return {"type": "tool_call", "tool": "payment", "args": {"amount_usd": 0.01, "recipient": "tool-provider", "memo": "premium data"}, "tokens_in": 100, "tokens_out": 30}
        if "write memory" in last or "remember" in last:
            if "memory_write" in tools:
                return {"type": "tool_call", "tool": "memory_write", "args": {"namespace": "default", "key": "note", "value": "demo note from agent"}, "tokens_in": 90, "tokens_out": 25}
        if "forbidden" in last or "code_exec" in last:
            if "code_exec" in tools:
                return {"type": "tool_call", "tool": "code_exec", "args": {"code": "1+1"}, "tokens_in": 60, "tokens_out": 20}
        return {"type": "final", "content": f"Acknowledged goal. Available tools: {tools}. (mock response)", "tokens_in": 100, "tokens_out": 40}


class AgentRuntime:
    def __init__(self, registry: CapabilityRegistry, memory: MemoryStore, cost: CostController, policy: PolicyEngine, tracer: Tracer) -> None:
        self.registry = registry
        self.memory = memory
        self.cost = cost
        self.policy = policy
        self.tracer = tracer
        self.llm = MockLLM()

    async def run_task(self, agent: AgentProcess, task: Task) -> Task:
        agent.status = AgentStatus.RUNNING
        task.status = TaskStatus.RUNNING
        self.tracer.record(agent.id, "system", f"Task started: {task.goal}", task.id)

        messages = [{"role": "user", "content": task.goal}]
        system = (
            f"You are agent '{agent.name}'. Intent: {agent.intent}. "
            f"Budget remaining: ${agent.remaining_budget():.4f}. "
            f"Only use tools you have capabilities for: {agent.capabilities}."
        )

        for step_idx in range(settings.max_agent_steps):
            est = self.cost.estimate(agent.model, 200, 100)
            ok, reason = self.policy.check_budget(agent, est, task.id)
            if not ok:
                task.status = TaskStatus.BLOCKED
                task.error = reason
                self.tracer.inc("policy_denials")
                self.tracer.record(agent.id, "policy", reason, task.id)
                break

            resp = self.llm.complete(system, messages, agent.capabilities)
            tokens_in = resp.get("tokens_in", 100)
            tokens_out = resp.get("tokens_out", 40)

            entry = self.cost.charge(agent.id, agent.model, tokens_in, tokens_out, task.id)
            agent.spent_usd += entry.usd
            agent.tokens_in += tokens_in
            agent.tokens_out += tokens_out
            task.spent_usd += entry.usd
            self.tracer.inc("llm_calls")
            self.tracer.inc("total_spend_usd", entry.usd)
            self.tracer.record(agent.id, "llm_call", f"LLM step {step_idx}", task.id, {"tokens_in": tokens_in, "tokens_out": tokens_out, "usd": entry.usd})

            if resp["type"] == "final":
                task.result = resp["content"]
                task.status = TaskStatus.COMPLETED
                task.steps.append({"type": "final", "content": resp["content"]})
                self.tracer.inc("tasks_completed")
                self.tracer.record(agent.id, "system", "Task completed", task.id, {"result": resp["content"]})
                break

            if resp["type"] == "tool_call":
                tool_name = resp["tool"]
                args = resp.get("args", {})
                allowed, reason = self.policy.check_tool(agent, tool_name, task.id, args)
                if not allowed:
                    task.steps.append({"type": "policy_deny", "tool": tool_name, "reason": reason})
                    self.tracer.inc("policy_denials")
                    self.tracer.record(agent.id, "policy", reason, task.id)
                    messages.append({"role": "assistant", "content": f"Tool denied: {reason}"})
                    messages.append({"role": "user", "content": "Continue without that tool or finish."})
                    continue

                handler = self.registry.get(tool_name)
                if handler is None:
                    messages.append({"role": "assistant", "content": f"Unknown tool {tool_name}"})
                    continue

                try:
                    result = handler(**args) if isinstance(args, dict) else handler(args)
                except Exception as e:
                    result = {"error": str(e)}

                self.tracer.inc("tool_calls")
                self.tracer.record(agent.id, "tool_call", f"Called {tool_name}", task.id, {"args": args, "result": result})
                task.steps.append({"type": "tool_call", "tool": tool_name, "args": args, "result": result})
                messages.append({"role": "assistant", "content": f"Tool {tool_name} => {json.dumps(result)}"})
                messages.append({"role": "user", "content": "After search / tool result, produce the final answer."})
                continue

            task.result = str(resp)
            task.status = TaskStatus.COMPLETED
            break
        else:
            task.status = TaskStatus.FAILED
            task.error = "max steps exceeded"
            self.tracer.inc("tasks_failed")

        agent.status = AgentStatus.IDLE if task.status == TaskStatus.COMPLETED else AgentStatus.FAILED
        agent.updated_at = task.updated_at
        return task
