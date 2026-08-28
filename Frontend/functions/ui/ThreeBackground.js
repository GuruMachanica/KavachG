// ThreeBackground.js - 3D Industrial Surveillance Particle Radar & Cyber Grid (High Performance Optimized)
export class ThreeBackground {
  constructor() {
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.particles = null;
    this.grid = null;
    this.animationFrameId = null;
    this.mouse = { x: 0, y: 0 };
    this.targetMouse = { x: 0, y: 0 };
    this.dangerState = false;
    this.isPaused = false;
  }

  init() {
    if (typeof THREE === "undefined") {
      return;
    }

    if (document.getElementById("three-bg-container")) {
      return;
    }

    const container = document.createElement("div");
    container.id = "three-bg-container";
    container.style.position = "fixed";
    container.style.top = "0";
    container.style.left = "0";
    container.style.width = "100vw";
    container.style.height = "100vh";
    container.style.zIndex = "0";
    container.style.pointerEvents = "none";
    container.style.opacity = "0.85";
    document.body.prepend(container);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
    this.camera.position.z = 450;

    this.renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: false, // Performance boost on high-DPI displays
      powerPreference: "high-performance",
      precision: "mediump"
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    container.appendChild(this.renderer.domElement);

    this._createParticleConstellation();
    this._createCyberPlane();

    // Event Listeners with Performance Throttling
    window.addEventListener("resize", () => this._onResize(), { passive: true });
    window.addEventListener("mousemove", (e) => this._onMouseMove(e), { passive: true });

    // Tab visibility pause to drop GPU usage to 0% when backgrounded
    document.addEventListener("visibilitychange", () => {
      this.isPaused = document.hidden;
      if (!this.isPaused) {
        this._animate();
      }
    });

    this._animate();
  }

  _createParticleConstellation() {
    const particleCount = 650;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const cyan = new THREE.Color(0x00f0ff);
    const emerald = new THREE.Color(0x00e5a3);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 1100;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 800;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 600;

      const mixed = Math.random() > 0.4 ? cyan : emerald;
      colors[i * 3] = mixed.r;
      colors[i * 3 + 1] = mixed.g;
      colors[i * 3 + 2] = mixed.b;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 3.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  _createCyberPlane() {
    const size = 1200;
    const divisions = 24;
    this.grid = new THREE.GridHelper(size, divisions, 0x00f0ff, 0x071e33);
    this.grid.position.y = -220;
    this.grid.material.opacity = 0.22;
    this.grid.material.transparent = true;
    this.scene.add(this.grid);
  }

  setDangerState(isDanger) {
    if (!this.particles || this.dangerState === isDanger) return;
    this.dangerState = isDanger;
    const targetColor = isDanger ? new THREE.Color(0xff3366) : new THREE.Color(0x00f0ff);
    const colors = this.particles.geometry.attributes.color.array;
    for (let i = 0; i < colors.length / 3; i++) {
      colors[i * 3] = targetColor.r;
      colors[i * 3 + 1] = targetColor.g;
      colors[i * 3 + 2] = targetColor.b;
    }
    this.particles.geometry.attributes.color.needsUpdate = true;
  }

  _onMouseMove(event) {
    this.targetMouse.x = (event.clientX / window.innerWidth - 0.5) * 2;
    this.targetMouse.y = (event.clientY / window.innerHeight - 0.5) * 2;
  }

  _onResize() {
    if (!this.camera || !this.renderer) return;
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  _animate() {
    if (this.isPaused) return;

    this.animationFrameId = requestAnimationFrame(() => this._animate());

    // Smooth mouse interpolation
    this.mouse.x += (this.targetMouse.x - this.mouse.x) * 0.04;
    this.mouse.y += (this.targetMouse.y - this.mouse.y) * 0.04;

    if (this.particles) {
      this.particles.rotation.y += 0.0006;
      this.particles.rotation.x += 0.0002;
    }

    if (this.grid) {
      this.grid.rotation.y -= 0.0003;
    }

    if (this.camera) {
      this.camera.position.x += (this.mouse.x * 50 - this.camera.position.x) * 0.04;
      this.camera.position.y += (-this.mouse.y * 35 - this.camera.position.y) * 0.04;
      this.camera.lookAt(this.scene.position);
    }

    this.renderer.render(this.scene, this.camera);
  }
}

export const threeBackground = new ThreeBackground();
