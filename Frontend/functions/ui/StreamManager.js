// StreamManager.js - Live Camera Stream Controller (Backend MJPEG + Direct Local WebCam)
import { apiClient } from "../core/ApiClient.js";
import { stateManager } from "../core/StateManager.js";
import { eventBus } from "../core/EventBus.js";

export class StreamManager {
  constructor(imgElement, badgeTextElement, videoElement = null) {
    this.img = imgElement;
    this.badgeText = badgeTextElement;
    this.video = videoElement;
    this.retryTimer = null;
    this.retryCount = 0;
    this.retryDelay = 1000;
    this.maxDelay = 6000;
    this.isLocalWebcam = false;
    this.localStream = null;
  }

  connect(forceMode = null) {
    if (!this.img) return;
    clearTimeout(this.retryTimer);

    if (this.isLocalWebcam) {
      this.stopLocalWebcam();
    }

    const mode = forceMode || stateManager.get("liveMode") || "video_feed";
    const token = stateManager.get("token");
    const streamUrl = apiClient.getStreamUrl(mode, token);

    if (this.badgeText) {
      this.badgeText.textContent = "CONNECTING LIVE OPTICAL STREAM...";
    }

    // Connect to live backend stream with cache-busting timestamp
    this.img.src = `${streamUrl}&_t=${Date.now()}`;
    this.img.style.display = "block";
    if (this.video) this.video.style.display = "none";

    this.img.onload = () => {
      this.retryDelay = 1000;
      this.retryCount = 0;
      if (this.badgeText) {
        this.badgeText.textContent = `LIVE FEED: ${mode.toUpperCase().replace("/", " ")}`;
      }
      eventBus.emit("stream:connected", mode);
    };

    this.img.onerror = () => {
      this.retryCount++;
      if (this.badgeText) {
        this.badgeText.textContent = `RECONNECTING LIVE CAMERA (${this.retryCount})...`;
      }
      eventBus.emit("stream:dropped");
      clearTimeout(this.retryTimer);
      this.retryTimer = setTimeout(() => {
        this.retryDelay = Math.min(this.retryDelay * 1.5, this.maxDelay);
        this.connect(mode);
      }, this.retryDelay);
    };
  }

  async startLocalWebcam(videoEl) {
    clearTimeout(this.retryTimer);
    this.video = videoEl || this.video;

    try {
      if (this.badgeText) {
        this.badgeText.textContent = "REQUESTING LOCAL DEVICE WEBCAM...";
      }

      this.localStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });

      if (this.video) {
        this.video.srcObject = this.localStream;
        this.video.play();
        this.video.style.display = "block";
      }
      if (this.img) this.img.style.display = "none";

      this.isLocalWebcam = true;
      if (this.badgeText) {
        this.badgeText.textContent = "LIVE: DIRECT LOCAL WEBCAM ACTIVE";
      }
      eventBus.emit("stream:local_connected");
    } catch (err) {
      console.warn("Direct webcam access unavailable, falling back to backend stream:", err);
      this.isLocalWebcam = false;
      this.connect();
    }
  }

  stopLocalWebcam() {
    if (this.localStream) {
      this.localStream.getTracks().forEach((t) => t.stop());
      this.localStream = null;
    }
    this.isLocalWebcam = false;
  }

  disconnect() {
    clearTimeout(this.retryTimer);
    this.stopLocalWebcam();
    if (this.img) this.img.src = "";
  }

  forceReset() {
    this.retryDelay = 1000;
    this.retryCount = 0;
    this.disconnect();
    this.connect();
  }
}
