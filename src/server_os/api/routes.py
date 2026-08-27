"""REST API routes for Server OS."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from server_os.kernel.models import (
    AgentCreate,
    AgentProcess,
    Task,
    TaskStatus,
    Workflow,
    WorkflowCreate,
)

router = APIRouter()


def get_os(request: Request):
    return request.app.state.os


@router.get("/health")
async def health():
    return {"status": "ok", "service": "server-os", "version": "0.1.0"}


@router.get("/metrics")
async def metrics(request: Request):
    os = get_os(request)
    return os.tracer.dump_metrics()


@router.post("/v1/agents", response_model=AgentProcess)
async def create_agent(body: AgentCreate, request: Request):
    os = get_os(request)
    agent = AgentProcess(
        name=body.name,
        intent=body.intent,
        budget_usd=body.budget_usd,
        model=body.model,
        capabilities=body.capabilities,
        metadata=body.metadata,
    )
    tokens = os.registry.synthesize(body.capabilities)
    agent.capabilities = [t.name for t in tokens]
    os.store.create_agent(agent)
    os.tracer.inc("agents_created")
    os.tracer.record(agent.id, "system", f"Agent created: {agent.name}", data={"intent": agent.intent})
    return agent


@router.get("/v1/agents")
async def list_agents(request: Request):
    os = get_os(request)
    return [a.model_dump(mode="json") for a in os.store.list_agents()]


@router.get("/v1/agents/{agent_id}")
async def get_agent(agent_id: str, request: Request):
    os = get_os(request)
    agent = os.store.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, "agent not found")
    return agent.model_dump(mode="json")


@router.post("/v1/agents/{agent_id}/tasks")
async def create_and_run_task(agent_id: str, body: dict[str, Any], request: Request):
    os = get_os(request)
    agent = os.store.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, "agent not found")
    goal = body.get("goal")
    if not goal:
        raise HTTPException(400, "goal required")
    task = Task(agent_id=agent_id, goal=goal)
    os.store.create_task(task)
    task = await os.runtime.run_task(agent, task)
    os.store.update_task(task)
    os.store.save()
    return task.model_dump(mode="json")


@router.get("/v1/agents/{agent_id}/traces")
async def agent_traces(agent_id: str, request: Request):
    os = get_os(request)
    return os.tracer.for_agent(agent_id)


@router.get("/v1/cost/ledger")
async def cost_ledger(request: Request):
    os = get_os(request)
    return os.cost.dump()


@router.get("/v1/audit")
async def audit_log(request: Request):
    os = get_os(request)
    return os.policy.dump()


@router.post("/v1/workflows")
async def create_workflow(body: WorkflowCreate, request: Request):
    os = get_os(request)
    agent_ids = []
    roles = body.agents or ["planner", "worker"]
    for role in roles:
        agent = AgentProcess(
            name=f"{body.name}-{role}",
            intent=f"Role: {role}. Overall goal: {body.goal}. Stay within budget and use only granted tools.",
            budget_usd=body.budget_usd / max(len(roles), 1),
            model="mock-gpt",
            capabilities=["web_search", "memory_read", "memory_write"],
        )
        tokens = os.registry.synthesize(agent.capabilities)
        agent.capabilities = [t.name for t in tokens]
        os.store.create_agent(agent)
        agent_ids.append(agent.id)
        os.tracer.inc("agents_created")

    wf = Workflow(name=body.name, goal=body.goal, agent_ids=agent_ids)
    os.store.create_workflow(wf)

    results = []
    for aid in agent_ids:
        agent = os.store.get_agent(aid)
        task = Task(agent_id=aid, goal=f"[{agent.name}] Contribute to: {body.goal}")
        os.store.create_task(task)
        task = await os.runtime.run_task(agent, task)
        os.store.update_task(task)
        results.append({"agent": agent.name, "result": task.result, "status": task.status})

    wf.status = TaskStatus.COMPLETED
    wf.result = str(results)
    os.store.save()
    return {"workflow": wf.model_dump(mode="json"), "results": results}


@router.get("/dashboard")
async def dashboard():
    """Serve the WebMCP control plane from web/server-os.html."""
    return RedirectResponse(url="/web/server-os.html", status_code=307)
