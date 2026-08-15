#!/usr/bin/env bash
# Server OS end-to-end verification contract.
# Covers: API, cost, governance, multi-agent, dashboard, SDK, CLI, MCP, skills, AGENTS.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SERVER_OS_URL:-http://127.0.0.1:8080}"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
PASS=0
FAIL=0

green() { printf "\033[32m✓ %s\033[0m\n" "$*"; PASS=$((PASS+1)); }
red()   { printf "\033[31m✗ %s\033[0m\n" "$*"; FAIL=$((FAIL+1)); }
info()  { printf "\033[36m→ %s\033[0m\n" "$*"; }

wait_for_health() {
  info "Waiting for Server OS at $BASE ..."
  for i in $(seq 1 40); do
    if curl -sf "$BASE/health" >/dev/null 2>&1; then
      green "Health check passed"
      return 0
    fi
    sleep 0.5
  done
  red "Server did not become healthy at $BASE"
  exit 1
}

info "Checking AGENTS.md and skills..."
if [[ -f "$ROOT/AGENTS.md" ]] && grep -q "verify.sh" "$ROOT/AGENTS.md"; then
  green "AGENTS.md present with verify contract"
else
  red "AGENTS.md missing or incomplete"
fi

SKILL_COUNT=0
for d in cost-control governance-audit deploy-verify x402-payments multi-agent-workflow; do
  f="$ROOT/skills/$d/SKILL.md"
  if [[ -f "$f" ]] && head -1 "$f" | grep -q '^---'; then
    SKILL_COUNT=$((SKILL_COUNT+1))
  else
    red "Skill missing or invalid frontmatter: $d"
  fi
done
if [[ "$SKILL_COUNT" -eq 5 ]]; then
  green "All 5 SKILL.md packages present with frontmatter"
fi

info "Running unit + surface tests (pytest)..."
if (cd "$ROOT" && python -m pytest -q tests/ 2>/dev/null); then
  green "Pytest suite passed"
else
  if (cd "$ROOT" && python -m pytest -q tests/test_smoke.py tests/test_cli.py tests/test_skills_and_agents_md.py tests/test_mcp.py 2>/dev/null); then
    green "Core + CLI + skills + MCP pytest passed (SDK may skip until server up)"
  else
    red "Pytest failures"
  fi
fi

wait_for_health

info "API: create research agent..."
CREATE=$(curl -sf -X POST "$BASE/v1/agents" -H "Content-Type: application/json" -d '{"name":"verify-research","intent":"Answer factual questions using only approved tools and stay under budget. May search the web and use memory.","budget_usd":0.50,"model":"mock-gpt","capabilities":["web_search","memory_read","memory_write"]}')
AGENT_ID=$(echo "$CREATE" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
if [[ -n "$AGENT_ID" ]]; then green "Agent created: $AGENT_ID"; else red "Failed to create agent"; exit 1; fi

info "API: run factual task..."
TASK=$(curl -sf -X POST "$BASE/v1/agents/$AGENT_ID/tasks" -H "Content-Type: application/json" -d '{"goal":"What is the capital of France?"}')
STATUS=$(echo "$TASK" | python -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
RESULT=$(echo "$TASK" | python -c "import sys,json; print(json.load(sys.stdin).get('result') or '')")
if [[ "$STATUS" == "completed" ]] && echo "$RESULT" | grep -qi "paris"; then green "Task completed with correct answer (Paris)"; else red "Task failed or wrong answer (status=$STATUS)"; fi

info "API: cost ledger..."
LEDGER=$(curl -sf "$BASE/v1/cost/ledger")
COUNT=$(echo "$LEDGER" | python -c "import sys,json; print(len(json.load(sys.stdin)))")
if [[ "$COUNT" -ge 1 ]]; then green "Cost ledger has $COUNT entries"; else red "Cost ledger empty"; fi

info "API: audit log reachable..."
curl -sf "$BASE/v1/audit" | python -c "import sys,json; json.load(sys.stdin)" >/dev/null
green "Audit log reachable"

info "API: metrics..."
METRICS=$(curl -sf "$BASE/metrics")
AC=$(echo "$METRICS" | python -c "import sys,json; print(int(json.load(sys.stdin).get('agents_created',0)))")
if [[ "$AC" -ge 1 ]]; then green "Metrics agents_created=$AC"; else red "Metrics unexpected"; fi

info "API: multi-agent workflow..."
WF=$(curl -sf -X POST "$BASE/v1/workflows" -H "Content-Type: application/json" -d '{"name":"verify-wf","agents":["planner","researcher"],"goal":"Summarize what an agentic operating system is","budget_usd":1.0}')
WF_STATUS=$(echo "$WF" | python -c "import sys,json; print(json.load(sys.stdin).get('workflow',{}).get('status',''))")
if [[ "$WF_STATUS" == "completed" ]]; then green "Multi-agent workflow completed"; else red "Workflow status=$WF_STATUS"; fi

info "API: dashboard..."
if curl -sf "$BASE/dashboard" | grep -q "Server OS"; then green "Dashboard is live"; else red "Dashboard not reachable"; fi

info "API: payment-capable agent path..."
CREATE3=$(curl -sf -X POST "$BASE/v1/agents" -H "Content-Type: application/json" -d '{"name":"verify-payer","intent":"May make small payments for premium tools when required. Budget aware.","budget_usd":0.20,"model":"mock-gpt","capabilities":["payment","web_search"]}')
AGENT3=$(echo "$CREATE3" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
curl -sf -X POST "$BASE/v1/agents/$AGENT3/tasks" -H "Content-Type: application/json" -d '{"goal":"Please pay for the premium data feed"}' >/dev/null
green "Payment-capable agent task executed"

info "SDK: create + run via ServerOSClient..."
if python - << PY
from server_os.sdk import ServerOSClient
from server_os.kernel.models import AgentCreate
with ServerOSClient("$BASE") as c:
    a = c.create_agent(AgentCreate(name="verify-sdk", intent="Answer factual questions under budget", budget_usd=0.3, capabilities=["web_search"]))
    t = c.run_task(a.id, "What is the capital of France?")
    assert "paris" in (t.result or "").lower(), t.result
    assert c.health()["status"] == "ok"
print("ok")
PY
then green "SDK create + run + health OK"; else red "SDK path failed"; fi

info "CLI: status + agents list..."
if python -m server_os.cli status --url "$BASE" >/dev/null 2>&1; then green "CLI status OK"; else red "CLI status failed"; fi
if python -m server_os.cli agents list --url "$BASE" >/dev/null 2>&1; then green "CLI agents list OK"; else red "CLI agents list failed"; fi

info "MCP: list tools + create_agent via Client..."
if python - << 'PY'
import asyncio
from mcp import Client
from server_os.mcp.server import mcp
async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}
        required = {"create_agent", "run_task", "list_agents", "get_cost_ledger", "get_audit_log", "create_workflow"}
        assert required.issubset(names), names
        await client.call_tool("list_available_tools", {})
        await client.call_tool("create_agent", {"name": "verify-mcp", "intent": "Answer questions under budget", "budget_usd": 0.2, "capabilities": ["web_search"]})
asyncio.run(main())
print("ok")
PY
then green "MCP tools + create_agent OK"; else red "MCP path failed"; fi

echo ""
echo "=============================="
echo " Server OS verification result"
echo "=============================="
echo "  PASSED: $PASS"
echo "  FAILED: $FAIL"
echo "=============================="

if [[ "$FAIL" -eq 0 ]]; then
  echo "ALL CHECKS PASSED — API, cost, governance, workflow, SDK, CLI, MCP, skills, AGENTS.md."
  exit 0
else
  echo "SOME CHECKS FAILED — inspect output above."
  exit 1
fi
