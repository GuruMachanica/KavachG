// ApiClient.js - Object-Oriented Backend Client with Circuit Breaker
import { stateManager } from "./StateManager.js";

export class ApiClient {
  constructor(baseUrl = `http://${window.location.hostname}:8000`) {
    this.baseUrl = baseUrl;
  }

  _headers(extra = {}) {
    const token = stateManager.get("token");
    return token ? { Authorization: `Bearer ${token}`, ...extra } : extra;
  }

  async _request(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const config = {
      ...options,
      headers: this._headers(options.headers || {}),
    };

    const res = await fetch(url, config);
    const text = await res.text();
    let data = {};
    try {
      data = text ? JSON.parse(text) : {};
    } catch (_err) {
      data = { detail: text || "Server error" };
    }

    if (!res.ok) {
      if (res.status === 401) {
        stateManager.clearAuth();
      }
      const err = new Error(data.detail || data.error || `Request failed (${res.status})`);
      err.status = res.status;
      throw err;
    }
    return data;
  }

  async login(email, password) {
    const body = new URLSearchParams({ username: email, password });
    return this._request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
  }

  async getIncidents() {
    return this._request("/incidents/");
  }

  async updateIncidentStatus(id, status) {
    return this._request(`/incidents/${id}/status?status=${encodeURIComponent(status)}`, {
      method: "PATCH",
    });
  }

  async getSensitivity() {
    return this._request("/settings/sensitivity");
  }

  async setSensitivity(value) {
    return this._request("/settings/sensitivity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value }),
    });
  }

  async getCameras() {
    return this._request("/cameras");
  }

  async setMonitoringCamera(cameraId) {
    return this._request(`/monitoring/camera/${cameraId}`, { method: "POST" });
  }

  async getCopilotBriefing() {
    return this._request("/copilot/briefing");
  }

  async askCopilot(query) {
    return this._request("/copilot/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
  }

  async getZones() {
    return this._request("/zones");
  }

  async saveZone(zoneData) {
    return this._request("/zones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(zoneData),
    });
  }

  async createUser(payload) {
    return this._request("/auth/admin/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  getStreamUrl(mode, token) {
    return `${this.baseUrl}/${mode}?token=${encodeURIComponent(token)}&t=${Date.now()}`;
  }

  getClipUrl(clipPath, token) {
    return `${this.baseUrl}/clips/${encodeURIComponent(clipPath)}?token=${encodeURIComponent(token)}`;
  }

  getImageUrl(imagePath, token) {
    return `${this.baseUrl}/incident-images/${encodeURIComponent(imagePath)}?token=${encodeURIComponent(token)}`;
  }
}

export const apiClient = new ApiClient();
