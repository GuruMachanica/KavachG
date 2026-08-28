// app.js - KavachG Autonomous Industrial Safety Command Center Bootstrap (Lazy Loaded & Mobile Optimized)
import { eventBus } from "./core/EventBus.js";
import { stateManager } from "./core/StateManager.js";
import { apiClient } from "./core/ApiClient.js";
import { wsService } from "./core/WebSocketService.js";
import { audioAlertEngine } from "./core/AudioAlertEngine.js";
import { emailAlertService } from "./core/EmailAlertService.js";
import { voiceEngine } from "./core/VoiceAnnouncementEngine.js";
import { threeBackground } from "./ui/ThreeBackground.js";
import { animationEngine } from "./ui/AnimationEngine.js";
import { modalManager } from "./ui/ModalManager.js";

// View Dynamic Loaders for Code Splitting & AJAX Lazy Loading
const BUILD_V = Date.now();
const VIEW_FACTORIES = {
  overview: () => import(`./views/OverviewView.js?v=${BUILD_V}`).then((m) => new m.OverviewView()),
  detection: () => import(`./views/DetectionView.js?v=${BUILD_V}`).then((m) => new m.DetectionView()),
  digitaltwin: () => import(`./views/DigitalTwinView.js?v=${BUILD_V}`).then((m) => new m.DigitalTwinView()),
  incidents: () => import(`./views/IncidentsView.js?v=${BUILD_V}`).then((m) => new m.IncidentsView()),
  copilot: () => import(`./views/CopilotView.js?v=${BUILD_V}`).then((m) => new m.CopilotView()),
  settings: () => import(`./views/SettingsView.js?v=${BUILD_V}`).then((m) => new m.SettingsView()),
};


export class KavachGApplication {
  constructor() {
    this.views = {};
    this.loadingView = false;
  }

  init() {
    // 1. Initialize 3D Background & Alert Services
    threeBackground.init();
    emailAlertService.init();

    // 2. Setup Event Bus Listeners
    this._setupEvents();

    // 3. Setup Mobile Navigation & Resize Handlers
    this._setupMobileNavigation();

    // 4. Check Authentication State
    if (stateManager.isAuthenticated()) {
      this._showApp();
      this.switchTab("overview");
      this.refreshData();
      wsService.connect();
      // Auto-poll database every 4 seconds
      setInterval(() => this.refreshData(), 4000);
    } else {
      this._showLogin();
    }
  }


  _setupEvents() {
    // Auth events
    eventBus.on("auth:logout", () => {
      this._showLogin();
      this.showToast("Logged out successfully.");
      wsService.disconnect();
    });

    eventBus.on("auth:login", () => {
      this._showApp();
      this.switchTab("overview");
      this.refreshData();
      wsService.connect();
    });

    // Tab switching
    eventBus.on("nav:tab", (tab) => this.switchTab(tab));

    // Toast notifications
    eventBus.on("toast", ({ message, type = "ok" }) => this.showToast(message, type));


    // Incident alerts
    eventBus.on("incident:alert", (incident) => {
      this.showToast(`HAZARD DETECTED: ${incident?.type?.toUpperCase() || "ALERT"}`, "error");
      audioAlertEngine.playAlarm();
      voiceEngine.announce(incident);
      emailAlertService.sendIncidentAlert(incident);
      this.refreshData();
    });

    // Global state updates
    eventBus.on("state:updated", ({ key, value }) => {
      if (key === "incidents") {
        const curTab = stateManager.get("currentTab");
        if (this.views[curTab]) {
          this.views[curTab].render();
        }
      }
    });

    // DOM Global Event Listeners
    document.querySelectorAll(".sidebar-nav-btn[data-tab], .nav-btn[data-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        this.switchTab(btn.dataset.tab);
        this.closeMobileSidebar();
      });
    });

    // Global Universal Command & Search Palette (Ctrl+K or Search Bar click)
    const openPalette = () => {
      modalManager.showCommandPalette();
    };

    document.getElementById("global-search-bar")?.addEventListener("click", openPalette);
    document.getElementById("global-search-input")?.addEventListener("click", openPalette);

    window.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        openPalette();
      }
    });

    document.getElementById("btn-new-audit")?.addEventListener("click", () => {
      this.switchTab("incidents");
      this.closeMobileSidebar();
      this.showToast("Initiating rapid OSHA 1910 subpart inspection...");
    });


    // Support Modal
    document.getElementById("sidebar-support-btn")?.addEventListener("click", () => {
      modalManager.showSupportModal();
      this.closeMobileSidebar();
    });

    // System Log Modal
    document.getElementById("sidebar-syslog-btn")?.addEventListener("click", () => {
      modalManager.showSystemLogModal();
      this.closeMobileSidebar();
    });

    // Admin Profile Modal
    document.querySelectorAll(".user-session-card, .user-avatar, #welcome-text").forEach((el) => {
      el.style.cursor = "pointer";
      el.addEventListener("click", (e) => {
        if (e.target.id !== "logout-btn") {
          modalManager.showAdminProfileModal();
          this.closeMobileSidebar();
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

  _setupMobileNavigation() {
    // Mobile Drawer Toggle Button
    const topHeader = document.querySelector(".top-header");
    if (topHeader && !document.getElementById("mobile-menu-btn")) {
      const menuBtn = document.createElement("button");
      menuBtn.id = "mobile-menu-btn";
      menuBtn.className = "mobile-menu-btn";
      menuBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>`;
      menuBtn.setAttribute("aria-label", "Toggle Navigation Menu");
      menuBtn.addEventListener("click", () => this.toggleMobileSidebar());
      topHeader.prepend(menuBtn);
    }

    // Mobile Backdrop
    if (!document.getElementById("sidebar-backdrop")) {
      const backdrop = document.createElement("div");
      backdrop.id = "sidebar-backdrop";
      backdrop.className = "sidebar-backdrop hidden";
      backdrop.addEventListener("click", () => this.closeMobileSidebar());
      document.body.appendChild(backdrop);
    }
  }

  toggleMobileSidebar() {
    const sidebar = document.querySelector(".sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) {
      const isOpen = sidebar.classList.toggle("sidebar-mobile-open");
      if (backdrop) {
        backdrop.classList.toggle("hidden", !isOpen);
      }
    }
  }

  closeMobileSidebar() {
    const sidebar = document.querySelector(".sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) sidebar.classList.remove("sidebar-mobile-open");
    if (backdrop) backdrop.classList.add("hidden");
  }

  /**
   * Dynamic Async View Lazy Loader & Tab Switcher
   */
  async switchTab(tabName) {
    if (this.loadingView) return;
    stateManager.set("currentTab", tabName);

    document.querySelectorAll(".tab-content").forEach((tab) => tab.classList.add("hidden"));
    document.querySelectorAll(".sidebar-nav-btn, .nav-btn").forEach((btn) => btn.classList.remove("active"));

    const activeTabEl = document.getElementById(`tab-${tabName}`);
    const activeBtnEls = document.querySelectorAll(`[data-tab='${tabName}']`);

    activeBtnEls.forEach((btn) => btn.classList.add("active"));

    // Lazy load the view module if not instantiated yet
    if (!this.views[tabName] && VIEW_FACTORIES[tabName]) {
      this.loadingView = true;
      try {
        this.views[tabName] = await VIEW_FACTORIES[tabName]();
      } catch (err) {
        console.error(`Failed to lazy-load view: ${tabName}`, err);
      } finally {
        this.loadingView = false;
      }
    }

    const activeView = this.views[tabName];
    if (activeTabEl) {
      activeTabEl.classList.remove("hidden");
      if (activeView && typeof activeView.render === "function") {
        activeView.render();
      }
      animationEngine.fadeIn(activeTabEl);
    }
  }

  async refreshData() {
    try {
      const [incidents, people, sensitivity, cameras] = await Promise.all([
        apiClient.getIncidents().catch(() => []),
        apiClient.getPeople().catch(() => []),
        apiClient.getSensitivity().catch(() => ({ confidence_threshold: 0.5 })),
        apiClient.getCameras().catch(() => []),
      ]);

      stateManager.set("incidents", incidents);
      stateManager.set("people", people);
      stateManager.set("sensitivity", sensitivity.confidence_threshold || 0.5);
      stateManager.set("cameras", cameras);

      const curTab = stateManager.get("currentTab") || "overview";
      if (this.views[curTab]) {
        this.views[curTab].render();
      }
    } catch (err) {
      console.warn("Telemetry polling warning:", err);
    }
  }

  showToast(message, type = "ok") {
    const container = document.getElementById("toast-container") || document.body;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  _showLogin() {
    document.getElementById("login-view")?.classList.remove("hidden");
    document.getElementById("app-view")?.classList.add("hidden");
  }

  _showApp() {
    document.getElementById("login-view")?.classList.add("hidden");
    document.getElementById("app-view")?.classList.remove("hidden");

    const user = stateManager.get("user");
    if (user && document.getElementById("welcome-text")) {
      document.getElementById("welcome-text").textContent = `${user.name || "Operator"}`;
    }
  }
}

// Bootstrap Application on DOM Ready
window.addEventListener("DOMContentLoaded", () => {
  const app = new KavachGApplication();
  app.init();
  window.kavachGApp = app;
});

