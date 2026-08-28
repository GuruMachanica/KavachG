// ApiClient.js - High Performance HTTP Client with In-Flight Deduplication, TTL Cache & Abort Control
import { stateManager } from "./StateManager.js";

export class ApiClient {
  constructor(baseUrl = null) {
    if (baseUrl) {
      this.baseUrl = baseUrl;
    } else {
      const isLocal = typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:");
      const storedUrl = typeof window !== "undefined" ? (localStorage.getItem("kavachg_api_url") || localStorage.getItem("apiUrl")) : null;
      const windowUrl = typeof window !== "undefined" ? window.API_BASE_URL : null;
      
      this.baseUrl = storedUrl || windowUrl || (isLocal ? "http://127.0.0.1:8000" : "https://kavachg.onrender.com");

    }
    this.cache = new Map(); // key -> { data, expiry }
    this.inFlight = new Map(); // key -> Promise
    this.activeControllers = new Map(); // key -> AbortController
  }


  async _request(endpoint, options = {}, cacheTtlMs = 0) {
    const method = options.method || "GET";
    const cacheKey = `${method}:${endpoint}`;

    // 1. Check TTL cache for GET requests
    if (method === "GET" && cacheTtlMs > 0) {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() < cached.expiry) {
        return cached.data;
      }
    }

    // 2. Request deduplication (merge simultaneous in-flight GET requests)
    if (method === "GET" && this.inFlight.has(cacheKey)) {
      return this.inFlight.get(cacheKey);
    }

    // 3. Abort previous in-flight request if a fresh one is triggered
    if (this.activeControllers.has(cacheKey)) {
      this.activeControllers.get(cacheKey).abort();
    }
    const controller = new AbortController();
    this.activeControllers.set(cacheKey, controller);

    const token = stateManager.get("token");
    const headers = {
      ...(options.headers || {}),
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const fetchPromise = (async () => {
      try {
        const res = await fetch(`${this.baseUrl}${endpoint}`, {
          ...options,
          headers,
          signal: controller.signal,
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || `HTTP Error ${res.status}`);
        }

        const data = await res.json();

        if (method === "GET" && cacheTtlMs > 0) {
          this.cache.set(cacheKey, { data, expiry: Date.now() + cacheTtlMs });
        }

        return data;
      } finally {
        this.inFlight.delete(cacheKey);
        this.activeControllers.delete(cacheKey);
      }
    })();

    if (method === "GET") {
      this.inFlight.set(cacheKey, fetchPromise);
    }

    return fetchPromise;
  }

  invalidateCache(pattern = null) {
    if (!pattern) {
      this.cache.clear();
    } else {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) this.cache.delete(key);
      }
    }
  }

  async login(email, password) {
    const body = new URLSearchParams({ username: email, password });
    const res = await this._request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    this.invalidateCache();
    return res;
  }

  async getIncidents() {
    return this._request("/incidents/", {}, 1500); // 1.5s cache
  }

  async resolveIncident(id) {
    return this.updateIncidentStatus(id, "Resolved");
  }

  async updateIncidentStatus(id, status) {
    const res = await this._request(`/incidents/${id}/status?status=${encodeURIComponent(status)}`, {
      method: "PATCH",
    });
    this.invalidateCache("/incidents");
    return res;
  }

  async getSensitivity() {
    return this._request("/settings/sensitivity", {}, 3000); // 3s cache
  }

  async updateSensitivity(threshold) {
    const res = await this._request(`/settings/sensitivity?confidence_threshold=${threshold}`, {
      method: "POST",
    });
    this.invalidateCache("/settings");
    return res;
  }

  async getPeople() {
    return this._request("/people/", {}, 3000); // 3s cache
  }

  async addPerson(name, extra = "", admin = false) {
    const res = await this._request("/people/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, extra, admin: admin ? 1 : 0 }),
    });
    this.invalidateCache("/people");
    return res;
  }

  async getBriefing() {
    return this._request("/copilot/briefing", {}, 5000);
  }

  async askCopilot(query) {
    return this._request("/copilot/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
  }

  async getSwarmStatus() {
    return this._request("/swarm/status", {}, 3000);
  }

  async toggleSwarmPatrol(active = null) {
    const res = await this._request("/swarm/patrol/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ active }),
    });
    this.invalidateCache("/swarm");
    return res;
  }

  async getCameras() {
    return this._request("/cameras", {}, 5000);
  }

  async setCamera(cameraId) {
    const res = await this._request(`/cameras/${cameraId}`, {
      method: "POST",
    });
    this.invalidateCache("/cameras");
    return res;
  }

  async createUser(payload) {
    const res = await this._request("/auth/admin/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return res;
  }

  getClipUrl(clipPath, token = null) {
    const tok = token || stateManager.get("token");
    const filename = clipPath.split(/[\\/]/).pop();
    return `${this.baseUrl}/clips/${filename}${tok ? `?token=${encodeURIComponent(tok)}` : ""}`;
  }

  getImageUrl(imagePath, token = null) {
    const tok = token || stateManager.get("token");
    const filename = imagePath.split(/[\\/]/).pop();
    return `${this.baseUrl}/incident_images/${filename}${tok ? `?token=${encodeURIComponent(tok)}` : ""}`;
  }

  getStreamUrl(mode = "video_feed", token = null) {
    const activeToken = token || stateManager.get("token");
    const tokParam = activeToken ? `token=${encodeURIComponent(activeToken)}` : "";
    const cleanMode = mode.startsWith("/") ? mode.slice(1) : mode;
    return tokParam ? `${this.baseUrl}/${cleanMode}?${tokParam}` : `${this.baseUrl}/${cleanMode}`;
  }
}

export const apiClient = new ApiClient();

