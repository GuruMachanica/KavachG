// LandingVisualizer.js - Interactive High-FPS Edge AI Detection Simulation for Landing Page
export class LandingVisualizer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext("2d");
    this.mode = "ppe";
    this.animId = null;
    this.scanLineY = 0;
    this.scanDirection = 1;
    this.time = 0;
  }

  init() {
    this._resize();
    window.addEventListener("resize", () => this._resize());
    this._animate();
  }

  setMode(mode) {
    this.mode = mode;
  }

  _resize() {
    if (!this.canvas) return;
    this.canvas.width = this.canvas.parentElement.clientWidth;
    this.canvas.height = this.canvas.parentElement.clientHeight || 420;
  }

  _animate() {
    this.animId = requestAnimationFrame(() => this._animate());
    this.time += 0.02;

    const w = this.canvas.width;
    const h = this.canvas.height;
    const ctx = this.ctx;

    // 1. Dark Factory Floor Grid Background
    ctx.fillStyle = "#050b12";
    ctx.fillRect(0, 0, w, h);

    // Subtle grid lines
    ctx.strokeStyle = "rgba(0, 240, 255, 0.05)";
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x < w; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // 2. Animated Scanning Line
    this.scanLineY += 2 * this.scanDirection;
    if (this.scanLineY > h) this.scanDirection = -1;
    if (this.scanLineY < 0) this.scanDirection = 1;

    const scanGrad = ctx.createLinearGradient(0, this.scanLineY - 30, 0, this.scanLineY + 30);
    scanGrad.addColorStop(0, "rgba(0, 240, 255, 0)");
    scanGrad.addColorStop(0.5, "rgba(0, 240, 255, 0.25)");
    scanGrad.addColorStop(1, "rgba(0, 240, 255, 0)");
    ctx.fillStyle = scanGrad;
    ctx.fillRect(0, this.scanLineY - 30, w, 60);

    ctx.strokeStyle = "rgba(0, 240, 255, 0.7)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, this.scanLineY);
    ctx.lineTo(w, this.scanLineY);
    ctx.stroke();

    // 3. Render Simulated Detections according to Mode
    if (this.mode === "ppe") {
      this._renderPPEMode(w, h);
    } else if (this.mode === "fall") {
      this._renderFallMode(w, h);
    } else if (this.mode === "fire") {
      this._renderFireMode(w, h);
    }

    // 4. Optical HUD Telemetry Overlays
    this._renderHUDOverlay(w, h);
  }

  _renderPPEMode(w, h) {
    const ctx = this.ctx;

    // Worker 1 (Compliant)
    const w1X = w * 0.25 + Math.sin(this.time * 0.5) * 15;
    const w1Y = h * 0.35;
    const w1W = 140;
    const w1H = 220;

    // Bounding box
    ctx.strokeStyle = "#00f0ff";
    ctx.lineWidth = 2;
    ctx.strokeRect(w1X, w1Y, w1W, w1H);

    // Corner brackets
    this._drawCorners(w1X, w1Y, w1W, w1H, "#00f0ff");

    // Tag
    ctx.fillStyle = "#00f0ff";
    ctx.fillRect(w1X, w1Y - 24, w1W, 24);
    ctx.fillStyle = "#030712";
    ctx.font = "bold 11px 'IBM Plex Mono', monospace";
    ctx.fillText("WORKER #01: 98.6%", w1X + 8, w1Y - 8);

    // Sub items
    ctx.fillStyle = "rgba(0, 229, 163, 0.85)";
    ctx.fillText("✔ HELMET [OK]", w1X + 8, w1Y + 20);
    ctx.fillText("✔ VEST [OK]", w1X + 8, w1Y + 36);

    // Worker 2 (Hazard Detected - No Hardhat)
    const w2X = w * 0.65 + Math.cos(this.time * 0.4) * 10;
    const w2Y = h * 0.38;
    const w2W = 140;
    const w2H = 210;

    const pulse = Math.abs(Math.sin(this.time * 4));
    const dangerColor = `rgba(255, 183, 3, ${0.7 + pulse * 0.3})`;

    ctx.strokeStyle = dangerColor;
    ctx.lineWidth = 2.5;
    ctx.strokeRect(w2X, w2Y, w2W, w2H);
    this._drawCorners(w2X, w2Y, w2W, w2H, "#ffb703");

    // Tag
    ctx.fillStyle = "#ffb703";
    ctx.fillRect(w2X, w2Y - 24, w2W, 24);
    ctx.fillStyle = "#030712";
    ctx.font = "bold 11px 'IBM Plex Mono', monospace";
    ctx.fillText("HAZARD: NO HARDHAT", w2X + 8, w2Y - 8);

    ctx.fillStyle = "#ff3366";
    ctx.fillText("✖ HELMET MISSING", w2X + 8, w2Y + 20);
    ctx.fillStyle = "rgba(0, 229, 163, 0.85)";
    ctx.fillText("✔ VEST [OK]", w2X + 8, w2Y + 36);
  }

  _renderFallMode(w, h) {
    const ctx = this.ctx;

    // Skeletal Keypoint Simulation
    const cx = w * 0.5;
    const cy = h * 0.55;

    // Draw joints and bones
    const joints = [
      { x: cx, y: cy - 90 }, // head
      { x: cx, y: cy - 50 }, // neck
      { x: cx - 35, y: cy - 40 }, // l-shoulder
      { x: cx + 35, y: cy - 40 }, // r-shoulder
      { x: cx - 45, y: cy }, // l-elbow
      { x: cx + 45, y: cy }, // r-elbow
      { x: cx - 50, y: cy + 40 }, // l-wrist
      { x: cx + 50, y: cy + 40 }, // r-wrist
      { x: cx, y: cy + 10 }, // pelvis
      { x: cx - 25, y: cy + 70 }, // l-knee
      { x: cx + 25, y: cy + 70 }, // r-knee
      { x: cx - 30, y: cy + 130 }, // l-ankle
      { x: cx + 30, y: cy + 130 }, // r-ankle
    ];

    // Bone links
    ctx.strokeStyle = "#00f0ff";
    ctx.lineWidth = 3;
    const bones = [
      [0, 1], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7],
      [1, 8], [8, 9], [8, 10], [9, 11], [10, 12]
    ];
    bones.forEach(([i, j]) => {
      ctx.beginPath();
      ctx.moveTo(joints[i].x, joints[i].y);
      ctx.lineTo(joints[j].x, joints[j].y);
      ctx.stroke();
    });

    // Joints points
    ctx.fillStyle = "#ffffff";
    joints.forEach((pt) => {
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 4.5, 0, Math.PI * 2);
      ctx.fill();
    });

    // Inclination HUD Box
    ctx.fillStyle = "rgba(13, 22, 33, 0.85)";
    ctx.strokeStyle = "rgba(0, 240, 255, 0.4)";
    ctx.strokeRect(cx - 160, cy - 150, 320, 45);
    ctx.fillRect(cx - 160, cy - 150, 320, 45);

    ctx.fillStyle = "#00f0ff";
    ctx.font = "bold 12px 'IBM Plex Mono', monospace";
    ctx.fillText("POSE STABILITY: NOMINAL (θ = 86.4°)", cx - 145, cy - 128);
    ctx.fillStyle = "rgba(0, 229, 163, 0.85)";
    ctx.font = "11px 'IBM Plex Mono', monospace";
    ctx.fillText("FALL PROBABILITY: 0.02% | VY = 0.04 m/s", cx - 145, cy - 112);
  }

  _renderFireMode(w, h) {
    const ctx = this.ctx;
    const fx = w * 0.5;
    const fy = h * 0.55;

    // Thermal radial gradient
    const grad = ctx.createRadialGradient(fx, fy, 10, fx, fy, 120);
    grad.addColorStop(0, "rgba(255, 51, 102, 0.7)");
    grad.addColorStop(0.4, "rgba(255, 183, 3, 0.4)");
    grad.addColorStop(1, "rgba(255, 51, 102, 0)");

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(fx, fy, 120, 0, Math.PI * 2);
    ctx.fill();

    // Fire Detection Bounding Box
    ctx.strokeStyle = "#ff3366";
    ctx.lineWidth = 2.5;
    ctx.strokeRect(fx - 70, fy - 80, 140, 150);
    this._drawCorners(fx - 70, fy - 80, 140, 150, "#ff3366");

    ctx.fillStyle = "#ff3366";
    ctx.fillRect(fx - 70, fy - 105, 140, 24);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 11px 'IBM Plex Mono', monospace";
    ctx.fillText("FLAME LOC: 99.1%", fx - 62, fy - 89);

    ctx.fillStyle = "#ffb703";
    ctx.fillText("PEAK TEMP: 412°C", fx - 60, fy - 50);
    ctx.fillText("SMOKE INDEX: HIGH", fx - 60, fy - 32);
  }

  _drawCorners(x, y, w, h, color) {
    const ctx = this.ctx;
    const len = 12;
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;

    // Top-Left
    ctx.beginPath();
    ctx.moveTo(x, y + len);
    ctx.lineTo(x, y);
    ctx.lineTo(x + len, y);
    ctx.stroke();

    // Top-Right
    ctx.beginPath();
    ctx.moveTo(x + w - len, y);
    ctx.lineTo(x + w, y);
    ctx.lineTo(x + w, y + len);
    ctx.stroke();

    // Bottom-Left
    ctx.beginPath();
    ctx.moveTo(x, y + h - len);
    ctx.lineTo(x, y + h);
    ctx.lineTo(x + len, y + h);
    ctx.stroke();

    // Bottom-Right
    ctx.beginPath();
    ctx.moveTo(x + w - len, y + h);
    ctx.lineTo(x + w, y + h);
    ctx.lineTo(x + w, y + h - len);
    ctx.stroke();
  }

  _renderHUDOverlay(w, h) {
    const ctx = this.ctx;
    ctx.fillStyle = "rgba(0, 240, 255, 0.75)";
    ctx.font = "11px 'IBM Plex Mono', monospace";
    ctx.fillText(`CAM-01 • RESOLUTION: 1920x1080 • LATENCY: 38ms • INFERENCE: TENSOR-RT`, 16, h - 16);
  }
}
