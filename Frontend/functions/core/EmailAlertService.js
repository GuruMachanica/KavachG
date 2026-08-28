// EmailAlertService.js - OOP EmailJS Incident Notification System
import { eventBus } from "./EventBus.js";

export class EmailAlertService {
  constructor() {
    this.config = {
      enabled: JSON.parse(localStorage.getItem("email_alerts_enabled") ?? "false"),
      serviceId: localStorage.getItem("emailjs_service_id") || "",
      templateId: localStorage.getItem("emailjs_template_id") || "",
      publicKey: localStorage.getItem("emailjs_public_key") || "",
      recipientEmail: localStorage.getItem("emailjs_recipient") || "safety-officer@plant.com",
    };
    this.lastSentTimes = new Map();
    this.cooldownSeconds = 60; // Prevent spamming for same incident type
    this.isInitialized = false;
  }

  init() {
    if (typeof emailjs !== "undefined" && this.config.publicKey) {
      try {
        emailjs.init({ publicKey: this.config.publicKey });
        this.isInitialized = true;
        console.log("[EmailAlertService] EmailJS initialized successfully.");
      } catch (err) {
        console.error("[EmailAlertService] Failed to initialize EmailJS:", err);
      }
    }
  }

  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    localStorage.setItem("email_alerts_enabled", JSON.stringify(this.config.enabled));
    localStorage.setItem("emailjs_service_id", this.config.serviceId);
    localStorage.setItem("emailjs_template_id", this.config.templateId);
    localStorage.setItem("emailjs_public_key", this.config.publicKey);
    localStorage.setItem("emailjs_recipient", this.config.recipientEmail);

    if (this.config.publicKey && typeof emailjs !== "undefined") {
      emailjs.init({ publicKey: this.config.publicKey });
      this.isInitialized = true;
    }
  }

  getConfig() {
    return { ...this.config };
  }

  async sendIncidentAlert(incident) {
    if (!this.config.enabled) return false;
    if (!this.config.serviceId || !this.config.templateId || !this.config.publicKey) {
      console.warn("[EmailAlertService] Email alerts enabled but EmailJS credentials are incomplete.");
      return false;
    }

    const type = String(incident.type || "hazard").toLowerCase();
    const now = Date.now();
    const lastSent = this.lastSentTimes.get(type) || 0;

    // Apply cooldown check
    if (now - lastSent < this.cooldownSeconds * 1000) {
      console.log(`[EmailAlertService] Suppressing duplicate email for '${type}' (Cooldown active).`);
      return false;
    }

    const templateParams = {
      to_email: this.config.recipientEmail,
      incident_id: incident.id ? `#${incident.id}` : "LIVE_ALERT",
      incident_type: String(incident.type || "Safety Hazard").toUpperCase(),
      incident_description: incident.description || "Automated computer vision hazard alert triggered.",
      timestamp: incident.created_at ? new Date(incident.created_at).toLocaleString() : new Date().toLocaleString(),
      camera_id: incident.camera_id !== undefined ? `Camera #${incident.camera_id}` : "Zone Surveillance",
      confidence: incident.confidence ? `${Math.round(incident.confidence * 100)}%` : "N/A",
      dashboard_url: window.location.origin,
    };

    try {
      if (typeof emailjs === "undefined") {
        throw new Error("EmailJS SDK not loaded in browser.");
      }

      await emailjs.send(this.config.serviceId, this.config.templateId, templateParams);
      this.lastSentTimes.set(type, now);
      eventBus.emit("toast", { message: `📧 Emergency Email Alert dispatched to ${this.config.recipientEmail}` });
      return true;
    } catch (error) {
      console.error("[EmailAlertService] Failed to send email via EmailJS:", error);
      eventBus.emit("toast", { message: `Email alert failed: ${error.text || error.message}`, type: "error" });
      return false;
    }
  }

  async sendTestAlert() {
    return this.sendIncidentAlert({
      id: "TEST-01",
      type: "PPE Violation (Test)",
      description: "This is a verification test email from the KavachG Safety Command Center.",

      created_at: new Date().toISOString(),
      camera_id: 0,
      confidence: 0.98,
    });
  }
}

export const emailAlertService = new EmailAlertService();
