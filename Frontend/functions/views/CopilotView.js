// CopilotView.js - AI Safety Copilot Assistant (Prefilled Safety Intelligence & Fast Prompts)
import { BaseView } from "./BaseView.js";
import { apiClient } from "../core/ApiClient.js";
import { eventBus } from "../core/EventBus.js";
import { Icons } from "../ui/Icons.js";

export class CopilotView extends BaseView {
  constructor() {
    super("tab-copilot");
    this.messages = [
      {
        role: "ai",
        text: "Autonomous Safety Intelligence Initialized.\n• Active Vision Streams: 4 Channels\n• Current Compliance Index: 92% (OSHA 1910 Compliant)\n• Last Anomaly Logged: #ERR-Acoustic-99 (Sector Alpha Compressor Unit B)\n\nAsk any question about OSHA 1910 standard mappings, root-cause mitigations, or shift safety protocols.",
      },
    ];
  }

  render() {
    if (!this.container) return;

    const messagesHtml = this.messages.map((m) => `
      <div class="copilot-msg ${m.role === "user" ? "copilot-msg-user" : "copilot-msg-ai"}" style="padding: 1rem 1.25rem; border-radius: 12px; background: ${m.role === "user" ? "rgba(0, 240, 255, 0.12)" : "rgba(13, 22, 33, 0.85)"}; border: 1px solid ${m.role === "user" ? "var(--accent-cyan)" : "var(--border-subtle)"};">
        <div style="font-size: 0.75rem; font-family: var(--font-mono); margin-bottom: 0.35rem; color: ${m.role === "user" ? "var(--accent-cyan)" : "var(--accent-emerald)"}; font-weight: 700;">
          ${m.role === "user" ? "OPERATOR SESSION" : "VAJRANETRA SAFETY COPILOT"}
        </div>
        <div style="line-height: 1.6; font-size: 0.9rem; white-space: pre-line; color: #e2e8f0;">${this.escape(m.text)}</div>
      </div>
    `).join("");

    this.container.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 340px; gap: 1.5rem; align-items: start;">
        <!-- Left: Chat Panel -->
        <div class="panel" style="display: flex; flex-direction: column; height: 560px; padding: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="color: var(--accent-cyan);">${Icons.copilot}</span>
              <h3 style="font-size: 1.1rem; font-weight: 700;">OSHA Safety Copilot Agent</h3>
            </div>
            <span style="font-size: 0.75rem; color: var(--accent-emerald); font-family: var(--font-mono); background: rgba(0,229,163,0.1); padding: 2px 8px; border-radius: 4px; border: 1px solid var(--accent-emerald);">LLM REASONING READY</span>
          </div>

          <div id="copilot-history" style="flex: 1; overflow-y: auto; padding: 1rem 0; display: flex; flex-direction: column; gap: 0.85rem;">
            ${messagesHtml}
          </div>

          <form id="copilot-input-form" style="display: flex; gap: 0.5rem; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle);">
            <input id="copilot-query-input" placeholder="Ask about OSHA compliance, hazard protocols, or live risk rating..." style="flex: 1; background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle); color: #fff; padding: 0.65rem 1rem; border-radius: 8px;" required />
            <button type="submit" class="btn-primary" style="padding: 0 1.5rem; font-weight: 700;">Query</button>
          </form>
        </div>

        <!-- Right: OSHA Fast Prompt Chips -->
        <div style="display: flex; flex-direction: column; gap: 1rem;">
          <div class="panel" style="padding: 1.25rem;">
            <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
              <span style="color: var(--accent-cyan);">${Icons.audits}</span>
              <h4 style="font-size: 0.95rem; font-weight: 700;">Regulatory Quick-Chips</h4>
            </div>
            <p class="muted" style="font-size: 0.8rem; margin-bottom: 0.75rem;">Instant OSHA standard references</p>
            
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
              <button class="btn-secondary copilot-chip" style="font-size: 0.8rem; text-align: left; padding: 0.6rem 0.8rem;" data-prompt="What are the OSHA 1910.132 PPE compliance requirements for manufacturing floors?">
                OSHA 1910.132 (PPE Mandates)
              </button>
              <button class="btn-secondary copilot-chip" style="font-size: 0.8rem; text-align: left; padding: 0.6rem 0.8rem;" data-prompt="Explain OSHA 1910.28 walking-working surfaces and fall arrest criteria.">
                OSHA 1910.28 (Fall Protection)
              </button>
              <button class="btn-secondary copilot-chip" style="font-size: 0.8rem; text-align: left; padding: 0.6rem 0.8rem;" data-prompt="What immediate steps must be taken upon detecting optical smoke or flame?">
                OSHA 1910.38 (Emergency Response)
              </button>
            </div>
          </div>

          <div class="panel" style="padding: 1.25rem;">
            <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.25rem;">
              <span style="color: var(--accent-cyan);">${Icons.log}</span>
              <h4 style="font-size: 0.95rem; font-weight: 700;">Shift Briefing Generator</h4>
            </div>
            <p class="muted" style="font-size: 0.8rem; margin-bottom: 0.75rem;">Generate synthesized supervisor safety briefing</p>
            <button id="btn-gen-briefing" class="btn-secondary" style="width: 100%; font-size: 0.8rem; padding: 0.6rem;">Generate Briefing</button>
          </div>
        </div>
      </div>
    `;

    // Prompt chip listeners
    this.container.querySelectorAll(".copilot-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const prompt = chip.dataset.prompt;
        const input = this.container.querySelector("#copilot-query-input");
        if (input) {
          input.value = prompt;
          this._handleQuery(prompt);
        }
      });
    });

    this.container.querySelector("#copilot-input-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = this.container.querySelector("#copilot-query-input");
      const text = input.value.trim();
      if (text) {
        input.value = "";
        this._handleQuery(text);
      }
    });

    this.container.querySelector("#btn-gen-briefing")?.addEventListener("click", async () => {
      try {
        eventBus.emit("toast", { message: "Compiling daily safety briefing..." });
        const briefing = await apiClient.getCopilotBriefing();
        this.messages.push({ role: "ai", text: `[DAILY SHIFT BRIEFING]\nRisk Posture: ${briefing.risk_posture}\nOpen Hazards: ${briefing.open_incidents}\nSummary: ${briefing.summary}` });
        this.render();
      } catch (err) {
        eventBus.emit("toast", { message: err.message, type: "error" });
      }
    });
  }

  async _handleQuery(text) {
    this.messages.push({ role: "user", text });
    this.render();

    try {
      const res = await apiClient.queryCopilot(text);
      this.messages.push({ role: "ai", text: res.response || "No response received." });
    } catch (err) {
      this.messages.push({ role: "ai", text: `Error: ${err.message}` });
    }
    this.render();
  }
}
