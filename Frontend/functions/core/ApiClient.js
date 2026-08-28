// ApiClient.js - High-Performance AJAX Client with In-Flight Deduplication, LRU Cache & Abort Control
import { stateManager } from "./StateManager.js";

export class ApiClient {
  constructor(baseUrl = `http://${window.location.hostname}:8000`) {
    this.baseUrl = baseUrl;
    this.cache = new Map();
    this.inFlight = new Map();
    this.activeControllers = new Map();
  }

  _headers(extra = {}) {
    const token = stateManager.get("token");
    return token ? { Authorization: `Bearer ${token}`, ...extra } : extra;
  }

  /**
   * High-concurrency optimized request handler with caching and deduplication
   */
  async _request(path, options = {}, cacheTtlMs = 0) {
    const url = `${this.baseUrl}${path}`;
    const method = (options.method || "GET").toUpperCase();
    const cacheKey = `${method}:${url}`;

    // 1. Check TTL Cache for GET requests
    if (method === "GET" && cacheTtlMs > 0) {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < cacheTtlMs) {
        return cached.data;
      }
    }

    // 2. In-Flight Promise Sharing (Prevents duplicate requests for the same endpoint)
    if (method === "GET" && this.inFlight.has(cacheKey)) {
      return this.inFlight.get(cacheKey);
    }

    // 3. Abort Control Management
    if (options.cancelPrevious) {
      if (this.activeControllers.has(cacheKey)) {
        this.activeControllers.get(cacheKey).abort();
      }
      const controller = new AbortController();
      this.activeControllers.set(cacheKey, controller);
      options.signal = controller.signal;
    }

    const config = {
      ...options,
      headers: this._headers(options.headers || {}),
    };

    const fetchPromise = (async () => {
      try {
        const res = await fetch(url, config);
        const text = await res.text();
        let data = {};
        try {
          data = text ? JSON.parse(text) : {};
        } catch (_err) {
          data = { detail: text || "Server response error" };
        }

        if (!res.ok) {
          if (res.status === 401) {
            stateManager.clearAuth();
          }
          const err = new Error(data.detail || data.error || `Request failed (${res.status})`);
          err.status = res.status;
          throw err;
        }

        // Cache successful response
        if (method === "GET" && cacheTtlMs > 0) {
          this.cache.set(cacheKey, { timestamp: Date.now(), data });
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
    return this._request("/incidents/", {}, 2000); // 2s cache
  }

  async updateIncidentStatus(id, status) {
    const res = await this._request(`/incidents/${id}/status?status=${encodeURIComponent(status)}`, {
      method: "PATCH",
    });
    this.invalidateCache("/incidents");
    return res;
  }

  async getSensitivity() {
    return this._request("/settings/sensitivity", {}, 5000); // 5s cache
  }

  async updateSensitivity(threshold) {
    const res = await this._request(`/settings/sensitivity?confidence_threshold=${threshold}`, {
      method: "POST",
    });
    this.invalidateCache("/settings");
    return res;
  }

  async getPeople() {
    return this._request("/people/", {}, 5000); // 5s cache
  }

  async registerUser(userData) {
    return this._request("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });
  }

  async getCameras() {
    return this._request("/cameras/", {}, 10000); // 10s cache
  }

  async setCamera(cameraId) {
    return this._request(`/cameras/select/${cameraId}`, {
      method: "POST",
    });
  }

  async queryCopilot(query) {
    return this._request(`/copilot/query?query=${encodeURIComponent(query)}`, {
      method: "POST",
      cancelPrevious: true,
    });
  }

  async getCopilotBriefing() {
    return this._request("/copilot/briefing", {}, 3000);
  }

  getStreamUrl(mode = "video_feed", token = null) {
    const activeToken = token || stateManager.get("token");
    const tokParam = activeToken ? `?token=${encodeURIComponent(activeToken)}` : "";
    return `${this.baseUrl}/${mode}${tokParam}`;
  }

  getClipUrl(clipPath, token = null) {
    const activeToken = token || stateManager.get("token");
    const tokParam = activeToken ? `?token=${encodeURIComponent(activeToken)}` : "";
    const filename = clipPath.split(/[/\\]/).pop();
    return `${this.baseUrl}/clips/${filename}${tokParam}`;
  }

  getImageUrl(imagePath, token = null) {
    const activeToken = token || stateManager.get("token");
    const tokParam = activeToken ? `?token=${encodeURIComponent(activeToken)}` : "";
    const filename = imagePath.split(/[/\\]/).pop();
    return `${this.baseUrl}/incident_images/${filename}${tokParam}`;
  }
}

export const apiClient = new ApiClient();
