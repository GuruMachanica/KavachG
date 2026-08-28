// IncidentsView.js - OSHA 1910 Compliance & Audit Management (No Emojis)
import { BaseView } from "./BaseView.js";
import { stateManager } from "../core/StateManager.js";
import { pdfReportGenerator } from "../core/PDFReportGenerator.js";
import { eventBus } from "../core/EventBus.js";
import { Icons } from "../ui/Icons.js";

export class IncidentsView extends BaseView {
  constructor() {
    super("tab-incidents");
  }

  render() {
    if (!this.container) return;

    const complianceScore = 92;

    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <!-- Header -->
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;">OSHA 1910 Compliance</h1>
          <p class="muted" style="font-size: 0.9rem;">Continuous monitoring and automated audit generation for Subpart D, I, and J.</p>
        </div>

        <!-- Main Split: Left Export & Score Cards | Right Document Preview & Audit History -->
        <div style="display: grid; grid-template-columns: 340px 1fr; gap: 1.5rem; align-items: start;">
          <!-- Left Column -->
          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <!-- Instant Export Card -->
            <div class="panel" style="padding: 2rem 1.5rem; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem;">
              <div style="color: var(--accent-cyan);">${Icons.download}</div>
              <h3 style="font-size: 1.2rem; font-weight: 700;">Instant OSHA 1910<br/>Audit Export</h3>
              <button id="btn-gen-osha-pdf" class="btn-primary" style="width: 100%; padding: 0.75rem; font-size: 0.85rem; font-weight: 800; letter-spacing: 0.05em; display: flex; align-items: center; justify-content: center; gap: 6px;">
                ${Icons.download} <span>GENERATE PDF REPORT</span>
              </button>
            </div>

            <!-- Overall Site Safety Radial Progress Card -->
            <div class="panel" style="padding: 2rem 1.5rem; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 1rem;">
              <span style="font-size: 0.75rem; font-family: var(--font-mono); letter-spacing: 0.1em; color: var(--text-muted); font-weight: 700;">OVERALL SITE SAFETY</span>
              
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
            </div>
          </div>

          <!-- Right Column -->
          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <!-- Document Monospace Terminal Preview Card -->
            <div class="panel" style="padding: 1.5rem; background: #060b12;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.5rem;">
                <span style="font-size: 0.8rem; font-family: var(--font-mono); letter-spacing: 0.08em; color: var(--text-muted); font-weight: 700;">DOCUMENT PREVIEW: REPORT #882-A</span>
                <span style="font-size: 0.9rem; color: var(--accent-cyan); cursor: pointer;" title="Open Popout">↗</span>
              </div>

              <div style="font-family: var(--font-mono); font-size: 0.85rem; line-height: 1.7; color: #cbd5e1;">
                <p class="muted">[SYSTEM LOG: ${new Date().toISOString()}]</p>
                <p class="muted">INITIATING OSHA 1910 SUBPART D SCAN...</p>
                <br/>
                <p>&gt; WALKING-WORKING SURFACES (1910.22)<br/>
                STATUS: <span style="color: var(--accent-emerald); font-weight: 700;">COMPLIANT</span>. Housekeeping maintained. No protruding hazards detected in Sector 4.</p>
                <br/>
                <p>&gt; FALL PROTECTION SYSTEMS (1910.28)<br/>
                STATUS: <span style="color: var(--accent-amber); font-weight: 700;">WARNING</span>. Guardrail system at Bay 12 requires tension adjustment.<br/>
                ACTION REQUIRED: Maintenance work order #492 dispatched.</p>
                <br/>
                <p>&gt; HAZARD COMMUNICATION (1910.1200)<br/>
                STATUS: <span style="color: var(--accent-emerald); font-weight: 700;">COMPLIANT</span>. All chemical labels legible and updated.</p>
              </div>
            </div>

            <!-- Audit History Table Card -->
            <div class="panel" style="padding: 1.5rem;">
              <h3 style="font-size: 0.8rem; font-family: var(--font-mono); letter-spacing: 0.1em; color: var(--text-muted); font-weight: 700; margin-bottom: 1rem;">AUDIT HISTORY</h3>

              <div class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>DATE</th>
                      <th>REPORT ID</th>
                      <th>SCORE</th>
                      <th>INSPECTOR</th>
                      <th>ACTION</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style="font-family: var(--font-mono);">2026-08-28</td>
                      <td style="color: var(--accent-cyan); font-family: var(--font-mono);">#882-A</td>
                      <td><span class="badge" style="background: rgba(0,240,255,0.15); color: var(--accent-cyan);">92%</span></td>
                      <td>AI Auto-Scan</td>
                      <td><button class="btn-secondary btn-view-audit" style="padding: 3px 8px; font-size: 0.75rem;" data-report="882-A">View</button></td>
                    </tr>
                    <tr>
                      <td style="font-family: var(--font-mono);">2026-08-27</td>
                      <td style="color: var(--accent-cyan); font-family: var(--font-mono);">#881-A</td>
                      <td><span class="badge" style="background: rgba(255,183,3,0.15); color: var(--accent-amber);">88%</span></td>
                      <td>AI Auto-Scan</td>
                      <td><button class="btn-secondary btn-view-audit" style="padding: 3px 8px; font-size: 0.75rem;" data-report="881-A">View</button></td>
                    </tr>
                    <tr>
                      <td style="font-family: var(--font-mono);">2026-08-26</td>
                      <td style="color: var(--accent-cyan); font-family: var(--font-mono);">#880-M</td>
                      <td><span class="badge" style="background: rgba(0,240,255,0.15); color: var(--accent-cyan);">95%</span></td>
                      <td>S. Connor</td>
                      <td><button class="btn-secondary btn-view-audit" style="padding: 3px 8px; font-size: 0.75rem;" data-report="880-M">View</button></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.container.querySelector("#btn-gen-osha-pdf")?.addEventListener("click", () => {
      eventBus.emit("toast", { message: "Generating Certified OSHA Form 301 PDF..." });
      pdfReportGenerator.generateIncidentReport({
        id: "882-A",
        type: "OSHA 1910 Composite Plant Audit",
        description: "Automated optical edge verification of walking surfaces, fall arrest gear, and PPE compliance.",
        created_at: new Date().toISOString(),
        camera_id: 0,
        status: "Compliant (92%)",
        confidence: 0.96,
      });
    });

    this.container.querySelectorAll(".btn-view-audit").forEach((btn) => {
      btn.addEventListener("click", () => {
        const rId = btn.dataset.report;
        pdfReportGenerator.generateIncidentReport({
          id: rId,
          type: "Shift Safety Audit Archive",
          description: `Historical OSHA 1910 audit report #${rId}`,
          created_at: new Date().toISOString(),
          camera_id: 0,
          status: "Archived",
          confidence: 0.94,
        });
      });
    });
  }
}
