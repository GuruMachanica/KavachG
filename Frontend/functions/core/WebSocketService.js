// WebSocketService.js - Self-Healing Realtime Stream
import { stateManager } from "./StateManager.js";
import { eventBus } from "./EventBus.js";
import { audioAlertEngine } from "./AudioAlertEngine.js";

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

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${protocol}://${window.location.hostname}:8000/ws/incidents`;
    
    try {
      this.ws = new WebSocket(url);
      
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
