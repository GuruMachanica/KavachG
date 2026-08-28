// ThreeBackground.js - 3D Industrial Surveillance Particle Radar Digital Twin
export class ThreeBackground {
  constructor() {
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.particles = null;
    this.animationFrameId = null;
    this.mouse = { x: 0, y: 0 };
    this.dangerState = false;
  }

  init() {
    if (typeof THREE === "undefined") {
      console.warn("[ThreeBackground] Three.js not loaded, skipping 3D canvas.");
      return;
    }

    const container = document.createElement("div");
    container.id = "three-bg-container";
    container.style.position = "fixed";
    container.style.top = "0";
    container.style.left = "0";
    container.style.width = "100vw";
    container.style.height = "100vh";
    container.style.zIndex = "-2";
    container.style.pointerEvents = "none";
    container.style.opacity = "0.45";
    document.body.prepend(container);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
    this.camera.position.z = 400;

    this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(this.renderer.domElement);

    this._createParticleGrid();

    window.addEventListener("resize", () => this._onResize());
    window.addEventListener("mousemove", (e) => this._onMouseMove(e));

    this._animate();
  }

  _createParticleGrid() {
    const particleCount = 600;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const baseColor = new THREE.Color(0x00f0ff);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 800;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 600;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 500;

      colors[i * 3] = baseColor.r;
      colors[i * 3 + 1] = baseColor.g;
      colors[i * 3 + 2] = baseColor.b;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 3.5,
      vertexColors: true,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending,
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  setThreatLevel(isDanger) {
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
    this.mouse.x = (event.clientX / window.innerWidth - 0.5) * 2;
    this.mouse.y = (event.clientY / window.innerHeight - 0.5) * 2;
  }

  _onResize() {
    if (!this.camera || !this.renderer) return;
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  _animate() {
    this.animationFrameId = requestAnimationFrame(() => this._animate());
    if (this.particles) {
      this.particles.rotation.y += 0.001;
      this.particles.rotation.x += 0.0005;
      
      // Mouse Parallax
      this.camera.position.x += (this.mouse.x * 50 - this.camera.position.x) * 0.05;
      this.camera.position.y += (-this.mouse.y * 50 - this.camera.position.y) * 0.05;
      this.camera.lookAt(this.scene.position);
    }
    this.renderer.render(this.scene, this.camera);
  }
}

export const threeBackground = new ThreeBackground();
