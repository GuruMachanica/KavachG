// StateManager.js - Reactive State Store
import { eventBus } from "./EventBus.js";

export class StateManager {
  constructor() {
    this._state = {
      token: localStorage.getItem("token") || "",
      user: JSON.parse(localStorage.getItem("user") || "null"),
      incidents: [],
      sensitivity: 50,
      cameras: [],
      liveMode: "video_feed",
      selectedCameraId: 0,
      audioAlarmEnabled: true,
      systemStatus: "safe",
      zones: [],
      isDrawingZone: false,
      zoneDraftPoints: [],
      currentTab: "overview",
    };
  }

  get state() {
    return this._state;
  }

  get(key) {
    return this._state[key];
  }

  set(key, value) {
    const oldValue = this._state[key];
    this._state[key] = value;
    eventBus.emit(`state:${key}`, { value, oldValue });
    eventBus.emit("state:changed", { key, value, oldValue });
  }

  update(partial) {
    Object.entries(partial).forEach(([k, v]) => {
      this.set(k, v);
    });
  }

  setAuth(token, user) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    this.set("token", token);
    this.set("user", user);
    eventBus.emit("auth:login", user);
  }

  clearAuth() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    this.set("token", "");
    this.set("user", null);
    eventBus.emit("auth:logout");
  }

  isAuthenticated() {
    return Boolean(this._state.token && this._state.user);
  }
}

export const stateManager = new StateManager();
