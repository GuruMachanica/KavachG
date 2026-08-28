// PlantDigitalTwin.js - Sector Alpha 3D Holographic Radar & IoT Digital Twin (Three.js)
import { stateManager } from "../core/StateManager.js";
import { eventBus } from "../core/EventBus.js";

export class PlantDigitalTwin {
  constructor(containerElement) {
    this.container = containerElement;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.nodes = [];
    this.radarBeam = null;
    this.radarRings = [];
    this.animId = null;
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this._init();
  }

  _init() {
    if (!this.container || typeof THREE === "undefined") return;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, this.container.clientWidth / this.container.clientHeight, 1, 1000);
    this.camera.position.set(0, 160, 220);
    this.camera.lookAt(0, 0, 0);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.innerHTML = "";
    this.container.appendChild(this.renderer.domElement);

    // 1. Concentric Holographic Radar Rings
    const ringRadii = [30, 65, 100, 135];
    ringRadii.forEach((radius, idx) => {
      const ringGeo = new THREE.RingGeometry(radius - 0.5, radius + 0.5, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: idx === 3 ? 0x00f0ff : 0x1e3a5f,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: idx === 3 ? 0.4 : 0.25,
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2;
      this.scene.add(ringMesh);
      this.radarRings.push(ringMesh);
    });

    // 2. Radar Crosshair Axis Lines
    const axisMat = new THREE.LineBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.2 });
    const axisGeoX = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-140, 0, 0), new THREE.Vector3(140, 0, 0)]);
    const axisGeoZ = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, -140), new THREE.Vector3(0, 0, 140)]);
    this.scene.add(new THREE.Line(axisGeoX, axisMat));
    this.scene.add(new THREE.Line(axisGeoZ, axisMat));

    // 3. Rotating Holographic Sweep Cone
    const sweepGeo = new THREE.CircleGeometry(135, 32, 0, Math.PI / 3);
    const sweepMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.15,
    });
    this.radarBeam = new THREE.Mesh(sweepGeo, sweepMat);
    this.radarBeam.rotation.x = Math.PI / 2;
    this.scene.add(this.radarBeam);

    // 4. Active Spatial Camera & IoT Sensor Nodes
    this._createRadarNode(0, 45, 0, -35, "Camera 0: Assembly Node", 0x00f0ff, false);
    this._createRadarNode(1, 85, 0, 25, "Sensor 1: Compressor Unit B (Warning)", 0xffb703, true);
    this._createRadarNode(2, -50, 0, 65, "Camera 2: Warehouse Node", 0x00f0ff, false);
    this._createRadarNode(3, -75, 0, -50, "Camera 3: Logistics Bay", 0x00e5a3, false);
    this._createRadarNode(4, 15, 0, 85, "Camera 4: Substation Perimeter", 0x00f0ff, false);

    // Click Detection
    this.container.addEventListener("click", (e) => this._onCanvasClick(e));
    window.addEventListener("resize", () => this._onResize());

    this._animate();
  }

  _createRadarNode(id, x, y, z, label, colorHex, isWarning) {
    const group = new THREE.Group();
    group.position.set(x, y, z);
    group.userData = { id, label, isWarning };

    // Glowing Sphere Pin
    const sphereGeo = new THREE.SphereGeometry(isWarning ? 4.5 : 3.5, 16, 16);
    const sphereMat = new THREE.MeshBasicMaterial({ color: colorHex });
    const sphere = new THREE.Mesh(sphereGeo, sphereMat);
    group.add(sphere);

    // Outer Pulse Wave
    const ringGeo = new THREE.RingGeometry(5, 7, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: colorHex,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2;
    group.add(ring);
    group.userData.ring = ring;

    this.scene.add(group);
    this.nodes.push(group);
  }

  _onCanvasClick(event) {
    const rect = this.container.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / this.container.clientWidth) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / this.container.clientHeight) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.nodes, true);

    if (intersects.length > 0) {
      const topGroup = intersects[0].object.parent;
      if (topGroup && topGroup.userData) {
        stateManager.set("selectedCameraId", topGroup.userData.id);
        eventBus.emit("toast", { message: `Focused on ${topGroup.userData.label}` });
        eventBus.emit("nav:tab", "detection");
      }
    }
  }

  _onResize() {
    if (!this.container || !this.camera || !this.renderer) return;
    this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
  }

  _animate() {
    this.animId = requestAnimationFrame(() => this._animate());

    // Rotate Radar Sweep Beam
    if (this.radarBeam) {
      this.radarBeam.rotation.z -= 0.025;
    }

    // Node Pulsing
    const time = performance.now() * 0.003;
    this.nodes.forEach((node) => {
      const ring = node.userData.ring;
      if (ring) {
        const scale = 1 + (Math.sin(time * 3) + 1) * 0.4;
        ring.scale.set(scale, scale, scale);
      }
    });

    this.renderer.render(this.scene, this.camera);
  }

  destroy() {
    if (this.animId) cancelAnimationFrame(this.animId);
    if (this.renderer && this.renderer.domElement) {
      this.renderer.domElement.remove();
    }
  }
}
