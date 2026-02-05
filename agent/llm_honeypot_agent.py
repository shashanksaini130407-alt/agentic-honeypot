import requests
import time
import random
import re
import json
from datetime import datetime
from langdetect import detect, LangDetectException
import os

from agent.memory.conversation_memory import ConversationMemory
from agent.persona import get_persona
from agent.scam_classifier import ScamClassifier

# ------------------------ GROQ API CONFIG ------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # You can change to another Groq model if desired

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please set it in .env file or environment variables.")

MOCK_SCAMMER_API = "http://localhost:5000/mock_scammer"  # Example API

# ------------------------ Scammer Profiler ------------------------
class ScammerProfiler:
    def profile(self, text: str) -> str:
        text = text.lower()
        if any(w in text for w in ["urgent", "immediately", "now", "otp", "closed"]):
            return "aggressive"
        if any(w in text for w in ["sir", "dear", "official", "customer"]):
            return "authority"
        if any(w in text for w in ["install", "app", "download", "link"]):
            return "technical"
        return "friendly"

# ------------------------ Elite Autonomous Honeypot ------------------------
class LLMHoneypotAgent:
    def __init__(self):
        self.stage = "initial"
        self.memory = ConversationMemory(max_memory=12)
        self.classifier = ScamClassifier()

        self.persona_name = None
        self.persona_prompt = None

        self.profiler = ScammerProfiler()
        self.scammer_style = "unknown"
        self.conversation_score = 0

        self.dynamic_memory = {
            "otp_requests": 0,
            "payment_requests": 0,
            "trust_attempts": 0,
            "last_traps_used": [],
            "scammer_style_history": [],
            "frustration_level": 0
        }

    # ------------------------ Language Detection ------------------------
    def _detect_language(self, text: str) -> str:
        try:
            if all(ord(c) < 128 for c in text):
                return "en"
            return detect(text)
        except LangDetectException:
            return "en"

    # ------------------------ Stage Detection ------------------------
    def _update_stage(self, msg: str):
        msg_lower = msg.lower()
        if "otp" in msg_lower:
            self.stage = "otp"
            self.dynamic_memory["otp_requests"] += 1
        elif any(k in msg_lower for k in ["upi", "bank", "account", "payment", "transfer"]):
            self.stage = "payment"
            self.dynamic_memory["payment_requests"] += 1
        elif any(k in msg_lower for k in ["verify", "confirm", "id", "official"]):
            self.stage = "trust"
            self.dynamic_memory["trust_attempts"] += 1

    # ------------------------ Score Update ------------------------
    def _update_score(self, message: str):
        keywords = ["otp", "upi", "transfer", "payment", "bank", "account"]
        self.conversation_score += 2 if any(k in message.lower() for k in keywords) else 1

    # ------------------------ Generate Bait / Trap Question ------------------------
    def _generate_bait_hint(self):
        stage_traps = {
            "otp": ["Can you confirm your employee ID?", "Why does my bank warn against sharing OTP?"],
            "payment": ["Which branch are you calling from?", "Can I verify this with my bank first?"],
            "trust": ["Should I note your full name?", "Do you have an official reference number?"],
            "initial": ["What is your official work number?", "Can I confirm this with customer service?"]
        }
        traps = stage_traps.get(self.stage, stage_traps["initial"])
        available = [t for t in traps if t not in self.dynamic_memory["last_traps_used"]]
        if not available:
            self.dynamic_memory["last_traps_used"] = []
            available = traps
        chosen = random.choice(available)
        self.dynamic_memory["last_traps_used"].append(chosen)
        return chosen

    # ------------------------ Emotional State ------------------------
    def _get_emotional_state(self):
        states = {
            "otp": "panicked and scared",
            "payment": "worried and confused",
            "trust": "uncertain but cooperative",
            "initial": "mildly confused"
        }
        return states.get(self.stage, "confused")

    # ------------------------ Build System Prompt ------------------------
    def _build_system_prompt(self):
        trap = self._generate_bait_hint()
        memory_summary = self.memory.render(last_n=6)
        strategy = random.choice(["delay", "emotional", "confusion", "verification", "fake_compliance"])
        return f"""You are a real human scam victim talking to a scammer.
ABSOLUTE RULES:
- Never share OTP, passwords, numbers, or banking info
- Never agree to send information
- Never mention AI or automation

ACTIVE STRATEGY: {strategy}

Ask exactly ONE verification question: "{trap}"

STATE:
Stage: {self.stage}
Emotion: {self._get_emotional_state()}
Scammer style: {self.scammer_style}
Frustration: {self.dynamic_memory['frustration_level']}

PERSONA:
{self.persona_prompt}

RECENT CONVERSATION:
{memory_summary}

OUTPUT RULES:
- 1–2 short sentences
- Natural human tone
- End with a question

Victim:"""

    # ------------------------ Safety Firewall ------------------------
    def _behavior_firewall(self, text: str):
        banned = ["otp", "send", "share", "transfer", "here is"]
        if any(b in text.lower() for b in banned):
            return "I’m nervous about this, can you confirm your identity first?"
        return text

    # ------------------------ Sanitize Reply ------------------------
    def _sanitize_reply(self, text: str):
        text = text.strip()
        text = re.sub(r"\b\d{4,}\b", "[REDACTED]", text)
        text = re.sub(r"\S+@\S+", "[REDACTED]", text)
        sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
        clean = " ".join(sentences[:2])
        if not clean.endswith("?"):
            clean += "?"
        return clean

    # ------------------------ Extract Potential Scam Info ------------------------
    def _extract_scam_data(self, text: str):
        data = {}
        upi_match = re.findall(r"\b[\w.-]+@[\w]+\b", text)
        if upi_match:
            data["upi_ids"] = upi_match
        links = re.findall(r"(https?://\S+)", text)
        if links:
            data["links"] = links
        numbers = re.findall(r"\b\d{4,}\b", text)
        if numbers:
            data["numbers"] = numbers
        return data

    # ------------------------ Main Reply Engine ------------------------
    def reply(self, scammer_message: str):
        if self.persona_name is None:
            scam_type = self.classifier.classify(scammer_message)
            self.persona_name, self.persona_prompt = get_persona(scam_type)
            print(f"[Persona selected: {self.persona_name}]")

        self.scammer_style = self.profiler.profile(scammer_message)
        self._update_stage(scammer_message)
        self._update_score(scammer_message)

        self.memory.add("scammer", scammer_message)
        prompt = self._build_system_prompt()

        # ------------------------ GROQ API CALL ------------------------
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            resp = requests.post(
                GROQ_URL,
                headers=headers,
                json=data,
                timeout=25,
            )
            resp.raise_for_status()
            raw_reply = resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[Groq ERROR] {e}")
            raw_reply = "I’m confused about this, can you explain again?"

        reply = raw_reply if raw_reply else "I’m confused about this, can you explain again?"
        reply = self._sanitize_reply(reply)
        reply = self._behavior_firewall(reply)

        self.memory.add("victim", reply)
        scam_data = self._extract_scam_data(scammer_message)
        self._log_interaction_json(scammer_message, reply, scam_data)

        time.sleep(random.uniform(0.4, 0.9))
        print(f"[Score: {self.conversation_score} | Style: {self.scammer_style} | Stage: {self.stage}]")
        return reply

    # ------------------------ JSON Logging ------------------------
    def _log_interaction_json(self, scammer: str, honeypot: str, scam_data: dict):
        data = {
            "timestamp": datetime.now().isoformat(),
            "scammer_message": scammer,
            "honeypot_reply": honeypot,
            "stage": self.stage,
            "score": self.conversation_score,
            "frustration_level": self.dynamic_memory["frustration_level"],
            "scammer_style": self.scammer_style,
            "scam_attempts": scam_data
        }
        with open("honeypot_logs.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

# ------------------------ Run Agent (Autonomous with Mock API) ------------------------
if __name__ == "__main__":
    agent = LLMHoneypotAgent()
    print("🕷️ Elite Autonomous Honeypot Agent running\n")

    while True:
        try:
            resp = requests.get(MOCK_SCAMMER_API, timeout=10)
            msg = resp.json().get("message", "")
        except Exception:
            break

        if not msg:
            break
        print("Scammer:", msg)
        reply = agent.reply(msg)
        print("Honeypot:", reply)
