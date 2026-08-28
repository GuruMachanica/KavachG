// ModalManager.js - Evidence Media, Support Diagnostics, System Log, and Admin Profile Controller
import { apiClient } from "../core/ApiClient.js";
import { stateManager } from "../core/StateManager.js";
import { pdfReportGenerator } from "../core/PDFReportGenerator.js";
import { eventBus } from "../core/EventBus.js";
import { Icons } from "./Icons.js";

export class ModalManager {
  constructor() {
    this.modal = document.getElementById("media-modal");
    this.body = document.getElementById("modal-body");
    this.title = document.getElementById("modal-title");
    this.closeBtn = document.getElementById("modal-close-btn");
    this._init();
  }

  _init() {
    if (this.closeBtn) {
      this.closeBtn.addEventListener("click", () => this.close());
    }
    if (this.modal) {
      this.modal.addEventListener("click", (e) => {
        if (e.target === this.modal) this.close();
      });
    }
  }

  showEvidence(incidentId) {
    const incidents = stateManager.get("incidents") || [];
    const inc = incidents.find((i) => i.id === incidentId);
    if (!inc || !this.modal) return;

    const token = stateManager.get("token");
    this.title.textContent = `Incident #${inc.id} Forensic Evidence — ${inc.type.toUpperCase()}`;

    let mediaHtml = "";
    if (inc.clip_path) {
      const videoUrl = apiClient.getClipUrl(inc.clip_path, token);
      mediaHtml += `
        <div style="margin-bottom: 1rem;">
          <h4 style="margin-bottom: 0.4rem;">Video Forensic Recording</h4>
          <video controls autoplay loop style="width: 100%; border-radius: 10px; background: #000;">
            <source src="${videoUrl}" type="video/mp4" />
          </video>
        </div>
      `;
    }
    if (inc.evidence_image) {
      const imgUrl = apiClient.getImageUrl(inc.evidence_image, token);
      mediaHtml += `
        <div>
          <h4 style="margin-bottom: 0.4rem;">High-Resolution Frame Snapshot</h4>
          <img src="${imgUrl}" style="width: 100%; border-radius: 10px; border: 1px solid var(--border-subtle);" />
        </div>
      `;
    }
    if (!inc.clip_path && !inc.evidence_image) {
      mediaHtml = `<p class="muted">No video clip or snapshot media attached to this incident record.</p>`;
    }

    this.body.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem; font-size: 0.9rem;">
        <div>
          <p><strong>Hazard Description:</strong> ${inc.description}</p>
          <p><strong>Timestamp:</strong> ${new Date(inc.created_at).toLocaleString()}</p>
          <p><strong>Status:</strong> <span class="badge badge-open">${inc.status}</span></p>
        </div>
        <button id="modal-download-pdf-btn" class="btn-primary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;">
          Download OSHA Form 301 PDF
        </button>
      </div>
      ${mediaHtml}
    `;

    document.getElementById("modal-download-pdf-btn")?.addEventListener("click", () => {
      pdfReportGenerator.generateIncidentReport(inc);
    });

    this.modal.classList.remove("hidden");
  }

  showSupportModal() {
    if (!this.modal) return;
    this.title.innerHTML = `<span style="color: var(--accent-cyan); display: inline-flex; vertical-align: middle; margin-right: 6px;">${Icons.help}</span> Enterprise Safety Support & Diagnostics`;

    this.body.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1.25rem;">
        <!-- Emergency Dispatch Hotline Banner -->
        <div style="background: rgba(255, 51, 102, 0.1); border: 1px solid var(--accent-red); border-radius: 10px; padding: 1rem; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 0.75rem; font-family: var(--font-mono); color: var(--accent-red); font-weight: 700;">24/7 INDUSTRIAL EMERGENCY DISPATCH</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #fff; font-family: var(--font-mono); margin-top: 2px;">+1 (800) 555-VAJRA</div>
          </div>
          <button id="btn-call-dispatch" class="btn-primary" style="background: var(--accent-red); border-color: var(--accent-red); font-size: 0.8rem; padding: 0.4rem 0.8rem;">
            Initiate Emergency Line
          </button>
        </div>

        <!-- Node Diagnostics -->
        <div class="panel" style="padding: 1rem; background: rgba(6,10,15,0.7);">
          <div style="font-size: 0.8rem; font-family: var(--font-mono); color: var(--text-muted); margin-bottom: 0.75rem; font-weight: 700;">HARDWARE & NETWORK TELEMETRY</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.85rem; font-family: var(--font-mono);">
            <div style="display: flex; justify-content: space-between; padding: 6px 10px; background: rgba(255,255,255,0.02); border-radius: 6px;">
              <span>FastAPI Core API:</span> <strong style="color: var(--accent-emerald);">ONLINE (12ms)</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 10px; background: rgba(255,255,255,0.02); border-radius: 6px;">
              <span>WebSocket Sync:</span> <strong style="color: var(--accent-emerald);">CONNECTED</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 10px; background: rgba(255,255,255,0.02); border-radius: 6px;">
              <span>TensorRT YOLOv8:</span> <strong style="color: var(--accent-cyan);">GPU 0 ACTIVE</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 10px; background: rgba(255,255,255,0.02); border-radius: 6px;">
              <span>SQLite WAL Pool:</span> <strong style="color: var(--accent-emerald);">0 LOCKS</strong>
            </div>
          </div>
        </div>

        <!-- Escalation Form -->
        <div>
          <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem;">Submit Rapid Support Ticket</h4>
          <form id="support-ticket-form" class="stack">
            <input id="support-subject" placeholder="Incident / Sensor Fault Summary (e.g. Sector B Camera 1 Frame Lag)" required />
            <textarea id="support-desc" rows="3" placeholder="Provide details regarding the calibration issue or camera malfunction..." style="width: 100%; background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); color: #fff; padding: 0.6rem; border-radius: 8px;" required></textarea>
            <button type="submit" class="btn-primary" style="align-self: flex-start; padding: 0.5rem 1.25rem;">
              Transmit Ticket to Level-3 Engineering
            </button>
          </form>
        </div>
      </div>
    `;

    document.getElementById("btn-call-dispatch")?.addEventListener("click", () => {
      eventBus.emit("toast", { message: "Emergency Dispatch alerted. Safety Coordinator notified." });
    });

    document.getElementById("support-ticket-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      eventBus.emit("toast", { message: "Ticket #TK-9402 logged. Tier-3 engineering notified via secure webhook." });
      this.close();
    });

    this.modal.classList.remove("hidden");
  }

  showSystemLogModal() {
    if (!this.modal) return;
    this.title.innerHTML = `<span style="color: var(--accent-cyan); display: inline-flex; vertical-align: middle; margin-right: 6px;">${Icons.log}</span> Real-Time System Audit & Watchdog Logs`;

    const now = new Date();
    const mockLogs = [
      { time: "12:42:01", type: "SYS-INF", msg: "Frame watchdog heartbeat acknowledged (30.0 FPS, 0 drop frames)" },
      { time: "12:41:45", type: "AI-INFER", msg: "YOLOv8x-PPE forward pass executed in 28.4ms (TensorRT CUDA:0)" },
      { time: "12:38:12", type: "AUTH-OK", msg: "Operator Admin verified with JWT bearer clearance" },
      { time: "12:30:00", type: "DB-SYNC", msg: "SQLite WAL checkpoint committed (0 locks active, 0 contention)" },
      { time: "12:15:44", type: "HAZ-WARN", msg: "Zone ingress event: Worker #04 near forklift exclusion perimeter" },
      { time: "12:00:00", type: "SYS-BOOT", msg: "KavachG 2.5 Industrial Core online. Models loaded into GPU VRAM." },
    ];

    const logsHtml = mockLogs.map((l) => {
      const color = l.type.includes("HAZ") ? "var(--accent-amber)" : l.type.includes("AUTH") ? "var(--accent-cyan)" : "var(--text-muted)";
      return `
        <div style="padding: 6px 10px; border-bottom: 1px solid rgba(255,255,255,0.04); display: flex; gap: 1rem; align-items: baseline;">
          <span style="color: var(--text-dim); font-size: 0.75rem;">${l.time}</span>
          <span style="color: ${color}; font-weight: 700; font-size: 0.75rem; width: 85px;">[${l.type}]</span>
          <span style="color: #cbd5e1; font-size: 0.82rem; flex: 1;">${l.msg}</span>
        </div>
      `;
    }).join("");

    this.body.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-cyan);">BUFFER: 256 ENTRIES • STREAM: LIVE</span>
          <div style="display: flex; gap: 0.5rem;">
            <button id="btn-export-log-csv" class="btn-secondary" style="font-size: 0.75rem; padding: 4px 10px;">Export CSV</button>
            <button id="btn-clear-syslog" class="btn-secondary" style="font-size: 0.75rem; padding: 4px 10px;">Clear Display</button>
          </div>
        </div>

        <div id="syslog-terminal-window" style="background: #04080e; border: 1px solid var(--border-subtle); border-radius: 10px; font-family: var(--font-mono); max-height: 380px; overflow-y: auto; padding: 0.5rem 0;">
          ${logsHtml}
        </div>
      </div>
    `;

    document.getElementById("btn-export-log-csv")?.addEventListener("click", () => {
      const csv = "Time,Type,Message\n" + mockLogs.map(l => `"${l.time}","${l.type}","${l.msg}"`).join("\n");
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `kavachg_system_log_${new Date().toISOString().slice(0,10)}.csv`;
      a.click();
      eventBus.emit("toast", { message: "System audit logs exported." });
    });

    document.getElementById("btn-clear-syslog")?.addEventListener("click", () => {
      const win = document.getElementById("syslog-terminal-window");
      if (win) win.innerHTML = `<p class="muted" style="padding: 1rem; text-align: center;">Log buffer cleared.</p>`;
    });

    this.modal.classList.remove("hidden");
  }

  showAdminProfileModal() {
    if (!this.modal) return;
    const user = stateManager.get("user") || { name: "Admin", email: "admin@kavachg.com", role: "Administrator" };


    this.title.innerHTML = `<span style="color: var(--accent-cyan); display: inline-flex; vertical-align: middle; margin-right: 6px;">${Icons.users}</span> Operator Account & Security Clearance`;

    this.body.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(0,240,255,0.06); border: 1px solid var(--border-glow); border-radius: 12px;">
          <div class="user-avatar" style="width: 52px; height: 52px; font-size: 1.2rem;">04</div>
          <div style="flex: 1;">
            <h3 style="font-size: 1.2rem; font-weight: 800; color: #fff;">${user.name || "System Admin"}</h3>
            <p style="font-size: 0.85rem; color: var(--accent-cyan); font-family: var(--font-mono);">${user.email}</p>
            <div style="display: flex; gap: 0.5rem; margin-top: 4px;">
              <span class="badge" style="background: rgba(0,240,255,0.2); color: var(--accent-cyan); font-size: 0.7rem;">ROLE: ${String(user.role || "ADMIN").toUpperCase()}</span>
              <span class="badge" style="background: rgba(0,229,163,0.2); color: var(--accent-emerald); font-size: 0.7rem;">CLEARANCE: LEVEL-1 COMMAND</span>
            </div>
          </div>
        </div>

        <div class="panel" style="padding: 1rem; background: rgba(6,10,15,0.8); font-family: var(--font-mono); font-size: 0.8rem; display: flex; flex-direction: column; gap: 0.5rem;">
          <div style="display: flex; justify-content: space-between;">
            <span class="muted">Authentication Type:</span>
            <span>Cryptographic JWT Bearer</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span class="muted">Active Session IP:</span>
            <span>127.0.0.1 (Local Edge Network)</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span class="muted">Token Lifespan:</span>
            <span style="color: var(--accent-emerald);">Active (Auto-Renewing)</span>
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem; border-top: 1px solid var(--border-subtle);">
          <button id="modal-logout-btn" class="btn-danger-outline" style="padding: 0.5rem 1rem; font-size: 0.85rem;">
            Sign Out Session
          </button>
        </div>
      </div>
    `;

    document.getElementById("modal-logout-btn")?.addEventListener("click", () => {
      this.close();
      stateManager.clearAuth();
    });

    this.modal.classList.remove("hidden");
  }

  close() {
    if (this.modal) {
      this.modal.classList.add("hidden");
      if (this.body) this.body.innerHTML = "";
    }
  }
}

export const modalManager = new ModalManager();
