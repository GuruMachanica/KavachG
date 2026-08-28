// DetectionView.js - Live Camera Stream & Multi-Mode Computer Vision Visualizer
import { BaseView } from "./BaseView.js";
import { stateManager } from "../core/StateManager.js";
import { apiClient } from "../core/ApiClient.js";
import { eventBus } from "../core/EventBus.js";
import { StreamManager } from "../ui/StreamManager.js";
import { CanvasHUD } from "../ui/CanvasHUD.js";
import { HeatmapEngine } from "../ui/HeatmapEngine.js";
import { Icons } from "../ui/Icons.js";

export class DetectionView extends BaseView {
  constructor() {
    super("tab-detection");
    this.streamManager = null;
    this.canvasHUD = null;
    this.heatmapEngine = null;
    this.viewMode = "single";
    this.heatmapActive = false;
  }

  render() {
    if (!this.container) return;

    const activeMode = stateManager.get("liveMode") || "video_feed";
    const modes = [
      { id: "video_feed", label: "Raw Video", desc: "Unprocessed live optical camera feed" },
      { id: "live/ppe", label: "PPE Compliance", desc: "Live hardhat, safety vest & mask IoU bounding" },
      { id: "live/fire-smoke", label: "Fire & Smoke", desc: "Thermal & optical flame hazard localization" },
      { id: "live/fall", label: "Fall Detection", desc: "Temporal skeletal velocity & pose angle" },
      { id: "live/pose", label: "Skeletal Pose", desc: "17-point full-body keypoint tracking" },
    ];

    const cameras = stateManager.get("cameras") || [];
    const selectedCam = stateManager.get("selectedCameraId") || 0;
    const token = stateManager.get("token");

    const singleCamHtml = `
      <div class="viewport-container panel">
        <img id="live-stream-img" class="live-stream-img" alt="Live Camera Stream" />
        <video id="live-local-video" class="live-stream-img" autoplay playsinline muted style="display:none;"></video>
        <canvas id="zone-canvas" class="canvas-overlay"></canvas>
        <canvas id="heatmap-canvas" class="canvas-overlay" style="pointer-events: none; ${this.heatmapActive ? "" : "display:none;"}"></canvas>

        <div class="viewport-hud">
          <div class="stream-status-badge">
            <span class="pulse-dot"></span>
            <span id="stream-status-text">CONNECTING LIVE CAMERA...</span>
          </div>

          <div class="mode-selector">
            ${modes.map((m) => `
              <button class="mode-btn ${activeMode === m.id ? "active" : ""}" data-mode="${m.id}" title="${m.desc}">
                ${m.label}
              </button>
            `).join("")}
          </div>
        </div>
      </div>
    `;

    const matrixHtml = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 240px 240px; gap: 0.75rem; width: 100%;">
        ${[0, 1, 2, 3].map((camIdx) => `
          <div class="panel" style="position: relative; border-radius: 12px; overflow: hidden; background: #000; cursor: pointer;" data-matrix-cam="${camIdx}">
            <img src="${apiClient.getStreamUrl(activeMode, token)}&cam=${camIdx}&_t=${Date.now()}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='assets/cctv_factory_${(camIdx % 2) + 1}.jpg'" />
            <div style="position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.75); padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-family: var(--font-mono); color: var(--accent-cyan); border: 1px solid var(--border-subtle);">
              Camera #${camIdx} ${camIdx === selectedCam ? "• ACTIVE" : ""}
            </div>
            <div style="position: absolute; bottom: 8px; right: 8px; font-size: 0.7rem; color: #fff; background: rgba(0,0,0,0.6); padding: 2px 6px; border-radius: 4px;">
              Click to Focus
            </div>
          </div>
        `).join("")}
      </div>
    `;

    const cameraOptions = `
      <option value="0" ${selectedCam === 0 ? "selected" : ""}>Camera 0 (Live Hardware Cam / Primary Edge)</option>
      <option value="webcam" ${selectedCam === "webcam" ? "selected" : ""}>Direct Local Device Webcam (Browser)</option>
      <option value="1" ${selectedCam === 1 ? "selected" : ""}>Camera 1 (Sector B Assembly Line)</option>
      <option value="2" ${selectedCam === 2 ? "selected" : ""}>Camera 2 (Sector C Substation)</option>
      <option value="3" ${selectedCam === 3 ? "selected" : ""}>Camera 3 (Sector D Logistics Bay)</option>
    `;

    this.container.innerHTML = `
      <div class="detection-grid">
        <!-- Main Viewport or Matrix -->
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; gap: 0.4rem;">
              <button id="view-single-btn" class="btn-secondary ${this.viewMode === "single" ? "btn-primary" : ""}" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;">
                Single Focus
              </button>
              <button id="view-matrix-btn" class="btn-secondary ${this.viewMode === "matrix" ? "btn-primary" : ""}" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;">
                Quad Matrix (2×2)
              </button>
              <button id="toggle-heatmap-btn" class="btn-secondary ${this.heatmapActive ? "btn-primary" : ""}" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;">
                Heatmap: ${this.heatmapActive ? "ON" : "OFF"}
              </button>
            </div>
          </div>

          ${this.viewMode === "single" ? singleCamHtml : matrixHtml}
        </div>

        <!-- Controls Sidebar -->
        <div class="panel side-card">
          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
              <span style="color: var(--accent-cyan);">${Icons.camera}</span>
              <h3 style="font-size: 1rem;">Camera Control</h3>
            </div>
            <p class="muted" style="font-size: 0.8rem; margin-bottom: 0.5rem;">Select active edge stream feed</p>
            <select id="camera-select-dropdown" style="width: 100%; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid var(--border-subtle); padding: 0.5rem; border-radius: 8px;">
              ${cameraOptions}
            </select>
          </div>

          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
              <span style="color: var(--accent-cyan);">${Icons.shield}</span>
              <h3 style="font-size: 1rem;">Danger Perimeter Fence</h3>
            </div>
            <p class="muted" style="font-size: 0.8rem; margin-bottom: 0.5rem;">Draw virtual polygon intrusion fences</p>
            <div style="display: flex; gap: 0.4rem;">
              <button id="draw-zone-btn" class="btn-secondary" style="flex: 1;">Draw Zone</button>
              <button id="clear-zone-btn" class="btn-secondary">Clear</button>
            </div>
            <div id="zone-status-msg" class="muted" style="font-size: 0.75rem; margin-top: 0.4rem;">Click "Draw Zone" then click 4 points on video.</div>
          </div>

          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
              <span style="color: var(--accent-cyan);">${Icons.settings}</span>
              <h3 style="font-size: 1rem;">Autonomous Watchdog</h3>
            </div>
            <p class="muted" style="font-size: 0.8rem; margin-bottom: 0.5rem;">Self-healing background capture engine active.</p>
            <button id="reconnect-stream-btn" class="btn-primary" style="width: 100%; font-size: 0.85rem; padding: 0.5rem;">Force Stream Reset / Reconnect</button>
          </div>
        </div>
      </div>
    `;

    if (this.viewMode === "single") {
      const imgEl = this.container.querySelector("#live-stream-img");
      const videoEl = this.container.querySelector("#live-local-video");
      const badgeEl = this.container.querySelector("#stream-status-text");
      const canvasEl = this.container.querySelector("#zone-canvas");
      const heatEl = this.container.querySelector("#heatmap-canvas");

      this.streamManager = new StreamManager(imgEl, badgeEl, videoEl);

      if (selectedCam === "webcam") {
        this.streamManager.startLocalWebcam(videoEl);
      } else {
        this.streamManager.connect(activeMode);
      }

      this.canvasHUD = new CanvasHUD(canvasEl);

      if (heatEl) {
        heatEl.width = canvasEl.parentElement.clientWidth;
        heatEl.height = canvasEl.parentElement.clientHeight;
        this.heatmapEngine = new HeatmapEngine(heatEl);
        this.heatmapEngine.addPoint(0.4, 0.5, 0.9);
        this.heatmapEngine.addPoint(0.42, 0.55, 0.8);
        this.heatmapEngine.addPoint(0.7, 0.6, 0.7);
        this.heatmapEngine.render();
      }
    }

    // Single / Matrix Toggle
    this.container.querySelector("#view-single-btn")?.addEventListener("click", () => {
      this.viewMode = "single";
      this.render();
    });
    this.container.querySelector("#view-matrix-btn")?.addEventListener("click", () => {
      this.viewMode = "matrix";
      this.render();
    });
    this.container.querySelector("#toggle-heatmap-btn")?.addEventListener("click", () => {
      this.heatmapActive = !this.heatmapActive;
      this.render();
    });

    // Mode Selector Buttons
    this.container.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.dataset.mode;
        stateManager.set("liveMode", mode);
        this.container.querySelectorAll(".mode-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        if (this.streamManager) {
          this.streamManager.connect(mode);
        }
      });
    });

    // Camera Dropdown Switcher
    this.container.querySelector("#camera-select-dropdown")?.addEventListener("change", async (e) => {
      const val = e.target.value;
      if (val === "webcam") {
        stateManager.set("selectedCameraId", "webcam");
        const videoEl = this.container.querySelector("#live-local-video");
        if (this.streamManager) this.streamManager.startLocalWebcam(videoEl);
      } else {
        const camId = parseInt(val, 10);
        stateManager.set("selectedCameraId", camId);
        try {
          await apiClient.setCamera(camId);
        } catch (_) {}
        if (this.streamManager) {
          this.streamManager.stopLocalWebcam();
          this.streamManager.connect(stateManager.get("liveMode") || "video_feed");
        }
      }
    });

    // Force Stream Reset
    this.container.querySelector("#reconnect-stream-btn")?.addEventListener("click", () => {
      if (this.streamManager) {
        this.streamManager.forceReset();
        eventBus.emit("toast", { message: "Resetting optical video stream engine..." });
      }
    });

    // Danger Zone Polygon Tool
    const drawBtn = this.container.querySelector("#draw-zone-btn");
    const clearBtn = this.container.querySelector("#clear-zone-btn");
    const statusMsg = this.container.querySelector("#zone-status-msg");

    drawBtn?.addEventListener("click", () => {
      if (this.canvasHUD) {
        this.canvasHUD.startDrawing((points) => {
          if (statusMsg) statusMsg.textContent = `Polygon Perimeter active: ${points.length} vertices locked.`;
          drawBtn.classList.remove("btn-primary");
        });
        drawBtn.classList.add("btn-primary");
        if (statusMsg) statusMsg.textContent = "Click 4 points on the viewport to define exclusion zone.";
      }
    });

    clearBtn?.addEventListener("click", () => {
      if (this.canvasHUD) {
        this.canvasHUD.clear();
        if (statusMsg) statusMsg.textContent = "Exclusion fence cleared.";
      }
    });
  }

  destroy() {
    if (this.streamManager) {
      this.streamManager.disconnect();
    }
  }
}
