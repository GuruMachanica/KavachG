# safety_copilot.py - Industrial Safety AI Copilot & Incident Triage Agent
import os
import json
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime
from database import DB_PATH

OSHA_STANDARDS = {
    "ppe": {
        "standard": "OSHA 1910.132 / 1910.135",
        "title": "Personal Protective Equipment & Head Protection",
        "criticality": "High",
        "guidelines": "Employers must provide and enforce compliant protective helmets and high-visibility apparel in active industrial/machinery zones.",
        "actions": [
            "Issue immediate verbal warning and halt unsafe activity.",
            "Verify hardhat ANSI Z89.1 certification and chinstrap integrity.",
            "Log compliance audit entry in safety registry."
        ]
    },
    "fire-smoke": {
        "standard": "OSHA 1910.38 / 1910.157",
        "title": "Emergency Action Plans & Portable Fire Suppression",
        "criticality": "Critical Emergency",
        "guidelines": "Immediate area evacuation required upon thermal/optical flame detection exceeding threshold.",
        "actions": [
            "Trigger regional acoustic alarm siren.",
            "Dispatch rapid-response fire suppression team.",
            "Isolate electrical/gas supply valves in sector."
        ]
    },
    "fall": {
        "standard": "OSHA 1910.28 / 1926.501",
        "title": "Duty to Have Fall Protection & Walking-Working Surfaces",
        "criticality": "Critical Life Safety",
        "guidelines": "Unstable or fallen worker requires immediate medical triage and perimeter stabilization.",
        "actions": [
            "Dispatch certified First Aid / EMT responder to exact camera zone.",
            "Check for head trauma and spinal stabilization protocols.",
            "Inspect floor surface for chemical spills, oil, or physical trip hazards."
        ]
    },
    "restricted": {
        "standard": "OSHA 1910.147 / 1910.212",
        "title": "Hazardous Energy Isolation & Machine Guarding Virtual Perimeter",
        "criticality": "High",
        "guidelines": "Unauthorized entry into hazardous machinery zone violates virtual safety perimeter.",
        "actions": [
            "Issue automated PA audio announcement: 'Restricted Zone Breach'.",
            "Verify worker authorization badge credentials.",
            "Initiate emergency machine interlock if worker approaches moving drive."
        ]
    }
}


def analyze_incident_with_ai(incident_type: str, confidence: float, camera_id: int) -> dict:
    """Triage and generate automated OSHA root-cause analysis for any incident."""
    norm_type = incident_type.lower()
    matched = None
    for k in OSHA_STANDARDS:
        if k in norm_type or norm_type in k:
            matched = OSHA_STANDARDS[k]
            break

    if not matched:
        matched = {
            "standard": "OSHA 1910 General Duty Clause Section 5(a)(1)",
            "title": "General Workplace Hazard",
            "criticality": "Moderate",
            "guidelines": "Maintain standard safe operating perimeter and clear area.",
            "actions": ["Notify floor supervisor.", "Review camera footage."]
        }

    return {
        "incident_type": incident_type,
        "standard_code": matched["standard"],
        "standard_title": matched["title"],
        "criticality": matched["criticality"],
        "triage_summary": f"Detected {incident_type} on Camera {camera_id} (Confidence {int(confidence*100)}%). {matched['guidelines']}",
        "recommended_actions": matched["actions"],
        "escalation_required": matched["criticality"] in ["Critical Life Safety", "Critical Emergency"]
    }


def generate_daily_safety_briefing() -> dict:
    """Aggregate recent alerts and compile automated shift safety briefing."""
    if not os.path.exists(DB_PATH):
        return {
            "safety_posture": "Optimal",
            "open_violations": 0,
            "recent_alerts": [],
            "copilot_recommendation": "Database initializing. All systems nominal.",
            "generated_at": datetime.utcnow().isoformat()
        }

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT count(*) FROM incidents WHERE status = 'Open'")
        open_count = c.fetchone()[0]

        c.execute("SELECT type, status, count(*) FROM incidents GROUP BY type, status")
        breakdown = c.fetchall()

        c.execute("SELECT type, description, created_at FROM incidents ORDER BY id DESC LIMIT 5")
        recent = c.fetchall()

    status_posture = "Optimal" if open_count == 0 else ("Caution" if open_count < 4 else "Elevated Risk")

    return {
        "safety_posture": status_posture,
        "open_violations": open_count,
        "recent_alerts": [
            {"type": r[0], "desc": r[1], "time": r[2]} for r in recent
        ],
        "copilot_recommendation": (
            "All systems nominal. Maintain routine perimeter surveillance."
            if open_count == 0 else
            f"Attention Required: {open_count} unresolved safety anomalies detected across plant zones. Prioritize open PPE and fall alerts."
        ),
        "generated_at": datetime.utcnow().isoformat()
    }


def _query_mistral_llm(query: str, briefing: dict) -> str:
    """Optional Cloud LLM reasoning via Mistral AI if MISTRAL_API_KEY is configured."""
    api_key = os.getenv("MISTRAL_API_KEY") or os.getenv("MISTRAL_KEY")
    if not api_key:
        return None

    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        system_prompt = (
            "You are the KavachG AI Safety Copilot by Team CodeGambit. "
            "You are an industrial safety intelligence assistant specializing in OSHA 1910 regulatory mandates, "
            "worker PPE compliance, skeletal fall kinematics, and chemical/thermal hazard mitigations. "
            f"Current plant posture: {briefing['safety_posture']} with {briefing['open_violations']} open incidents. "
            "Provide concise, actionable, and professional safety guidance."
        )

        payload = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.3,
            "max_tokens": 350
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=7) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[WARN] Mistral API call failed: {e}. Falling back to built-in OSHA engine.")
        return None


def ask_safety_copilot(query: str) -> dict:
    """Conversational AI agent endpoint answering operator questions about plant safety policies and live metrics."""
    q = query.lower()
    briefing = generate_daily_safety_briefing()

    # 1. Check for Mistral AI response
    mistral_response = _query_mistral_llm(query, briefing)
    if mistral_response:
        return {
            "query": query,
            "response": mistral_response,
            "engine": "Mistral AI (Cloud LLM)",
            "posture": briefing["safety_posture"],
            "open_violations": briefing["open_violations"]
        }

    # 2. Built-in Offline OSHA 1910 Engine
    if "how many" in q or "count" in q or "today" in q or "status" in q:
        response = f"Currently, there are {briefing['open_violations']} open safety anomalies in the plant. The overall safety posture is rated as **{briefing['safety_posture']}**."
    elif "fall" in q:
        rule = OSHA_STANDARDS["fall"]
        response = f"**Fall Safety Protocol ({rule['standard']})**: When a fall is detected, immediately dispatch EMT to the camera coordinates. Do not move the worker if spinal injury is suspected. Verify that floor surfaces are clear of oil or water."
    elif "ppe" in q or "helmet" in q or "vest" in q:
        rule = OSHA_STANDARDS["ppe"]
        response = f"**PPE Compliance Policy ({rule['standard']})**: All workers inside machinery and active construction sectors must wear ANSI-compliant hardhats and high-visibility vests. Supervisors are notified automatically upon sustained violation."
    elif "fire" in q or "smoke" in q:
        rule = OSHA_STANDARDS["fire-smoke"]
        response = f"**Fire Emergency Standard ({rule['standard']})**: Immediate sound alarm dispatch. Verify fire suppression access and clear exit routes in the affected zone."
    else:
        response = f"KavachG Safety Copilot: Monitoring active streams. Current plant risk status is **{briefing['safety_posture']}**. Recommended action: {briefing['copilot_recommendation']}"

    return {
        "query": query,
        "response": response,
        "engine": "KavachG OSHA-1910 Core (Local)",
        "posture": briefing["safety_posture"],
        "open_violations": briefing["open_violations"]
    }
