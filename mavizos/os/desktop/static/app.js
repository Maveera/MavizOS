const API = "/api/v1";

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function showPanel(name) {
  document.querySelectorAll(".panel").forEach((p) => p.classList.remove("visible"));
  document.querySelectorAll(".nav").forEach((n) => n.classList.remove("active"));
  document.getElementById("panel-" + name)?.classList.add("visible");
  document.querySelector(`.nav[data-panel="${name}"]`)?.classList.add("active");
}

document.querySelectorAll(".nav").forEach((btn) => {
  btn.addEventListener("click", () => showPanel(btn.dataset.panel));
});

async function loadAgents() {
  const agents = await api("/agents");
  const grid = document.getElementById("agents-list");
  grid.innerHTML = agents
    .map(
      (a) =>
        `<div class="card"><h3>${a.name}</h3><p>${a.description}</p><p style="color:var(--success)">running</p></div>`
    )
    .join("");
}

async function loadAudit() {
  const entries = await api("/audit?limit=30");
  const tbody = document.querySelector("#audit-table tbody");
  tbody.innerHTML = entries
    .map(
      (e) =>
        `<tr><td>${String(e.timestamp).slice(0, 19)}</td><td>${e.actor}</td><td>${e.action}</td><td>${e.outcome}</td></tr>`
    )
    .join("");
}

async function loadApprovals() {
  const pending = await api("/approvals/pending");
  const list = document.getElementById("approvals-list");
  if (!pending.length) {
    list.innerHTML = "<li>No pending approvals</li>";
    return;
  }
  list.innerHTML = pending
    .map(
      (r) =>
        `<li><strong>${r.action_type}</strong> — ${r.description} <code>${r.id.slice(0, 8)}</code></li>`
    )
    .join("");
}

async function loadIncidents() {
  const list = document.getElementById("incidents-list");
  list.innerHTML = "<li>Run an investigation from Report panel to create incidents.</li>";
}

document.getElementById("hunt-run")?.addEventListener("click", async () => {
  const hypothesis =
    document.getElementById("hunt-hypothesis").value ||
    "Hunt for lateral movement";
  const out = document.getElementById("hunt-result");
  out.textContent = "Running hunt...";
  try {
    const result = await api("/hunt", {
      method: "POST",
      body: JSON.stringify({ hypothesis }),
    });
    out.textContent = JSON.stringify(result, null, 2);
  } catch (e) {
    out.textContent = "Error: " + e.message;
  }
});

document.getElementById("run-investigate")?.addEventListener("click", async () => {
  const view = document.getElementById("report-view");
  view.textContent = "Running 10-step investigation (simulated TI)...";
  try {
    const result = await api("/investigate", {
      method: "POST",
      body: JSON.stringify({
        alerts: [
          {
            title: "Suspicious encoded PowerShell execution",
            description: "Encoded PowerShell with network connection",
            severity: "high",
            source: "edr",
            source_system: "crowdstrike",
            host: "WORKSTATION-42",
            user: "jsmith",
            ip_address: "203.0.113.50",
            process: "powershell.exe",
            file_hash: "a1b2c3d4e5f6789012345678abcdef01",
          },
        ],
      }),
    });
    document.getElementById("incident-id").value = result.incident_id;
    const report = result.report;
    view.innerHTML = `
      <h3>${report.severity} — confidence ${report.confidence}</h3>
      <p>${report.executive_summary}</p>
      <p><em>IOCs: ${report.iocs?.length || 0} (simulated in demo)</em></p>
    `;
    loadApprovals();
  } catch (e) {
    view.textContent = "Error: " + e.message;
  }
});

document.getElementById("load-report")?.addEventListener("click", async () => {
  const id = document.getElementById("incident-id").value.trim();
  if (!id) return;
  const view = document.getElementById("report-view");
  try {
    const inc = await api("/incidents/" + id);
    view.textContent = JSON.stringify(inc, null, 2);
  } catch (e) {
    view.textContent = "Error: " + e.message;
  }
});

async function init() {
  try {
    const health = await api("/health");
    document.getElementById("status-pill").textContent = health.status;
    await loadAgents();
    await loadAudit();
    await loadApprovals();
    loadIncidents();
  } catch (e) {
    document.getElementById("status-pill").textContent = "offline";
    document.getElementById("status-pill").style.background = "var(--danger)";
  }
}

init();
