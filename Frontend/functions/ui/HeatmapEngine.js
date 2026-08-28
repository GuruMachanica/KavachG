// HeatmapEngine.js - Spatial Hazard & Worker Dwell Density Heatmap Engine
export class HeatmapEngine {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext("2d") : null;
    this.points = [];
  }

  addPoint(normX, normY, intensity = 0.8) {
    this.points.push({ x: normX, y: normY, intensity, time: Date.now() });
    if (this.points.length > 500) {
      this.points.shift();
    }
  }

  render() {
    if (!this.ctx || !this.canvas) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);

    this.points.forEach((p) => {
      const px = p.x * w;
      const py = p.y * h;
      const radius = 35;

      const grad = this.ctx.createRadialGradient(px, py, 0, px, py, radius);
      grad.addColorStop(0, `rgba(255, 51, 102, ${p.intensity * 0.45})`);
      grad.addColorStop(0.5, `rgba(255, 183, 3, ${p.intensity * 0.25})`);
      grad.addColorStop(1, "rgba(0, 240, 255, 0)");

      this.ctx.fillStyle = grad;
      this.ctx.beginPath();
      this.ctx.arc(px, py, radius, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }

  clear() {
    this.points = [];
    if (this.ctx && this.canvas) {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
  }
}
