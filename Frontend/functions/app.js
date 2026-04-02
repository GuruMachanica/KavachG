const API_BASE = `http://${window.location.hostname}:8000`;

const state = {
  token: localStorage.getItem("token") || "",
  user: JSON.parse(localStorage.getItem("user") || "null"),
  incidents: [],
  sensitivity: 50,
  cameras: [],
  ws: null,
};

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function showToast(message, type = "ok") {
  const root = document.body;
  const toast = document.createElement("div");
  toast.className = `toast ${type === "error" ? "toast-error" : "toast-ok"}`;
  toast.textContent = message;
  root.appendChild(toast);
  setTimeout(() => toast.remove(), 2600);
}

function authHeaders(extra = {}) {
  if (!state.token) {
    return extra;
  }
  return { Authorization: `Bearer ${state.token}`, ...extra };
}

async function parseResponse(response) {
  const text = await response.text();
  let payload = {};
  try {
    payload = text ? JSON.parse(text) : {};
  } catch (_err) {
    payload = { detail: text || "Unknown error" };
  }
  if (!response.ok) {
    throw new Error(payload.detail || payload.error || "Request failed");
  }
  return payload;
}

async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  return parseResponse(response);
}

async function fetchIncidents() {
  const response = await fetch(`${API_BASE}/incidents/`, {
    headers: authHeaders(),
  });
  return parseResponse(response);
}

async function addIncident(type, description) {
  const response = await fetch(`${API_BASE}/incidents/`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ type, description }),
  });
  return parseResponse(response);
}

async function sendFeedback(id, comment) {
  const response = await fetch(`${API_BASE}/incidents/${id}/feedback`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(comment),
  });
  return parseResponse(response);
}

async function updateIncidentStatus(id, status) {
  const response = await fetch(
    `${API_BASE}/incidents/${id}/status?status=${encodeURIComponent(status)}`,
    { method: "PATCH", headers: authHeaders() }
  );
  return parseResponse(response);
}

async function getSensitivity() {
  const response = await fetch(`${API_BASE}/settings/sensitivity`, {
    headers: authHeaders(),
  });
  return parseResponse(response);
}

async function setSensitivity(value) {
  const response = await fetch(`${API_BASE}/settings/sensitivity`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ value }),
  });
  return parseResponse(response);
}

async function createUser(payload) {
  const response = await fetch(`${API_BASE}/auth/admin/create`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  return parseResponse(response);
}

async function getCameras() {
  const response = await fetch(`${API_BASE}/cameras`, {
    headers: authHeaders(),
  });
  return parseResponse(response);
}

async function runDetection(path, file) {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  return parseResponse(response);
}

function clipUrl(incident) {
  if (incident.clip_path) {
    return `${API_BASE}/clips/${encodeURIComponent(incident.clip_path)}?token=${encodeURIComponent(state.token)}`;
  }
  const match = String(incident.description || "").match(/([A-Za-z0-9_-]+\.mp4)/);
  if (!match) {
    return "";
  }
  return `${API_BASE}/clips/${encodeURIComponent(match[1])}?token=${encodeURIComponent(state.token)}`;
}

function formatTime(value) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString();
}

function setTab(tabName) {
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.add("hidden"));
  document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.remove("active"));
  document.getElementById(`tab-${tabName}`).classList.remove("hidden");
  document.querySelector(`[data-tab='${tabName}']`).classList.add("active");
}

function showApp() {
  document.getElementById("login-view").classList.add("hidden");
  document.getElementById("app-view").classList.remove("hidden");
  const name = state.user?.name || state.user?.email || "Operator";
  const role = state.user?.role || "user";
  document.getElementById("welcome-text").textContent = `Welcome, ${name} (${role})`;
}

function showLogin() {
  document.getElementById("app-view").classList.add("hidden");
  document.getElementById("login-view").classList.remove("hidden");
}

function incidentStats() {
  const now = new Date();
  const weekAgo = new Date();
  weekAgo.setDate(now.getDate() - 7);
  return {
    total: state.incidents.length,
    today: state.incidents.filter((i) => new Date(i.created_at).toDateString() === now.toDateString()).length,
    week: state.incidents.filter((i) => new Date(i.created_at) >= weekAgo).length,
    ppe: state.incidents.filter((i) => String(i.type).toLowerCase().includes("ppe")).length,
    fire: state.incidents.filter((i) => String(i.type).toLowerCase().includes("fire")).length,
    fall: state.incidents.filter((i) => String(i.type).toLowerCase().includes("fall")).length,
  };
}

function exportIncidentsCsv() {
  const header = "id,type,description,status,created_at\n";
  const lines = state.incidents.map((i) => [
    i.id,
    `"${String(i.type || "").replaceAll('"', '""')}"`,
    `"${String(i.description || "").replaceAll('"', '""')}"`,
    `"${String(i.status || "").replaceAll('"', '""')}"`,
    `"${String(i.created_at || "").replaceAll('"', '""')}"`,
  ].join(","));
  const blob = new Blob([header + lines.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `incidents_${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function renderOverview() {
  const stats = incidentStats();
  const recentRows = state.incidents.slice(0, 10).map((incident) => {
    const clip = clipUrl(incident);
    return `
      <tr>
        <td>${incident.id}</td>
        <td>${esc(incident.type)}</td>
        <td>${esc(incident.status)}</td>
        <td>${formatTime(incident.created_at)}</td>
        <td>${clip ? `<a href="${clip}" target="_blank">Clip</a>` : "-"}</td>
      </tr>`;
  }).join("");

  document.getElementById("tab-overview").innerHTML = `
    <div class="toolbar">
      <h2>Operational Dashboard</h2>
      <div class="actions-inline">
        <button id="export-incidents-btn">Export Incidents CSV</button>
        <button id="download-fall-report-btn">Download Fall Report</button>
      </div>
    </div>
    <div class="grid-4">
      <article class="stat"><span class="muted">Incidents Today</span><strong>${stats.today}</strong></article>
      <article class="stat"><span class="muted">Incidents This Week</span><strong>${stats.week}</strong></article>
      <article class="stat"><span class="muted">PPE / Fire / Fall</span><strong>${stats.ppe} / ${stats.fire} / ${stats.fall}</strong></article>
      <article class="stat"><span class="muted">Total</span><strong>${stats.total}</strong></article>
    </div>
    <div class="card" style="margin-top: 1rem;">
      <h3>Recent Incidents</h3>
      <table>
        <thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Time</th><th>Clip</th></tr></thead>
        <tbody>${recentRows || `<tr><td colspan="5" class="muted">No incidents yet</td></tr>`}</tbody>
      </table>
    </div>
  `;

  document.getElementById("export-incidents-btn").addEventListener("click", exportIncidentsCsv);
  document.getElementById("download-fall-report-btn").addEventListener("click", async () => {
    try {
      const response = await fetch(`${API_BASE}/report/fall`, { headers: authHeaders() });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "fall_report.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      showToast(`Report failed: ${error.message}`, "error");
    }
  });
}

function renderDetection() {
  const cameraOptions = state.cameras.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join("");
  document.getElementById("tab-detection").innerHTML = `
    <h2>Monitoring & Detection</h2>
    <div class="split" style="margin-top: 1rem;">
      <article class="card">
        <h3>Live Monitoring</h3>
        <div class="stack">
          <label>Camera</label>
          <select id="camera-select">${cameraOptions || `<option value="0">Default Camera</option>`}</select>
          <label>Mode</label>
          <select id="stream-mode">
            <option value="video_feed">Raw Feed</option>
            <option value="live/ppe">PPE</option>
            <option value="live/fire-smoke">Fire/Smoke</option>
            <option value="live/fall">Fall</option>
          </select>
          <div class="actions-inline">
            <button id="stream-toggle-btn">Pause</button>
            <button id="snapshot-btn">Snapshot</button>
          </div>
          <img id="live-view" src="${API_BASE}/video_feed" alt="Live stream" />
        </div>
      </article>
      <article class="card">
        <h3>Run Image Detection</h3>
        <div class="stack">
          <label>Model</label>
          <select id="model-select">
            <option value="/detect/ppe/">PPE Detection</option>
            <option value="/detect/fire-smoke/">Fire/Smoke Detection</option>
            <option value="/detect/fall/">Fall Detection</option>
          </select>
          <input id="detect-file" type="file" accept="image/*" />
          <button id="run-detect-btn">Run Detection</button>
          <div id="detect-status" class="muted"></div>
          <pre id="detect-results" class="code-box"></pre>
        </div>
      </article>
    </div>
  `;

  const live = document.getElementById("live-view");
  const modeSelect = document.getElementById("stream-mode");
  let paused = false;

  function setLiveSource(modeValue) {
    const streamUrl = `${API_BASE}/${modeValue}?t=${Date.now()}`;
    live.src = "";
    live.src = streamUrl;
  }

  async function stopMonitoringLive() {
    try {
      await fetch(`${API_BASE}/monitoring/stop`, { method: "POST" });
    } catch (_error) {
      // Ignore network errors; stream src clear is still applied locally.
    }
  }

  modeSelect.addEventListener("change", () => {
    if (!paused) {
      setLiveSource(modeSelect.value);
    }
  });

  document.getElementById("stream-toggle-btn").addEventListener("click", (event) => {
    paused = !paused;
    if (paused) {
      live.src = "";
      stopMonitoringLive();
      event.target.textContent = "Resume";
    } else {
      setLiveSource(modeSelect.value);
      event.target.textContent = "Pause";
    }
  });

  document.getElementById("snapshot-btn").addEventListener("click", () => {
    const canvas = document.createElement("canvas");
    canvas.width = live.naturalWidth || 1280;
    canvas.height = live.naturalHeight || 720;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }
    ctx.drawImage(live, 0, 0, canvas.width, canvas.height);
    const a = document.createElement("a");
    a.href = canvas.toDataURL("image/png");
    a.download = `snapshot_${Date.now()}.png`;
    a.click();
  });

  document.getElementById("camera-select").addEventListener("change", () => {
    showToast("Camera selection updated for operator context.");
  });

  document.getElementById("run-detect-btn").addEventListener("click", async () => {
    const file = document.getElementById("detect-file").files[0];
    const modelPath = document.getElementById("model-select").value;
    const statusEl = document.getElementById("detect-status");
    const resultsEl = document.getElementById("detect-results");
    if (!file) {
      statusEl.textContent = "Select an image first.";
      return;
    }
    statusEl.textContent = "Running model...";
    resultsEl.textContent = "";
    try {
      const result = await runDetection(modelPath, file);
      const detections = result.detections || [];
      statusEl.textContent = `Completed with ${detections.length} detection(s).`;
      resultsEl.textContent = JSON.stringify(detections, null, 2);
    } catch (error) {
      statusEl.textContent = "Detection failed.";
      resultsEl.textContent = error.message;
    }
  });
}

function renderIncidents() {
  const rows = state.incidents.map((incident) => {
    const clip = clipUrl(incident);
    const statusOptions = ["Open", "In Progress", "Closed"].map((status) =>
      `<option value="${status}" ${incident.status === status ? "selected" : ""}>${status}</option>`
    ).join("");
    return `
      <tr>
        <td>${incident.id}</td>
        <td>${esc(incident.type)}</td>
        <td>${esc(incident.description || "-")}</td>
        <td>${formatTime(incident.created_at)}</td>
        <td>${clip ? `<a href="${clip}" target="_blank">View</a>` : "-"}</td>
        <td><select data-id="${incident.id}" class="status-select">${statusOptions}</select></td>
        <td><button data-id="${incident.id}" class="feedback-btn">Feedback</button></td>
      </tr>`;
  }).join("");

  document.getElementById("tab-incidents").innerHTML = `
    <div class="toolbar">
      <h2>Incident Registry</h2>
      <div class="actions-inline">
        <input id="manual-type" placeholder="Type (ppe/fire-smoke/fall/manual)" />
        <input id="manual-desc" placeholder="Manual incident description" />
        <button id="manual-add-btn">Log Incident</button>
      </div>
    </div>
    <div class="card" style="margin-top: 1rem;">
      <table>
        <thead>
          <tr><th>ID</th><th>Type</th><th>Description</th><th>Time</th><th>Clip</th><th>Status</th><th>Feedback</th></tr>
        </thead>
        <tbody>${rows || `<tr><td colspan="7" class="muted">No incidents found</td></tr>`}</tbody>
      </table>
    </div>
  `;

  document.getElementById("manual-add-btn").addEventListener("click", async () => {
    const type = document.getElementById("manual-type").value.trim() || "manual";
    const description = document.getElementById("manual-desc").value.trim();
    if (!description) {
      showToast("Enter incident description.", "error");
      return;
    }
    try {
      await addIncident(type, description);
      showToast("Incident logged.");
      await refreshAll();
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  document.querySelectorAll(".status-select").forEach((select) => {
    select.addEventListener("change", async (event) => {
      const id = event.target.dataset.id;
      try {
        await updateIncidentStatus(id, event.target.value);
        showToast("Status updated.");
        await refreshAll();
      } catch (error) {
        showToast(error.message, "error");
      }
    });
  });

  document.querySelectorAll(".feedback-btn").forEach((btn) => {
    btn.addEventListener("click", async (event) => {
      const id = event.target.dataset.id;
      const comment = prompt("Enter feedback for this incident:");
      if (!comment) {
        return;
      }
      try {
        await sendFeedback(id, comment);
        showToast("Feedback submitted.");
      } catch (error) {
        showToast(error.message, "error");
      }
    });
  });
}

function renderSettings() {
  document.getElementById("tab-settings").innerHTML = `
    <h2>Admin Controls</h2>
    <div class="split" style="margin-top: 1rem;">
      <article class="card">
        <h3>Detection Sensitivity</h3>
        <div class="stack">
          <label>Sensitivity: <span id="sens-label">${state.sensitivity}</span></label>
          <input id="sens-slider" type="range" min="0" max="100" value="${state.sensitivity}" />
          <button id="sens-save-btn">Save Sensitivity</button>
          <div id="sens-status" class="muted"></div>
        </div>
      </article>
      <article class="card">
        <h3>Create User Account</h3>
        <div class="stack">
          <input id="new-user-name" placeholder="Name" />
          <input id="new-user-email" type="email" placeholder="Email" />
          <input id="new-user-pass" type="password" placeholder="Password" />
          <select id="new-user-role">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
          <button id="create-user-btn">Create User</button>
          <div id="create-user-status" class="muted"></div>
        </div>
      </article>
    </div>
  `;

  const slider = document.getElementById("sens-slider");
  const label = document.getElementById("sens-label");
  slider.addEventListener("input", () => {
    label.textContent = slider.value;
  });

  document.getElementById("sens-save-btn").addEventListener("click", async () => {
    const statusEl = document.getElementById("sens-status");
    try {
      await setSensitivity(Number(slider.value));
      state.sensitivity = Number(slider.value);
      statusEl.className = "ok-text";
      statusEl.textContent = "Sensitivity saved.";
    } catch (error) {
      statusEl.className = "error-text";
      statusEl.textContent = error.message;
    }
  });

  document.getElementById("create-user-btn").addEventListener("click", async () => {
    const payload = {
      name: document.getElementById("new-user-name").value.trim(),
      email: document.getElementById("new-user-email").value.trim(),
      password: document.getElementById("new-user-pass").value,
      role: document.getElementById("new-user-role").value,
    };
    const statusEl = document.getElementById("create-user-status");
    if (!payload.name || !payload.email || !payload.password) {
      statusEl.className = "error-text";
      statusEl.textContent = "All fields are required.";
      return;
    }
    try {
      await createUser(payload);
      statusEl.className = "ok-text";
      statusEl.textContent = "User created successfully.";
      showToast("User account created.");
    } catch (error) {
      statusEl.className = "error-text";
      statusEl.textContent = error.message;
    }
  });
}

function connectRealtime() {
  if (!state.token) {
    return;
  }
  if (state.ws) {
    state.ws.close();
  }
  const wsBase = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.hostname}:8000/ws/incidents`;
  state.ws = new WebSocket(wsBase);
  state.ws.onmessage = async () => {
    await refreshAll();
    showToast("Incident stream updated.");
  };
  state.ws.onclose = () => {
    setTimeout(connectRealtime, 2500);
  };
}

async function refreshAll() {
  try {
    const [incidents, sensitivity, cameras] = await Promise.all([
      fetchIncidents(),
      getSensitivity(),
      getCameras(),
    ]);
    state.incidents = incidents;
    state.sensitivity = sensitivity.sensitivity ?? 50;
    state.cameras = cameras;
    renderOverview();
    renderDetection();
    renderIncidents();
    renderSettings();
  } catch (error) {
    if (String(error.message).includes("401")) {
      logout();
      return;
    }
    showToast(error.message, "error");
  }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  state.token = "";
  state.user = null;
  if (state.ws) {
    state.ws.close();
    state.ws = null;
  }
  showLogin();
}

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  const errorEl = document.getElementById("login-error");
  const loginBtn = document.getElementById("login-btn");

  errorEl.textContent = "";
  loginBtn.disabled = true;
  loginBtn.textContent = "Signing in...";
  try {
    const data = await login(email, password);
    state.token = data.access_token;
    state.user = data.user;
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));
    showApp();
    setTab("overview");
    await refreshAll();
    connectRealtime();
  } catch (error) {
    errorEl.textContent = error.message;
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "Sign In";
  }
});

document.querySelectorAll(".nav-btn[data-tab]").forEach((btn) => {
  btn.addEventListener("click", () => setTab(btn.dataset.tab));
});

document.getElementById("logout-btn").addEventListener("click", logout);

if (state.token && state.user) {
  showApp();
  setTab("overview");
  refreshAll();
  connectRealtime();
} else {
  showLogin();
}
