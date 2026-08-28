// DigitalTwinView.js - Sector Alpha 3D Radar & Environmental Telemetry (No Emojis)
import { BaseView } from "./BaseView.js";
import { stateManager } from "../core/StateManager.js";
import { PlantDigitalTwin } from "../ui/PlantDigitalTwin.js";
import { eventBus } from "../core/EventBus.js";
import { Icons } from "../ui/Icons.js";

export class DigitalTwinView extends BaseView {
  constructor() {
    super("tab-digitaltwin");
    this.twin = null;
  }

  render() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
          <div>
            <h1 style="font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;">Sector Alpha</h1>
            <p class="muted" style="font-size: 0.9rem;">Core Manufacturing Unit — Spatial IoT & Environmental Telemetry.</p>
          </div>

          <div style="display: flex; gap: 0.75rem; font-size: 0.75rem; font-family: var(--font-mono); background: rgba(6,10,15,0.8); padding: 4px 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <span style="color: var(--accent-cyan);">● Active Nodes: 12</span>
            <span style="color: var(--accent-amber);">● Warnings: 1</span>
            <span style="color: var(--accent-cyan);">Status: <strong style="color: #fff;">SCANNING</strong></span>
          </div>
        </div>

        <!-- 3D Radar Digital Twin Viewport (with Floating Alert Card) -->
        <div class="panel" style="position: relative; height: 440px; border-radius: 16px; overflow: hidden; background: radial-gradient(circle at center, #091a2a 0%, #03080e 100%);">
          <div id="twin-viewport" style="width: 100%; height: 100%;"></div>

          <!-- Floating Error Notification Card -->
          <div style="position: absolute; top: 20px; right: 20px; width: 280px; background: rgba(15, 23, 42, 0.95); border: 1px solid var(--accent-amber); border-radius: 8px; padding: 0.9rem; box-shadow: 0 0 25px rgba(255, 183, 3, 0.2); backdrop-filter: blur(12px);">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: var(--font-mono); margin-bottom: 0.35rem;">
              <span style="color: var(--accent-amber); font-weight: 700;">#ERR-Acoustic-99</span>
              <span class="muted">2m ago</span>
            </div>
            <p style="font-size: 0.8rem; line-height: 1.4; color: #cbd5e1; margin-bottom: 0.6rem;">
              Elevated DB levels detected near Compressor Unit B. Maintenance advised.
            </p>
            <a href="#investigate" id="twin-alert-investigate" style="color: var(--accent-cyan); font-size: 0.75rem; font-weight: 700; text-decoration: none;">
              Investigate →
            </a>
          </div>
        </div>

        <!-- 3 Environmental IoT Telemetry KPI Cards -->
        <div class="kpi-grid">
          <!-- Thermal Signature -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="color: var(--accent-cyan);">${Icons.thermal}</span>
                <span class="kpi-title">Thermal Signature</span>
              </div>
              <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-cyan);">NOMINAL</span>
            </div>
            <div class="kpi-val-row">
              <span class="kpi-value">42° <span style="font-size: 1.25rem; font-weight: 400; color: var(--text-muted);">C</span></span>
            </div>
            <div class="kpi-bar">
              <div class="kpi-bar-fill-cyan" style="width: 42%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.65rem; font-family: var(--font-mono); color: var(--text-muted);">
              <span>0°C</span>
              <span>100°C</span>
            </div>
          </div>

          <!-- Acoustic Levels -->
          <div class="kpi-card" style="border-color: rgba(255, 183, 3, 0.4);">
            <div class="kpi-header">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="color: var(--accent-amber);">${Icons.acoustic}</span>
                <span class="kpi-title">Acoustic Levels</span>
              </div>
              <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-amber);">WARNING</span>
            </div>
            <div class="kpi-val-row">
              <span class="kpi-value" style="color: var(--accent-amber);">88 <span style="font-size: 1.25rem; font-weight: 400; color: var(--text-muted);">dB</span></span>
            </div>
            <div style="display: flex; gap: 4px;">
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-cyan); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-amber); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.65rem; font-family: var(--font-mono); color: var(--text-muted);">
              <span>Normal</span>
              <span style="color: var(--accent-amber);">Threshold Near</span>
            </div>
          </div>

          <!-- Air Quality -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="color: var(--accent-emerald);">${Icons.airQuality}</span>
                <span class="kpi-title">Air Quality (VOC)</span>
              </div>
              <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-emerald);">EXCELLENT</span>
            </div>
            <div class="kpi-val-row">
              <span class="kpi-value">0.02 <span style="font-size: 1rem; font-weight: 400; color: var(--text-muted);">ppm</span></span>
            </div>
            <div style="display: flex; gap: 3px;">
              <div style="flex: 1; height: 4px; background: var(--accent-emerald); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-emerald); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-emerald); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-emerald); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-emerald); border-radius: 2px;"></div>
              <div style="flex: 1; height: 4px; background: var(--accent-emerald); border-radius: 2px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.65rem; font-family: var(--font-mono); color: var(--text-muted);">
              <span>Clean</span>
              <span>Hazardous</span>
            </div>
          </div>
        </div>
      </div>
    `;

    const viewportEl = this.container.querySelector("#twin-viewport");
    if (viewportEl) {
      if (this.twin) this.twin.destroy();
      this.twin = new PlantDigitalTwin(viewportEl);
    }

    this.container.querySelector("#twin-alert-investigate")?.addEventListener("click", (e) => {
      e.preventDefault();
      stateManager.set("selectedCameraId", 1);
      eventBus.emit("nav:tab", "detection");
      eventBus.emit("toast", { message: "Focusing on Compressor Unit B (Camera #1)" });
    });
  }
}
