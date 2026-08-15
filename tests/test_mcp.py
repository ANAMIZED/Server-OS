"""MCP Server in-process tests."""

from __future__ import annotations

import pytest

from mcp import Client
from server_os.mcp.server import mcp


@pytest.mark.asyncio
async def test_mcp_lists_expected_tools():
    async with Client(mcp) as client:
        result = await client.list_tools()
        names = {t.name for t in result.tools}
        expected = {
            "list_agents",
            "create_agent",
            "run_task",
            "get_agent",
            "get_cost_ledger",
            "get_audit_log",
            "get_metrics",
            "create_workflow",
            "list_available_tools",
        }
        assert expected.issubset(names)


@pytest.mark.asyncio
async def test_mcp_create_agent_and_list():
    async with Client(mcp) as client:
        created = await client.call_tool(
            "create_agent",
            {
                "name": "mcp-pytest",
                "intent": "Answer factual questions under budget",
                "budget_usd": 0.25,
                "capabilities": ["web_search"],
            },
        )
        assert created is not None
        listed = await client.call_tool("list_agents", {})
        assert listed is not None


@pytest.mark.asyncio
async def test_mcp_list_available_tools():
    async with Client(mcp) as client:
        result = await client.call_tool("list_available_tools", {})
        assert result is not None
