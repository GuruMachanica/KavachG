// app.js - VajraNetra Autonomous Industrial Safety Command Center Bootstrap
import { eventBus } from "./core/EventBus.js";
import { stateManager } from "./core/StateManager.js";
import { apiClient } from "./core/ApiClient.js";
import { wsService } from "./core/WebSocketService.js";
import { audioAlertEngine } from "./core/AudioAlertEngine.js";
import { emailAlertService } from "./core/EmailAlertService.js";
import { voiceEngine } from "./core/VoiceAnnouncementEngine.js";
import { threeBackground } from "./ui/ThreeBackground.js";
import { animationEngine } from "./ui/AnimationEngine.js";

import { OverviewView } from "./views/OverviewView.js";
import { DetectionView } from "./views/DetectionView.js";
import { DigitalTwinView } from "./views/DigitalTwinView.js";
import { IncidentsView } from "./views/IncidentsView.js";
import { CopilotView } from "./views/CopilotView.js";
import { SettingsView } from "./views/SettingsView.js";
import { modalManager } from "./ui/ModalManager.js";

export class VajraNetraApplication {
  constructor() {
    this.views = {
      overview: new OverviewView(),
      detection: new DetectionView(),
      digitaltwin: new DigitalTwinView(),
      incidents: new IncidentsView(),
      copilot: new CopilotView(),
      settings: new SettingsView(),
    };
  }

  init() {
    // 1. Initialize 3D Background & Email Alert Service
    threeBackground.init();
    emailAlertService.init();

    // 2. Setup Event Bus Listeners
    this._setupEvents();

    // 3. Check Authentication State
    if (stateManager.isAuthenticated()) {
      this._showApp();
      this.switchTab("overview");
      this.refreshData();
      wsService.connect();
    } else {
      this._showLogin();
    }
  }

  _setupEvents() {
    // Tab switching
    eventBus.on("nav:tab", (tab) => this.switchTab(tab));

    // Toast notifications
    eventBus.on("toast", ({ message, type = "ok" }) => this.showToast(message, type));

    // Incident alert
    eventBus.on("incident:alert", (incident) => {
      this.showToast(`HAZARD DETECTED: ${incident?.type?.toUpperCase() || "ALERT"}`, "error");
      threeBackground.setThreatLevel(true);
      emailAlertService.sendIncidentAlert(incident);
      voiceEngine.announceIncident(incident);
      this.refreshData();
    });

    // WebSocket data sync
    eventBus.on("ws:update", () => this.refreshData());

    // Refresh request
    eventBus.on("data:refresh", () => this.refreshData());

    // Export CSV request
    eventBus.on("incidents:export", () => this._exportCsv());

    // Auth events
    eventBus.on("auth:logout", () => {
      wsService.disconnect();
      this._showLogin();
    });

    // DOM Global Event Listeners
    document.querySelectorAll(".sidebar-nav-btn[data-tab], .nav-btn[data-tab]").forEach((btn) => {
      btn.addEventListener("click", () => this.switchTab(btn.dataset.tab));
    });

    document.getElementById("btn-new-audit")?.addEventListener("click", () => {
      this.switchTab("incidents");
      this.showToast("Initiating rapid OSHA 1910 subpart inspection...");
    });

    // Support Modal
    document.getElementById("sidebar-support-btn")?.addEventListener("click", () => {
      modalManager.showSupportModal();
    });

    // System Log Modal
    document.getElementById("sidebar-syslog-btn")?.addEventListener("click", () => {
      modalManager.showSystemLogModal();
    });

    // Admin Profile Modal
    document.querySelectorAll(".user-session-card, .user-avatar, #welcome-text").forEach((el) => {
      el.style.cursor = "pointer";
      el.addEventListener("click", (e) => {
        if (e.target.id !== "logout-btn") {
          modalManager.showAdminProfileModal();
        }
      });
    });

    document.getElementById("logout-btn")?.addEventListener("click", () => {
      stateManager.clearAuth();
    });


    document.getElementById("voice-toggle-btn")?.addEventListener("click", (e) => {
      voiceEngine.toggle(!voiceEngine.enabled);
      e.target.innerHTML = voiceEngine.enabled 
        ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg> <span>Voice ON</span>`
        : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg> <span>Voice OFF</span>`;
      e.target.className = `icon-btn ${voiceEngine.enabled ? "" : "muted-sound"}`;
      this.showToast(voiceEngine.enabled ? "AI Voice PA system enabled." : "AI Voice PA system muted.");
    });

    document.getElementById("alarm-toggle-btn")?.addEventListener("click", (e) => {
      const current = stateManager.get("audioAlarmEnabled");
      stateManager.set("audioAlarmEnabled", !current);
      e.target.innerHTML = !current 
        ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/></svg> <span>Sound ON</span>`
        : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><line x1="1" y1="1" x2="23" y2="23"/></svg> <span>Sound OFF</span>`;
      e.target.className = `icon-btn ${!current ? "" : "muted-sound"}`;
      this.showToast(!current ? "Audio alarms enabled." : "Audio alarms muted.");
    });

    // Login Form Handler
    document.getElementById("login-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("login-email").value.trim();
      const password = document.getElementById("login-password").value;
      const errorEl = document.getElementById("login-error");
      const btn = document.getElementById("login-btn");

      errorEl.textContent = "";
      btn.disabled = true;
      btn.textContent = "Authenticating...";

      try {
        const data = await apiClient.login(email, password);
        stateManager.setAuth(data.access_token, data.user);
        this._showApp();
        this.switchTab("overview");
        await this.refreshData();
        wsService.connect();
        this.showToast(`Welcome back, ${data.user.name || "Operator"}!`);
      } catch (err) {
        errorEl.textContent = err.message;
      } finally {
        btn.disabled = false;
        btn.textContent = "Authenticate & Launch Console";
      }
    });
  }

  switchTab(tabName) {
    stateManager.set("currentTab", tabName);

    document.querySelectorAll(".tab-content").forEach((tab) => tab.classList.add("hidden"));
    document.querySelectorAll(".sidebar-nav-btn, .nav-btn").forEach((btn) => btn.classList.remove("active"));

    const activeView = this.views[tabName];
    const activeTabEl = document.getElementById(`tab-${tabName}`);
    const activeBtnEls = document.querySelectorAll(`[data-tab='${tabName}']`);

    if (activeTabEl) {
      activeTabEl.classList.remove("hidden");
      animationEngine.fadeIn(activeTabEl);
    }
    activeBtnEls.forEach((btn) => btn.classList.add("active"));

    if (activeView) {
      activeView.render();
    }
  }


  async refreshData() {
    try {
      const [incidents, sens, cams, zones] = await Promise.all([
        apiClient.getIncidents(),
        apiClient.getSensitivity(),
        apiClient.getCameras(),
        apiClient.getZones(),
      ]);

      stateManager.set("incidents", incidents);
      stateManager.set("sensitivity", sens.sensitivity);
      stateManager.set("cameras", cams);
      stateManager.set("zones", zones);

      this._updateSystemStatusPill();

      const currentTab = stateManager.get("currentTab");
      if (this.views[currentTab]) {
        this.views[currentTab].render();
      }
    } catch (err) {
      console.error("[App] Data sync failed:", err);
    }
  }

  _updateSystemStatusPill() {
    const pill = document.getElementById("system-status-indicator");
    const text = document.getElementById("system-status-text");
    if (!pill || !text) return;

    const incidents = stateManager.get("incidents") || [];
    const openIncidents = incidents.filter((i) => i.status === "Open");
    const hasCritical = openIncidents.some((i) =>
      ["fall", "fire-smoke", "fire"].includes(String(i.type).toLowerCase())
    );

    if (hasCritical) {
      pill.className = "status-pill status-pill-danger";
      text.textContent = `${openIncidents.length} Critical Hazard(s) Active`;
      threeBackground.setThreatLevel(true);
    } else if (openIncidents.length > 0) {
      pill.className = "status-pill status-pill-warning";
      text.textContent = `${openIncidents.length} Incident(s) Pending`;
      threeBackground.setThreatLevel(false);
    } else {
      pill.className = "status-pill status-pill-safe";
      text.textContent = "All Systems Operational";
      threeBackground.setThreatLevel(false);
    }
  }

  _showApp() {
    document.getElementById("login-view")?.classList.add("hidden");
    document.getElementById("app-view")?.classList.remove("hidden");
    const user = stateManager.get("user");
    const welcome = document.getElementById("welcome-text");
    if (welcome) {
      welcome.textContent = `${user?.name || user?.email || "Operator"}`;
    }
  }

  _showLogin() {
    document.getElementById("app-view")?.classList.add("hidden");
    document.getElementById("login-view")?.classList.remove("hidden");
  }

  showToast(message, type = "ok") {
    const toast = document.createElement("div");
    toast.className = `toast ${type === "error" ? "toast-error" : "toast-ok"}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2800);
  }

  _exportCsv() {
    const incidents = stateManager.get("incidents") || [];
    const header = "ID,Type,Description,Status,Created_At,Confidence\n";
    const rows = incidents.map((i) =>
      [
        i.id,
        `"${String(i.type || "").replaceAll('"', '""')}"`,
        `"${String(i.description || "").replaceAll('"', '""')}"`,
        `"${String(i.status || "").replaceAll('"', '""')}"`,
        `"${i.created_at}"`,
        i.confidence || "",
      ].join(",")
    );
    const blob = new Blob([header + rows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `vajranetra_incidents_${Date.now()}.csv`;
    a.click();
    this.showToast("Incident log CSV exported successfully.");
  }
}

// Bootstrap on DOM Ready
window.addEventListener("DOMContentLoaded", () => {
  const app = new VajraNetraApplication();
  app.init();
  window.vajraNetraApp = app;
});
