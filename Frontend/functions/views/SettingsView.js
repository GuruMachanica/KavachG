// SettingsView.js - Calibration & Configuration (Clean SVG Icons, No Emojis)
import { BaseView } from "./BaseView.js";
import { stateManager } from "../core/StateManager.js";
import { apiClient } from "../core/ApiClient.js";
import { eventBus } from "../core/EventBus.js";
import { emailAlertService } from "../core/EmailAlertService.js";
import { Icons } from "../ui/Icons.js";

export class SettingsView extends BaseView {
  constructor() {
    super("tab-settings");
  }

  render() {
    if (!this.container) return;

    const sensitivity = stateManager.get("sensitivity") || 50;
    const emailConfig = emailAlertService.getConfig();

    this.container.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
        <!-- AI Calibration -->
        <div class="panel" style="padding: 1.5rem;">
          <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
            <span style="color: var(--accent-cyan);">${Icons.settings}</span>
            <h3 style="font-size: 1.1rem; font-weight: 700;">AI Detection Sensitivity</h3>
          </div>
          <p class="muted" style="font-size: 0.85rem; margin-bottom: 1rem;">Calibrate false-positive tolerance vs hazard sensitivity.</p>
          
          <div class="stack">
            <label>Confidence Threshold: <span id="sens-label">${sensitivity}%</span></label>
            <input id="sens-slider" type="range" min="10" max="95" value="${sensitivity}" />
            <button id="sens-save-btn" class="btn-primary">Save Sensitivity Threshold</button>
          </div>
        </div>

        <!-- EmailJS Alert System -->
        <div class="panel" style="padding: 1.5rem;">
          <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
            <span style="color: var(--accent-cyan);">${Icons.mail}</span>
            <h3 style="font-size: 1.1rem; font-weight: 700;">EmailJS Emergency Dispatch</h3>
          </div>
          <p class="muted" style="font-size: 0.85rem; margin-bottom: 1rem;">Automate instant email dispatch upon critical safety breaches.</p>
          
          <form id="email-config-form" class="stack">
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input type="checkbox" id="email-alerts-enabled" ${emailConfig.enabled ? "checked" : ""} style="width: auto;" />
              <span>Enable Instant Email Incident Alerts</span>
            </label>

            <input id="email-service-id" value="${this.escape(emailConfig.serviceId)}" placeholder="EmailJS Service ID (e.g. service_xyz)" />
            <input id="email-template-id" value="${this.escape(emailConfig.templateId)}" placeholder="EmailJS Template ID (e.g. template_abc)" />
            <input id="email-public-key" value="${this.escape(emailConfig.publicKey)}" placeholder="EmailJS Public Key (e.g. user_123)" />
            <input id="email-recipient" type="email" value="${this.escape(emailConfig.recipientEmail)}" placeholder="Safety Officer Email (Recipient)" />

            <div style="display: flex; gap: 0.5rem;">
              <button type="submit" class="btn-primary" style="flex: 1;">Save Email Config</button>
              <button type="button" id="email-test-btn" class="btn-secondary">Send Test</button>
            </div>
          </form>
        </div>

        <!-- User Administration -->
        <div class="panel" style="padding: 1.5rem;">
          <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
            <span style="color: var(--accent-cyan);">${Icons.users}</span>
            <h3 style="font-size: 1.1rem; font-weight: 700;">Operator & Admin Provisioning</h3>
          </div>
          <p class="muted" style="font-size: 0.85rem; margin-bottom: 1rem;">Register new plant safety personnel credentials.</p>
          
          <form id="create-user-form" class="stack">
            <input id="new-user-name" required placeholder="Full Name" />
            <input id="new-user-email" type="email" required placeholder="operator@plant.com" />
            <input id="new-user-pass" type="password" required minlength="8" placeholder="Password (8+ chars)" />
            <select id="new-user-role">
              <option value="operator">Plant Operator</option>
              <option value="safety_officer">Safety Officer</option>
              <option value="admin">System Administrator</option>
            </select>
            <button type="submit" class="btn-primary">Provision Account</button>
          </form>
        </div>
      </div>
    `;

    // Sensitivity Slider
    const slider = this.container.querySelector("#sens-slider");
    const label = this.container.querySelector("#sens-label");
    if (slider && label) {
      slider.addEventListener("input", () => { label.textContent = `${slider.value}%`; });
    }

    this.container.querySelector("#sens-save-btn")?.addEventListener("click", async () => {
      try {
        const val = parseInt(slider.value, 10);
        await apiClient.setSensitivity(val);
        stateManager.set("sensitivity", val);
        eventBus.emit("toast", { message: "Detection sensitivity calibrated." });
      } catch (err) {
        eventBus.emit("toast", { message: err.message, type: "error" });
      }
    });

    // EmailJS Form
    this.container.querySelector("#email-config-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      const updated = {
        enabled: this.container.querySelector("#email-alerts-enabled").checked,
        serviceId: this.container.querySelector("#email-service-id").value.trim(),
        templateId: this.container.querySelector("#email-template-id").value.trim(),
        publicKey: this.container.querySelector("#email-public-key").value.trim(),
        recipientEmail: this.container.querySelector("#email-recipient").value.trim(),
      };
      emailAlertService.updateConfig(updated);
      eventBus.emit("toast", { message: "EmailJS notification settings saved." });
    });

    // EmailJS Test Button
    this.container.querySelector("#email-test-btn")?.addEventListener("click", async () => {
      eventBus.emit("toast", { message: "Dispatching verification test email..." });
      await emailAlertService.sendTestAlert();
    });

    // User Create Form
    this.container.querySelector("#create-user-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        name: this.container.querySelector("#new-user-name").value.trim(),
        email: this.container.querySelector("#new-user-email").value.trim(),
        password: this.container.querySelector("#new-user-pass").value,
        role: this.container.querySelector("#new-user-role").value,
      };
      try {
        await apiClient.createUser(payload);
        eventBus.emit("toast", { message: `Account for ${payload.name} created.` });
        e.target.reset();
      } catch (err) {
        eventBus.emit("toast", { message: err.message, type: "error" });
      }
    });
  }
}
