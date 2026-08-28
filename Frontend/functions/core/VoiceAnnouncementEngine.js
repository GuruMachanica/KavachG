// VoiceAnnouncementEngine.js - Automated Industrial PA / Text-to-Speech Engine
import { stateManager } from "./StateManager.js";

export class VoiceAnnouncementEngine {
  constructor() {
    this.synth = window.speechSynthesis || null;
    this.enabled = JSON.parse(localStorage.getItem("voice_alerts_enabled") ?? "true");
    this.lastAnnouncementTime = 0;
    this.cooldownMs = 15000; // 15s between voice announcements
    this.voice = null;
    this._initVoice();
  }

  _initVoice() {
    if (!this.synth) return;
    const setVoice = () => {
      const voices = this.synth.getVoices();
      // Select an authoritative English voice
      this.voice = voices.find((v) => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("David"))) || voices[0];
    };
    setVoice();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = setVoice;
    }
  }

  toggle(enabled) {
    this.enabled = enabled;
    localStorage.setItem("voice_alerts_enabled", JSON.stringify(enabled));
  }

  announce(message, priority = "normal") {
    if (!this.synth || !this.enabled) return;
    const now = Date.now();
    if (priority !== "critical" && now - this.lastAnnouncementTime < this.cooldownMs) {
      return;
    }

    this.synth.cancel(); // Cancel any existing speech
    const utterance = new SpeechSynthesisUtterance(message);
    if (this.voice) utterance.voice = this.voice;
    utterance.rate = 1.05;
    utterance.pitch = priority === "critical" ? 1.15 : 1.0;
    utterance.volume = 1.0;

    this.lastAnnouncementTime = now;
    this.synth.speak(utterance);
  }

  announceIncident(incident) {
    const type = String(incident.type || "").toLowerCase();
    const camId = incident.camera_id !== undefined ? `Camera ${incident.camera_id}` : "Main Sector";

    if (type.includes("fire") || type.includes("smoke")) {
      this.announce(`Emergency Alert: Fire hazard detected on ${camId}. Evacuate sector immediately.`, "critical");
    } else if (type.includes("fall")) {
      this.announce(`Urgent Alert: Worker fall detected on ${camId}. First aid responder dispatched.`, "critical");
    } else if (type.includes("ppe") || type.includes("hardhat") || type.includes("vest")) {
      this.announce(`Safety Warning: PPE non-compliance detected on ${camId}. Protective gear required.`, "normal");
    } else if (type.includes("zone") || type.includes("restrict")) {
      this.announce(`Security Warning: Unauthorized entry into restricted perimeter on ${camId}.`, "critical");
    } else {
      this.announce(`Safety Notice: Anomaly logged on ${camId}.`, "normal");
    }
  }
}

export const voiceEngine = new VoiceAnnouncementEngine();
