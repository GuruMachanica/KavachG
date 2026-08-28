// StreamManager.js - Resilient Live Stream Controller with Exponential Backoff & Simulated Fallback
import { apiClient } from "../core/ApiClient.js";
import { stateManager } from "../core/StateManager.js";
import { eventBus } from "../core/EventBus.js";

export class StreamManager {
  constructor(imgElement, badgeTextElement) {
    this.img = imgElement;
    this.badgeText = badgeTextElement;
    this.retryTimer = null;
    this.retryCount = 0;
    this.retryDelay = 1000;
    this.maxDelay = 10000;
    this.isSimulated = false;
  }

  connect() {
    if (!this.img) return;
    clearTimeout(this.retryTimer);

    const mode = stateManager.get("liveMode") || "video_feed";
    const token = stateManager.get("token");
    const streamUrl = apiClient.getStreamUrl(mode, token);

    if (this.badgeText) {
      this.badgeText.textContent = "CONNECTING EDGE STREAM...";
    }

    this.img.src = streamUrl;

    this.img.onload = () => {
      this.retryDelay = 1000;
      this.retryCount = 0;
      this.isSimulated = false;
      if (this.badgeText) {
        this.badgeText.textContent = `LIVE: ${mode.toUpperCase()}`;
      }
      eventBus.emit("stream:connected", mode);
    };

    this.img.onerror = () => {
      this.retryCount++;
      if (this.retryCount > 2 && !this.isSimulated) {
        // Fallback to sample factory visual loop so operator can always interact
        this.isSimulated = true;
        this.img.src = "assets/photo.png";
        if (this.badgeText) {
          this.badgeText.textContent = `SIMULATED OPTICAL FEED: ${mode.toUpperCase()}`;
        }
        return;
      }

      if (this.badgeText) {
        this.badgeText.textContent = `STREAM CONNECTING (${Math.round(this.retryDelay / 1000)}s)...`;
      }
      eventBus.emit("stream:dropped");
      clearTimeout(this.retryTimer);
      this.retryTimer = setTimeout(() => {
        this.retryDelay = Math.min(this.retryDelay * 1.5, this.maxDelay);
        this.connect();
      }, this.retryDelay);
    };
  }

  disconnect() {
    clearTimeout(this.retryTimer);
    if (this.img) {
      this.img.src = "";
    }
  }

  forceReset() {
    this.retryDelay = 1000;
    this.retryCount = 0;
    this.isSimulated = false;
    this.connect();
  }
}
