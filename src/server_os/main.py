"""Server OS entrypoint."""

from __future__ import annotations

from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server_os.agents.runtime import AgentRuntime
from server_os.api.routes import router
from server_os.config import settings
from server_os.cost.controller import CostController
from server_os.governance.policy import PolicyEngine
from server_os.kernel.capabilities import CapabilityRegistry
from server_os.kernel.memory import MemoryStore
from server_os.kernel.store import ProcessTable
from server_os.observability.tracer import Tracer
from server_os.tools.builtin import register_builtins

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

WEB_DIR = Path(__file__).resolve().parents[2] / "web"


class ServerOS:
    def __init__(self) -> None:
        self.store = ProcessTable()
        self.memory = MemoryStore()
        self.registry = CapabilityRegistry()
        self.cost = CostController()
        self.policy = PolicyEngine()
        self.tracer = Tracer()
        self.tools = register_builtins(self.registry, self.memory)
        self.runtime = AgentRuntime(
            registry=self.registry,
            memory=self.memory,
            cost=self.cost,
            policy=self.policy,
            tracer=self.tracer,
        )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Server OS",
        description="Autonomous Agentic Operating System",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.os = ServerOS()
    app.include_router(router)
    if WEB_DIR.is_dir():
        app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
