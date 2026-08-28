// CanvasHUD.js - Interactive HTML5 Canvas Danger Zone Perimeter Editor
import { stateManager } from "../core/StateManager.js";
import { apiClient } from "../core/ApiClient.js";
import { eventBus } from "../core/EventBus.js";

export class CanvasHUD {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext("2d") : null;
    this._init();
  }

  _init() {
    if (!this.canvas) return;
    this.resize();
    window.addEventListener("resize", () => this.resize());
    this.canvas.addEventListener("click", (e) => this._onClick(e));
  }

  resize() {
    if (!this.canvas || !this.canvas.parentElement) return;
    this.canvas.width = this.canvas.parentElement.clientWidth;
    this.canvas.height = this.canvas.parentElement.clientHeight;
    this.render();
  }

  render() {
    if (!this.ctx) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    const zones = stateManager.get("zones") || [];
    const draft = stateManager.get("zoneDraftPoints") || [];

    // Render Saved Danger Zones
    zones.forEach((zone) => {
      if (!zone.points || zone.points.length < 3) return;
      this.ctx.beginPath();
      this.ctx.moveTo(zone.points[0][0] * this.canvas.width, zone.points[0][1] * this.canvas.height);
      for (let i = 1; i < zone.points.length; i++) {
        this.ctx.lineTo(zone.points[i][0] * this.canvas.width, zone.points[i][1] * this.canvas.height);
      }
      this.ctx.closePath();
      this.ctx.fillStyle = "rgba(255, 51, 102, 0.25)";
      this.ctx.fill();
      this.ctx.lineWidth = 2;
      this.ctx.strokeStyle = "rgba(255, 51, 102, 0.85)";
      this.ctx.stroke();

      // Label
      const p0 = zone.points[0];
      this.ctx.font = "600 12px 'IBM Plex Mono', monospace";
      this.ctx.fillStyle = "#ff3366";
      this.ctx.fillText(zone.name || "Restricted Zone", p0[0] * this.canvas.width + 6, p0[1] * this.canvas.height + 16);
    });

    // Render In-Progress Draft Polygon
    if (draft.length > 0) {
      this.ctx.beginPath();
      this.ctx.moveTo(draft[0][0] * this.canvas.width, draft[0][1] * this.canvas.height);
      for (let i = 1; i < draft.length; i++) {
        this.ctx.lineTo(draft[i][0] * this.canvas.width, draft[i][1] * this.canvas.height);
      }
      this.ctx.strokeStyle = "rgba(0, 240, 255, 0.9)";
      this.ctx.lineWidth = 2;
      this.ctx.setLineDash([4, 4]);
      this.ctx.stroke();
      this.ctx.setLineDash([]);

      draft.forEach((p) => {
        this.ctx.beginPath();
        this.ctx.arc(p[0] * this.canvas.width, p[1] * this.canvas.height, 5, 0, Math.PI * 2);
        this.ctx.fillStyle = "#00f0ff";
        this.ctx.fill();
      });
    }
  }

  _onClick(e) {
    const isDrawing = stateManager.get("isDrawingZone");
    if (!isDrawing) return;

    const rect = this.canvas.getBoundingClientRect();
    const nx = (e.clientX - rect.left) / rect.width;
    const ny = (e.clientY - rect.top) / rect.height;

    const draft = [...stateManager.get("zoneDraftPoints"), [nx, ny]];
    stateManager.set("zoneDraftPoints", draft);
    this.render();

    if (draft.length >= 4) {
      // Auto-save zone
      const zones = stateManager.get("zones") || [];
      const camId = stateManager.get("selectedCameraId") || 0;
      const zonePayload = {
        name: `Danger Zone #${zones.length + 1}`,
        camera_id: camId,
        points: draft,
      };

      apiClient.saveZone(zonePayload).then(() => {
        stateManager.set("zones", [...zones, zonePayload]);
        stateManager.set("zoneDraftPoints", []);
        stateManager.set("isDrawingZone", false);
        this.render();
        eventBus.emit("toast", { message: "Restricted Zone Saved & Armed!" });
      });
    }
  }
}
