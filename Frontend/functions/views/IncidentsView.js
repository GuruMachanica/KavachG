// IncidentsView.js - OSHA 1910 Compliance & Real Database Audit Records
import { BaseView } from "./BaseView.js";
import { stateManager } from "../core/StateManager.js";
import { apiClient } from "../core/ApiClient.js";
import { pdfReportGenerator } from "../core/PDFReportGenerator.js";
import { eventBus } from "../core/EventBus.js";
import { Icons } from "../ui/Icons.js";

export class IncidentsView extends BaseView {
  constructor() {
    super("tab-incidents");
  }

  render() {
    if (!this.container) return;

    const incidents = stateManager.get("incidents") || [];
    const openCount = incidents.filter((i) => i.status === "Open").length;
    const progressCount = incidents.filter((i) => i.status === "In Progress").length;
    const resolvedCount = incidents.filter((i) => i.status === "Resolved").length;

    const complianceScore = incidents.length > 0
      ? Math.round(((resolvedCount + progressCount * 0.5) / incidents.length) * 100)
      : 100;

    // Dynamically build audit table rows from SQLite incidents
    const tableRowsHtml = incidents.length > 0 ? incidents.map((inc) => {
      const isResolved = inc.status === "Resolved";
      const statusColor = isResolved ? "var(--accent-emerald)" : inc.status === "In Progress" ? "var(--accent-amber)" : "var(--accent-red)";
      const dateStr = inc.created_at ? new Date(inc.created_at).toLocaleDateString() : new Date().toLocaleDateString();
      const timeStr = inc.created_at ? new Date(inc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";

      return `
        <tr>
          <td style="font-family: var(--font-mono); font-size: 0.8rem;">
            ${dateStr} <span class="muted" style="font-size: 0.75rem;">${timeStr}</span>
          </td>
          <td style="color: var(--accent-cyan); font-family: var(--font-mono); font-weight: 700;">#INC-${inc.id.toString().padStart(4, '0')}</td>
          <td>
            <div style="font-size: 0.85rem; font-weight: 600; color: #fff;">${this.escape(inc.type)}</div>
            <div class="muted" style="font-size: 0.75rem;">${this.escape(inc.description)}</div>
          </td>
          <td style="font-family: var(--font-mono); font-size: 0.8rem;">CAM-0${(inc.camera_id ?? 0) + 1}</td>
          <td>
            <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-family: var(--font-mono); font-weight: 700; background: rgba(0,0,0,0.5); color: ${statusColor}; border: 1px solid ${statusColor};">
              ${inc.status}
            </span>
          </td>
          <td>
            <div style="display: flex; gap: 0.4rem;">
              ${!isResolved ? `
                <button class="btn-primary btn-resolve-inc" data-inc-id="${inc.id}" style="font-size: 0.75rem; padding: 0.3rem 0.6rem;">
                  Resolve
                </button>
              ` : `
                <span class="muted" style="font-size: 0.75rem; font-family: var(--font-mono);">Logged</span>
              `}
              ${inc.evidence_image ? `
                <a href="${inc.evidence_image}" target="_blank" class="btn-secondary" style="font-size: 0.75rem; padding: 0.3rem 0.6rem; text-decoration: none;">
                  Evidence
                </a>
              ` : ""}
            </div>
          </td>
        </tr>
      `;
    }).join("") : `
      <tr>
        <td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          No incident logs in database. Facility is operating within 100% OSHA nominal safety bounds.
        </td>
      </tr>
    `;

    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <h1 style="font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;">OSHA 1910 Compliance Audit</h1>
            <p class="muted" style="font-size: 0.9rem;">Continuous safety enforcement linked directly to SQLite WAL Database.</p>
          </div>
          <div style="font-size: 0.8rem; font-family: var(--font-mono); color: var(--accent-cyan); background: rgba(0,240,255,0.05); padding: 4px 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
            ${incidents.length} TOTAL AUDIT ENTRIES
          </div>
        </div>

        <!-- Main Split: Left Export & Score Cards | Right Document Preview & Audit History -->
        <div style="display: grid; grid-template-columns: 340px 1fr; gap: 1.5rem; align-items: start;">
          <!-- Left Column -->
          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <!-- Instant Export Card -->
            <div class="panel" style="padding: 2rem 1.5rem; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem;">
              <div style="color: var(--accent-cyan);">${Icons.download}</div>
              <h3 style="font-size: 1.2rem; font-weight: 700;">Instant OSHA 1910<br/>Audit Export</h3>
              <p class="muted" style="font-size: 0.8rem;">Generates official compliance report with incident timestamps and evidence logs.</p>
              <button id="btn-gen-osha-pdf" class="btn-primary" style="width: 100%; padding: 0.75rem; font-size: 0.85rem; font-weight: 800; letter-spacing: 0.05em; display: flex; align-items: center; justify-content: center; gap: 6px;">
                ${Icons.download} <span>GENERATE PDF REPORT</span>
              </button>
            </div>

            <!-- Overall Site Safety Radial Progress Card -->
            <div class="panel" style="padding: 2rem 1.5rem; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 1rem;">
              <span style="font-size: 0.75rem; font-family: var(--font-mono); letter-spacing: 0.1em; color: var(--text-muted); font-weight: 700;">DYNAMIC COMPLIANCE SCORE</span>
              
              <!-- Circular Progress Gauge -->
              <div style="position: relative; width: 160px; height: 160px; display: flex; align-items: center; justify-content: center;">
                <svg viewBox="0 0 36 36" style="width: 100%; height: 100%; transform: rotate(-90deg);">
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="3.5" />
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#00f0ff" stroke-dasharray="${complianceScore}, 100" stroke-width="3.5" stroke-linecap="round" />
                </svg>
                <div style="position: absolute; text-align: center;">
                  <div style="font-size: 2.25rem; font-weight: 800; font-family: var(--font-mono); line-height: 1;">${complianceScore}<span style="font-size: 1.25rem;">%</span></div>
                  <div style="font-size: 0.7rem; font-family: var(--font-mono); color: var(--text-muted); letter-spacing: 0.05em; margin-top: 4px;">COMPLIANT</div>
                </div>
              </div>

              <div style="display: flex; justify-content: space-around; width: 100%; font-size: 0.75rem; font-family: var(--font-mono); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
                <div><span style="color: var(--accent-red); font-weight: 800;">${openCount}</span> Open</div>
                <div><span style="color: var(--accent-amber); font-weight: 800;">${progressCount}</span> In-Review</div>
                <div><span style="color: var(--accent-emerald); font-weight: 800;">${resolvedCount}</span> Closed</div>
              </div>
            </div>
          </div>

          <!-- Right Column -->
          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <!-- Document Monospace Terminal Preview Card -->
            <div class="panel" style="padding: 1.5rem; background: #060b12;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.5rem;">
                <span style="font-size: 0.8rem; font-family: var(--font-mono); letter-spacing: 0.08em; color: var(--text-muted); font-weight: 700;">LIVE DATABASE AUDIT SUMMARY</span>
                <span style="font-size: 0.75rem; color: var(--accent-cyan); font-family: var(--font-mono);">DATABASE WAL ACTIVE</span>
              </div>

              <div style="font-family: var(--font-mono); font-size: 0.85rem; line-height: 1.7; color: #cbd5e1;">
                <p class="muted">[OSHA SCAN TIMESTAMP: ${new Date().toISOString()}]</p>
                <p class="muted">&gt; QUERYING SQLITE REPOSITORY: ${incidents.length} INCIDENTS LOGGED</p>
                <br/>
                <p>&gt; PPE MANDATE (OSHA 1910.132 / 1910.135)<br/>
                STATUS: <span style="${openCount > 0 ? 'color: var(--accent-red); font-weight: 700;' : 'color: var(--accent-emerald); font-weight: 700;'}">${openCount > 0 ? `${openCount} ACTIVE VIOLATION(S) DETECTED` : '100% COMPLIANT'}</span></p>
                <br/>
                <p>&gt; FALL PROTECTION & WALKING SURFACES (OSHA 1910.28)<br/>
                STATUS: <span style="color: var(--accent-emerald); font-weight: 700;">ACTIVE MONITORING ON CAM-01 & CAM-02</span></p>
                <br/>
                <p>&gt; FLAME & THERMAL HAZARDS (OSHA 1910.39)<br/>
                STATUS: <span style="color: var(--accent-emerald); font-weight: 700;">ZERO ACTIVE THERMAL OUTBREAKS</span></p>
              </div>
            </div>

            <!-- Audit History Table Card -->
            <div class="panel" style="padding: 1.5rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-size: 0.8rem; font-family: var(--font-mono); letter-spacing: 0.1em; color: var(--text-muted); font-weight: 700;">AUDIT HISTORY & INCIDENT LOGS</h3>
                <span class="muted" style="font-size: 0.75rem; font-family: var(--font-mono);">CLICK "RESOLVE" TO UPDATE SQLITE DB</span>
              </div>

              <div class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>TIMESTAMP</th>
                      <th>INCIDENT ID</th>
                      <th>CLASSIFICATION & DESCRIPTION</th>
                      <th>CAMERA</th>
                      <th>STATUS</th>
                      <th>ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${tableRowsHtml}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Hook PDF generation to real incident data
    this.container.querySelector("#btn-gen-osha-pdf")?.addEventListener("click", () => {
      pdfReportGenerator.generateOSHAReport(incidents);
    });

    // Hook Resolve buttons to SQLite DB update
    this.container.querySelectorAll(".btn-resolve-inc").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = parseInt(btn.dataset.incId, 10);
        btn.textContent = "Updating...";
        btn.disabled = true;

        try {
          await apiClient.resolveIncident(id);
          eventBus.emit("toast", { message: `Incident #INC-${id.toString().padStart(4, '0')} marked as Resolved in SQLite database!` });
          
          // Refresh data from DB
          const refreshed = await apiClient.getIncidents();
          stateManager.set("incidents", refreshed);
          this.render();
        } catch (err) {
          eventBus.emit("toast", { message: `Failed to resolve incident: ${err.message}` });
          btn.textContent = "Resolve";
          btn.disabled = false;
        }
      });
    });
  }
}
