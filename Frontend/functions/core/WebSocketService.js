// WebSocketService.js - Self-Healing Realtime Stream
import { stateManager } from "./StateManager.js";
import { eventBus } from "./EventBus.js";
import { audioAlertEngine } from "./AudioAlertEngine.js";
import { apiClient } from "./ApiClient.js";

export class WebSocketService {
  constructor() {
    this.ws = null;
    this.retryTimer = null;
    this.retryDelay = 2000;
  }

  connect() {
    const token = stateManager.get("token");
    if (!token) return;

    if (this.ws) {
      this.ws.close();
    }

    const baseApi = apiClient.baseUrl; // e.g. "https://kavachg.onrender.com" or "http://127.0.0.1:8000"
    const wsUrl = baseApi.replace(/^http/, "ws") + "/ws/incidents";
    
    try {
      this.ws = new WebSocket(wsUrl);

      
      this.ws.onopen = () => {
        this.retryDelay = 2000;
        eventBus.emit("ws:connected");
      };

      this.ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === "incident") {
            audioAlertEngine.playAlert("danger");
            eventBus.emit("incident:alert", msg.data);
          }
        } catch (_e) {}
        eventBus.emit("ws:update");
      };

      this.ws.onclose = () => {
        eventBus.emit("ws:disconnected");
        clearTimeout(this.retryTimer);
        this.retryTimer = setTimeout(() => {
          this.retryDelay = Math.min(this.retryDelay * 1.5, 10000);
          this.connect();
        }, this.retryDelay);
      };
    } catch (_err) {
      // Connect error
    }
  }

  disconnect() {
    clearTimeout(this.retryTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsService = new WebSocketService();
