// PlantDigitalTwin.js - Realistic 3D Factory Floor, Volumetric Vision Cones & IoT Digital Twin (Three.js)
import { stateManager } from "../core/StateManager.js";
import { eventBus } from "../core/EventBus.js";

export class PlantDigitalTwin {
  constructor(containerElement) {
    this.container = containerElement;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.animId = null;
    
    // Interactive objects
    this.nodes = [];
    this.cameraFrustums = [];
    this.workers = [];
    this.hazardBeacons = [];
    this.conveyors = [];
    
    // Controls & Interaction
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this.isDragging = false;
    this.prevMousePos = { x: 0, y: 0 };
    this.cameraTarget = new THREE.Vector3(0, 0, 0);
    this.orbitRadius = 260;
    this.orbitTheta = Math.PI / 4;
    this.orbitPhi = Math.PI / 3.2;

    this._init();
  }

  _init() {
    if (!this.container || typeof THREE === "undefined") return;

    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x030712, 0.0018);

    const aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(42, aspect, 1, 2000);
    this._updateCameraPosition();

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.container.innerHTML = "";
    this.container.appendChild(this.renderer.domElement);

    // 1. Ambient & Spatial Volumetric Lighting
    const ambientLight = new THREE.AmbientLight(0x0f2744, 1.2);
    this.scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0x00f0ff, 1.4);
    mainLight.position.set(120, 200, 100);
    this.scene.add(mainLight);

    const floorLight = new THREE.PointLight(0x00e5a3, 1.5, 300);
    floorLight.position.set(-60, 40, -40);
    this.scene.add(floorLight);

    // 2. Build 3D Realistic Industrial Architecture
    this._buildFloorAndGrid();
    this._buildSectorAssemblyLine();
    this._buildSectorSubstation();
    this._buildSectorWarehouse();
    this._buildSectorLogistics();
    this._buildCameraVisionCones();
    this._buildWorkerAvatars();

    // 3. Setup Orbit & Pointer Controls
    this._setupControls();
    window.addEventListener("resize", () => this._onResize());

    this._animate();
  }

  _updateCameraPosition() {
    this.camera.position.x = this.orbitRadius * Math.sin(this.orbitPhi) * Math.sin(this.orbitTheta);
    this.camera.position.y = this.orbitRadius * Math.cos(this.orbitPhi);
    this.camera.position.z = this.orbitRadius * Math.sin(this.orbitPhi) * Math.cos(this.orbitTheta);
    this.camera.lookAt(this.cameraTarget);
  }

  _buildFloorAndGrid() {
    // Holographic Base Plane
    const floorGeo = new THREE.PlaneGeometry(360, 280);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x07111e,
      roughness: 0.8,
      metalness: 0.2,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.5;
    this.scene.add(floor);

    // Precision Cyber Wireframe Grid
    const grid = new THREE.GridHelper(360, 36, 0x00f0ff, 0x122b44);
    grid.position.y = 0;
    this.scene.add(grid);

    // Perimeter Defensive Walls (Glassmorphic)
    const wallMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.15,
    });
    const wallGeo = new THREE.BoxGeometry(360, 25, 280);
    const walls = new THREE.Mesh(wallGeo, wallMat);
    walls.position.y = 12.5;
    this.scene.add(walls);
  }

  _buildSectorAssemblyLine() {
    const group = new THREE.Group();
    group.position.set(-80, 0, -60);

    // Assembly Conveyor Belt
    const convGeo = new THREE.BoxGeometry(110, 6, 18);
    const convMat = new THREE.MeshStandardMaterial({ color: 0x1b2d42, roughness: 0.5 });
    const conv = new THREE.Mesh(convGeo, convMat);
    conv.position.y = 3;
    group.add(conv);

    // Robotic Gantry Frame
    const gantryMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, wireframe: true });
    for (let x = -40; x <= 40; x += 40) {
      const gantry = new THREE.Mesh(new THREE.BoxGeometry(6, 32, 24), gantryMat);
      gantry.position.set(x, 16, 0);
      group.add(gantry);
    }

    // Moving Workpieces on Conveyor
    for (let i = 0; i < 4; i++) {
      const piece = new THREE.Mesh(
        new THREE.BoxGeometry(8, 6, 8),
        new THREE.MeshStandardMaterial({ color: 0x00e5a3, emissive: 0x00e5a3, emissiveIntensity: 0.4 })
      );
      piece.position.set(-45 + i * 30, 8, 0);
      group.add(piece);
      this.conveyors.push(piece);
    }

    this._addSectorLabel(group, "SECTOR A • ROBOTIC ASSEMBLY", 0x00f0ff);
    this.scene.add(group);
  }

  _buildSectorSubstation() {
    const group = new THREE.Group();
    group.position.set(80, 0, -60);

    // High Voltage Transformers
    const transfMat = new THREE.MeshStandardMaterial({ color: 0x22364f, metalness: 0.7 });
    for (let x = -25; x <= 25; x += 25) {
      const transf = new THREE.Mesh(new THREE.CylinderGeometry(8, 8, 24, 16), transfMat);
      transf.position.set(x, 12, 0);
      group.add(transf);

      // Glowing Core Coil
      const coil = new THREE.Mesh(
        new THREE.TorusGeometry(9, 1.2, 8, 24),
        new THREE.MeshBasicMaterial({ color: 0xffb703, wireframe: true })
      );
      coil.rotation.x = Math.PI / 2;
      coil.position.set(x, 12, 0);
      group.add(coil);
    }

    // Safety Perimeter Cage
    const cage = new THREE.Mesh(
      new THREE.BoxGeometry(80, 20, 40),
      new THREE.MeshBasicMaterial({ color: 0xffb703, wireframe: true, transparent: true, opacity: 0.3 })
    );
    cage.position.y = 10;
    group.add(cage);

    this._addSectorLabel(group, "SECTOR B • SUBSTATION (CAUTION)", 0xffb703);
    this.scene.add(group);
  }

  _buildSectorWarehouse() {
    const group = new THREE.Group();
    group.position.set(-80, 0, 60);

    // Multi-tier High-Bay Racks
    const rackMat = new THREE.MeshBasicMaterial({ color: 0x00e5a3, wireframe: true });
    for (let z = -20; z <= 20; z += 20) {
      const rack = new THREE.Mesh(new THREE.BoxGeometry(100, 36, 12), rackMat);
      rack.position.set(0, 18, z);
      group.add(rack);
    }

    this._addSectorLabel(group, "SECTOR C • HIGH-BAY WAREHOUSE", 0x00e5a3);
    this.scene.add(group);
  }

  _buildSectorLogistics() {
    const group = new THREE.Group();
    group.position.set(80, 0, 60);

    // Chemical / Fuel Storage Tanks
    const tankMat = new THREE.MeshStandardMaterial({ color: 0x162c46, roughness: 0.3 });
    [-20, 20].forEach((x) => {
      const tank = new THREE.Mesh(new THREE.CylinderGeometry(14, 14, 28, 24), tankMat);
      tank.position.set(x, 14, 0);
      group.add(tank);
    });

    this._addSectorLabel(group, "SECTOR D • LOGISTICS & STORAGE", 0x00f0ff);
    this.scene.add(group);
  }

  _buildCameraVisionCones() {
    const cams = [
      { id: 0, pos: [-80, 36, -60], target: [-80, 0, -60], name: "Camera 0 (Assembly)", color: 0x00f0ff },
      { id: 1, pos: [80, 36, -60], target: [80, 0, -60], name: "Camera 1 (Substation)", color: 0xffb703 },
      { id: 2, pos: [-80, 36, 60], target: [-80, 0, 60], name: "Camera 2 (Warehouse)", color: 0x00e5a3 },
      { id: 3, pos: [80, 36, 60], target: [80, 0, 60], name: "Camera 3 (Logistics)", color: 0x00f0ff },
    ];

    cams.forEach((c) => {
      // 1. Camera Mount Rig
      const mount = new THREE.Mesh(
        new THREE.SphereGeometry(3.5, 12, 12),
        new THREE.MeshBasicMaterial({ color: c.color })
      );
      mount.position.set(...c.pos);
      mount.userData = { id: c.id, label: c.name };
      this.scene.add(mount);
      this.nodes.push(mount);

      // 2. Volumetric Pyramidal Vision Frustum Cone
      const coneGeo = new THREE.ConeGeometry(38, 48, 4, 1, true);
      const coneMat = new THREE.MeshBasicMaterial({
        color: c.color,
        wireframe: true,
        transparent: true,
        opacity: 0.35,
      });
      const cone = new THREE.Mesh(coneGeo, coneMat);
      cone.position.set(c.pos[0], 18, c.pos[2]);
      cone.rotation.x = Math.PI;
      this.scene.add(cone);
      this.cameraFrustums.push(cone);
    });
  }

  _buildWorkerAvatars() {
    const workerConfigs = [
      { id: "W1", pos: [-60, 0, -45], color: 0x00e5a3, compliant: true },
      { id: "W2", pos: [-95, 0, -70], color: 0x00e5a3, compliant: true },
      { id: "W3", pos: [65, 0, -50], color: 0xff3366, compliant: false }, // Violation in substation!
      { id: "W4", pos: [-75, 0, 50], color: 0x00e5a3, compliant: true },
      { id: "W5", pos: [90, 0, 75], color: 0x00e5a3, compliant: true },
    ];

    workerConfigs.forEach((wc) => {
      const avatar = new THREE.Group();
      avatar.position.set(...wc.pos);

      // Body Capsule
      const body = new THREE.Mesh(
        new THREE.CylinderGeometry(2, 2.5, 9, 12),
        new THREE.MeshStandardMaterial({ color: 0x1e3a5f })
      );
      body.position.y = 4.5;
      avatar.add(body);

      // Head & Hardhat
      const head = new THREE.Mesh(
        new THREE.SphereGeometry(2, 12, 12),
        new THREE.MeshStandardMaterial({ color: wc.compliant ? 0xffb703 : 0xffffff })
      );
      head.position.y = 10.5;
      avatar.add(head);

      // Safety Halo Base Ring
      const halo = new THREE.Mesh(
        new THREE.RingGeometry(3.5, 4.5, 16),
        new THREE.MeshBasicMaterial({ color: wc.color, side: THREE.DoubleSide })
      );
      halo.rotation.x = -Math.PI / 2;
      halo.position.y = 0.2;
      avatar.add(halo);

      avatar.userData = { id: wc.id, compliant: wc.compliant, basePos: [...wc.pos] };
      this.scene.add(avatar);
      this.workers.push(avatar);
    });
  }

  _addSectorLabel(parent, text, colorHex) {
    const canvas = document.createElement("canvas");
    canvas.width = 320;
    canvas.height = 64;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#030712";
    ctx.fillRect(0, 0, 320, 64);
    ctx.strokeStyle = "#" + colorHex.toString(16).padStart(6, "0");
    ctx.lineWidth = 4;
    ctx.strokeRect(4, 4, 312, 56);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 18px 'IBM Plex Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText(text, 160, 38);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: 0.9 });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(38, 7.5, 1);
    sprite.position.set(0, 26, 0);
    parent.add(sprite);
  }

  _setupControls() {
    const el = this.container;

    el.addEventListener("mousedown", (e) => {
      this.isDragging = true;
      this.prevMousePos = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener("mousemove", (e) => {
      if (!this.isDragging) return;
      const dx = e.clientX - this.prevMousePos.x;
      const dy = e.clientY - this.prevMousePos.y;

      this.orbitTheta -= dx * 0.008;
      this.orbitPhi = Math.max(0.2, Math.min(Math.PI / 2.1, this.orbitPhi - dy * 0.008));

      this._updateCameraPosition();
      this.prevMousePos = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener("mouseup", () => {
      this.isDragging = false;
    });

    el.addEventListener("wheel", (e) => {
      e.preventDefault();
      this.orbitRadius = Math.max(120, Math.min(420, this.orbitRadius + e.deltaY * 0.25));
      this._updateCameraPosition();
    });

    el.addEventListener("click", (e) => this._onCanvasClick(e));
  }

  _onCanvasClick(event) {
    const rect = this.container.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / this.container.clientWidth) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / this.container.clientHeight) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.nodes, true);

    if (intersects.length > 0) {
      const topObj = intersects[0].object;
      if (topObj && topObj.userData && topObj.userData.id !== undefined) {
        stateManager.set("selectedCameraId", topObj.userData.id);
        eventBus.emit("toast", { message: `Focused 3D Camera: ${topObj.userData.label}` });
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
    const time = performance.now() * 0.002;

    // 1. Animate Conveyor Workpieces
    this.conveyors.forEach((p, idx) => {
      p.position.x += 0.25;
      if (p.position.x > 45) p.position.x = -45;
    });

    // 2. Pulse Camera Vision Cones
    this.cameraFrustums.forEach((cone) => {
      cone.rotation.y += 0.01;
      cone.material.opacity = 0.25 + Math.sin(time * 2) * 0.12;
    });

    // 3. Subtle Worker Breathing & Walking Patrol
    this.workers.forEach((w, idx) => {
      const base = w.userData.basePos;
      w.position.x = base[0] + Math.sin(time + idx * 1.5) * 4;
      w.position.z = base[2] + Math.cos(time + idx * 1.5) * 4;
    });

    // Auto Slow Rotation when idle
    if (!this.isDragging) {
      this.orbitTheta += 0.001;
      this._updateCameraPosition();
    }

    this.renderer.render(this.scene, this.camera);
  }

  destroy() {
    if (this.animId) cancelAnimationFrame(this.animId);
    if (this.renderer && this.renderer.domElement) {
      this.renderer.domElement.remove();
    }
  }
}
