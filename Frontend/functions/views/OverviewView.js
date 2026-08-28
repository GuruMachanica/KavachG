// OverviewView.js - Command Center Main Dashboard (Zero Old Graphics, High-Res CCTV)
import { BaseView } from "./BaseView.js";
import { stateManager } from "../core/StateManager.js";
import { apiClient } from "../core/ApiClient.js";
import { eventBus } from "../core/EventBus.js";
import { Icons } from "../ui/Icons.js";

export class OverviewView extends BaseView {
  constructor() {
    super("tab-overview");
  }

  render() {
    if (!this.container) return;

    const incidents = stateManager.get("incidents") || [];
    const token = stateManager.get("token");
    const openCount = incidents.filter((i) => i.status === "Open").length;

    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
          <div>
            <h1 style="font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;">Command Center</h1>
            <p class="muted" style="font-size: 0.9rem;">Real-time safety monitoring and anomaly detection.</p>
          </div>
          <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; font-family: var(--font-mono); color: var(--text-muted); background: rgba(255,255,255,0.03); padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-subtle);">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span>Last sync: 2s ago</span>
          </div>
        </div>

        <!-- 3 KPI Metric Cards -->
        <div class="kpi-grid">
          <!-- Active Workers -->
          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">ACTIVE WORKERS</span>
              <span style="color: var(--accent-cyan);">${Icons.users}</span>
            </div>
            <div class="kpi-val-row">
              <span class="kpi-value">142</span>
              <span class="kpi-trend kpi-trend-cyan">↗ 12%</span>
            </div>
            <div class="kpi-bar">
              <div class="kpi-bar-fill-cyan" style="width: 78%;"></div>
            </div>
          </div>

          <!-- Hazard Frequency -->
          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">HAZARD FREQUENCY</span>
              <span style="color: var(--accent-amber);">${Icons.alertTriangle}</span>
            </div>
            <div class="kpi-val-row">
              <span class="kpi-value">${openCount > 0 ? (openCount * 0.4).toFixed(1) : "0.8"}<span style="font-size: 1rem; color: var(--text-muted);">/hr</span></span>
              <span class="kpi-trend kpi-trend-amber">↘ 5%</span>
            </div>
            <div class="kpi-bar">
              <div class="kpi-bar-fill-amber" style="width: ${Math.min(100, Math.max(20, openCount * 25))}%;"></div>
            </div>
          </div>

          <!-- System Uptime -->
          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">SYSTEM UPTIME</span>
              <span style="color: var(--accent-emerald);">${Icons.shield}</span>
            </div>
            <div class="kpi-val-row">
              <span class="kpi-value">99.9<span style="font-size: 1.2rem;">%</span></span>
              <span style="font-size: 0.8rem; color: var(--accent-emerald); font-weight: 600;">Stable</span>
            </div>
            <div style="display: flex; gap: 4px;">
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: rgba(0, 240, 255, 0.4); border-radius: 2px;"></div>
            </div>
          </div>
        </div>

        <!-- Main Middle Split: Quad Cam Feeds + Live Telemetry Feed -->
        <div style="display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.5rem; align-items: start;">
          <!-- 2x2 Surveillance Matrix -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 240px 240px; gap: 1rem;">
            <!-- CAM-01 -->
            <div class="panel" style="position: relative; overflow: hidden; border-radius: 12px; background: #000; cursor: pointer;" data-jump-cam="0">
              <img src="assets/cctv_factory_1.jpg" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='assets/cctv_factory_1.jpg'" />
              
              <div style="position: absolute; top: 10px; left: 10px; background: rgba(6,10,15,0.85); border: 1px solid var(--border-subtle); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-family: var(--font-mono); color: #fff; display: flex; align-items: center; gap: 6px;">
                <span class="pulse-dot"></span> <span>CAM-01</span>
              </div>
              <div style="position: absolute; top: 10px; right: 10px; background: rgba(0, 229, 163, 0.2); border: 1px solid var(--accent-emerald); color: var(--accent-emerald); font-size: 0.7rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.05em;">
                COMPLIANT
              </div>
              <div style="position: absolute; bottom: 10px; left: 10px; font-size: 0.7rem; color: var(--accent-cyan); font-family: var(--font-mono); background: rgba(0,0,0,0.7); padding: 2px 6px; border-radius: 4px;">
                PPE: ALL OK (10 ENTITIES)
              </div>
            </div>

            <!-- CAM-02 (Hazard Detected) -->
            <div class="panel" style="position: relative; overflow: hidden; border-radius: 12px; background: #000; border-color: rgba(255, 183, 3, 0.5); cursor: pointer;" data-jump-cam="1">
              <img src="assets/cctv_factory_2.jpg" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='assets/cctv_factory_2.jpg'" />
              
              <div style="position: absolute; top: 10px; left: 10px; background: rgba(6,10,15,0.85); border: 1px solid var(--border-subtle); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-family: var(--font-mono); color: #fff; display: flex; align-items: center; gap: 6px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: var(--accent-amber);"></span> <span>CAM-02</span>
              </div>
              <div style="position: absolute; top: 10px; right: 10px; background: rgba(255, 183, 3, 0.25); border: 1px solid var(--accent-amber); color: var(--accent-amber); font-size: 0.7rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.05em; animation: pulseGlow 1.5s infinite;">
                HAZARD DETECTED
              </div>
              <div style="position: absolute; bottom: 10px; left: 10px; font-size: 0.7rem; color: var(--accent-amber); font-family: var(--font-mono); background: rgba(0,0,0,0.7); padding: 2px 6px; border-radius: 4px;">
                ACTIVE FORKLIFT EXCLUSION ZONE
              </div>
            </div>

            <!-- CAM-03 -->
            <div class="panel" style="position: relative; overflow: hidden; border-radius: 12px; background: #000; cursor: pointer;" data-jump-cam="2">
              <img src="assets/cctv_factory_1.jpg" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(0.9);" onerror="this.src='assets/cctv_factory_1.jpg'" />
              
              <div style="position: absolute; top: 10px; left: 10px; background: rgba(6,10,15,0.85); border: 1px solid var(--border-subtle); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-family: var(--font-mono); color: #fff; display: flex; align-items: center; gap: 6px;">
                <span class="pulse-dot"></span> <span>CAM-03</span>
              </div>
              <div style="position: absolute; top: 10px; right: 10px; background: rgba(0, 229, 163, 0.2); border: 1px solid var(--accent-emerald); color: var(--accent-emerald); font-size: 0.7rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">
                COMPLIANT
              </div>
              <div style="position: absolute; bottom: 10px; left: 10px; font-size: 0.7rem; color: var(--text-muted); font-family: var(--font-mono); background: rgba(0,0,0,0.7); padding: 2px 6px; border-radius: 4px;">
                GANTRY POSE TRACKING: NOMINAL
              </div>
            </div>

            <!-- CAM-04 -->
            <div class="panel" style="position: relative; overflow: hidden; border-radius: 12px; background: #000; cursor: pointer;" data-jump-cam="3">
              <img src="assets/cctv_factory_2.jpg" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(0.85);" onerror="this.src='assets/cctv_factory_2.jpg'" />
              
              <div style="position: absolute; top: 10px; left: 10px; background: rgba(6,10,15,0.85); border: 1px solid var(--border-subtle); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-family: var(--font-mono); color: #fff; display: flex; align-items: center; gap: 6px;">
                <span class="pulse-dot"></span> <span>CAM-04</span>
              </div>
              <div style="position: absolute; top: 10px; right: 10px; background: rgba(0, 240, 255, 0.2); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); font-size: 0.7rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">
                SCANNING
              </div>
              <div style="position: absolute; bottom: 10px; left: 10px; font-size: 0.7rem; color: var(--accent-cyan); font-family: var(--font-mono); background: rgba(0,0,0,0.7); padding: 2px 6px; border-radius: 4px;">
                SECTOR DUAL SENSOR LINK OK
              </div>
            </div>
          </div>

          <!-- Live Telemetry Stream Panel (Right) -->
          <div class="panel" style="padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; max-height: 495px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.75rem;">
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: var(--accent-cyan); font-size: 0.85rem;">☰</span>
                <h3 style="font-size: 0.95rem; font-weight: 700;">Live Telemetry</h3>
              </div>
              <span style="font-size: 0.7rem; font-family: var(--font-mono); background: rgba(255,255,255,0.06); padding: 2px 8px; border-radius: 4px; color: var(--text-muted);">AUTO-SCROLL ON</span>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem; overflow-y: auto; padding-right: 4px;">
              <!-- HAZ-CRIT -->
              <div style="background: rgba(255, 51, 102, 0.08); border-left: 3px solid var(--accent-red); border-radius: 0 8px 8px 0; padding: 0.75rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: var(--font-mono); margin-bottom: 0.35rem;">
                  <span style="color: var(--accent-red); font-weight: 700;">● HAZ-CRIT</span>
                  <span class="muted">10:42:05</span>
                </div>
                <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">Missing PPE: Hard Hat detected in Sector 4 (Heavy Machining).</p>
                <div style="display: flex; gap: 0.5rem; font-size: 0.7rem; font-family: var(--font-mono);">
                  <span style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px;">CAM-02</span>
                  <span style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; color: var(--accent-emerald);">Logged</span>
                </div>
              </div>

              <!-- SYS-INF -->
              <div style="background: rgba(0, 240, 255, 0.05); border-left: 3px solid var(--accent-cyan); border-radius: 0 8px 8px 0; padding: 0.75rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: var(--font-mono); margin-bottom: 0.35rem;">
                  <span style="color: var(--accent-cyan); font-weight: 700;">● SYS-INF</span>
                  <span class="muted">10:38:12</span>
                </div>
                <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">Routine shift change scan complete. 42 entities logged.</p>
                <div style="display: flex; gap: 0.5rem; font-size: 0.7rem; font-family: var(--font-mono);">
                  <span style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px;">CAM-01</span>
                </div>
              </div>

              <!-- HAZ-WARN -->
              <div style="background: rgba(255, 183, 3, 0.06); border-left: 3px solid var(--accent-amber); border-radius: 0 8px 8px 0; padding: 0.75rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: var(--font-mono); margin-bottom: 0.35rem;">
                  <span style="color: var(--accent-amber); font-weight: 700;">● HAZ-WARN</span>
                  <span class="muted">10:15:44</span>
                </div>
                <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">Proximity alert: Worker near active forklift zone.</p>
                <div style="display: flex; gap: 0.5rem; font-size: 0.7rem; font-family: var(--font-mono);">
                  <span style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px;">CAM-03</span>
                  <span style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; color: var(--accent-amber);">Warning</span>
                </div>
              </div>

              <!-- SYS-INF Start -->
              <div style="background: rgba(255, 255, 255, 0.02); border-left: 3px solid var(--text-muted); border-radius: 0 8px 8px 0; padding: 0.75rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: var(--font-mono); margin-bottom: 0.35rem;">
                  <span style="color: var(--text-muted); font-weight: 700;">● SYS-INF</span>
                  <span class="muted">09:00:00</span>
                </div>
                <p style="font-size: 0.85rem;">System initialized. Models loaded securely.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.container.querySelectorAll("[data-jump-cam]").forEach((card) => {
      card.addEventListener("click", () => {
        const camId = parseInt(card.dataset.jumpCam, 10);
        stateManager.set("selectedCameraId", camId);
        eventBus.emit("nav:tab", "detection");
      });
    });
  }
}
