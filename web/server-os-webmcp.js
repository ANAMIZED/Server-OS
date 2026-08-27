(function () {
  "use strict";
  var W = window.ANAMIZEDWebMCP;
  var logEl = document.getElementById("webmcp-log");
  var statusEl = document.getElementById("webmcp-status");
  var MOCK = { agents: [], metrics: { agents_created: 0 }, ledger: [], audit: [] };
  async function tryLive(path, fallback) {
    try { return { source: "live", data: await W.rest(path) }; }
    catch (_err) { return { source: "page-mock", data: fallback }; }
  }
  var tools = [
    { name: "get_metrics", description: "Runtime counters. Read-only.", inputSchema: { type: "object", properties: {} }, annotations: { readOnlyHint: true }, execute: async function () { return tryLive("/metrics", MOCK.metrics); } },
    { name: "list_agents", description: "List agent process records. Read-only.", inputSchema: { type: "object", properties: {} }, annotations: { readOnlyHint: true }, execute: async function () { return tryLive("/v1/agents", MOCK.agents); } },
    { name: "list_available_tools", description: "Capability names grantable to agents.", inputSchema: { type: "object", properties: {} }, annotations: { readOnlyHint: true }, execute: async function () { return { source: "page", tools: ["web_search", "memory_read", "memory_write"] }; } },
    { name: "get_cost_ledger", description: "Token/$ ledger. Read-only.", inputSchema: { type: "object", properties: {} }, annotations: { readOnlyHint: true }, execute: async function () { return tryLive("/v1/cost/ledger", MOCK.ledger); } },
    { name: "get_audit_log", description: "Governance allow/deny records. Read-only.", inputSchema: { type: "object", properties: {} }, annotations: { readOnlyHint: true }, execute: async function () { return tryLive("/v1/audit", MOCK.audit); } },
    { name: "create_agent", description: "Create an agent on live REST when available. Requires confirmation. Does not run a goal.", inputSchema: { type: "object", properties: { name: { type: "string" }, intent: { type: "string" }, budget_usd: { type: "number" } }, required: ["name", "intent"] }, annotations: { readOnlyHint: false },
      execute: async function (params) {
        if (!W.confirmWrite("Create agent " + params.name + "?")) return { cancelled: true };
        try {
          var created = await W.rest("/v1/agents", { method: "POST", body: { name: params.name, intent: params.intent, budget_usd: params.budget_usd || 0.5, capabilities: ["web_search", "memory_read", "memory_write"], model: "mock-gpt" } });
          W.log(logEl, "create_agent live " + params.name);
          return { source: "live", agent: created };
        } catch (_err) {
          var agent = { id: "page-" + Date.now(), name: params.name, intent: params.intent, budget_usd: params.budget_usd || 0.5, status: "mock" };
          MOCK.agents.push(agent); MOCK.metrics.agents_created += 1;
          W.log(logEl, "create_agent mock " + params.name);
          return { source: "page-mock", agent: agent, note: "No live Server-OS API on this origin." };
        }
      } }
  ];
  async function boot() {
    statusEl.textContent = W.supported() ? "WebMCP available — control-plane tools registered" : "WebMCP API not in this browser.";
    W.log(logEl, "registered " + JSON.stringify(await W.registerAll(tools)));
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
