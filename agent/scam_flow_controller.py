import requests
import json
from datetime import datetime
from .fraud_agent import FraudDetectionAgent
from .llm_honeypot_agent import LLMHoneypotAgent

MOCK_SCAMMER_API = "http://localhost:5000/mock_scammer"  # Same as in honeypot

class ScamFlowController:
    def __init__(self):
        self.fraud_agent = FraudDetectionAgent()
        self.honeypot_agent = LLMHoneypotAgent()
        print("🚦 Scam Flow Controller Initialized\n")

    def process_message(self, message: str):
        # ----------------------
        # Step 1: Fraud detection
        # ----------------------
        fraud_result = self.fraud_agent.analyze(message)
        print(f"[Fraud Check] Scam: {fraud_result['is_scam']} | Confidence: {fraud_result['confidence']}")

        if fraud_result["is_scam"]:
            # ----------------------
            # Step 2: Engage honeypot
            # ----------------------
            honeypot_reply_str = self.honeypot_agent.reply(message)  # Returns string

            # Wrap string reply in dict to match expected keys
            honeypot_result = {
                "reply": honeypot_reply_str,
                "scam_data": {},  # Optional: honeypot can extract scam data here if needed
                "stage": self.honeypot_agent.stage,
                "scammer_style": self.honeypot_agent.scammer_style,
                "conversation_score": self.honeypot_agent.conversation_score
            }

            # Combine everything into one JSON
            result_json = {
                "timestamp": datetime.now().isoformat(),
                "scammer_message": message,
                "fraud_result": fraud_result,
                "honeypot_reply": honeypot_result["reply"],
                "scam_data": honeypot_result["scam_data"],
                "stage": honeypot_result["stage"],
                "scammer_style": honeypot_result["scammer_style"],
                "conversation_score": honeypot_result["conversation_score"]
            }
        else:
            # Non-scam message
            result_json = {
                "timestamp": datetime.now().isoformat(),
                "scammer_message": message,
                "fraud_result": fraud_result,
                "honeypot_reply": None,
                "scam_data": {},
                "stage": None,
                "scammer_style": None,
                "conversation_score": 0
            }

        # Save to unified log file
        with open("scam_flow_logs.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(result_json) + "\n")

        return result_json

    # ------------------------
    # Autonomous loop fetching messages
    # ------------------------
    def run_autonomous(self):
        print("🤖 Starting autonomous scam monitoring...\n")
        while True:
            try:
                # Fetch a message from the mock scammer API
                resp = requests.get(MOCK_SCAMMER_API, timeout=10)
                msg = resp.json().get("message", "")
            except Exception:
                print("[!] Error fetching message. Retrying...")
                continue

            if not msg:
                # No more messages
                break

            print("Scammer:", msg)
            result = self.process_message(msg)
            print("Honeypot Reply:", result.get("honeypot_reply"))
            print("-" * 60)

# ------------------------
# Run controller
# ------------------------
if __name__ == "__main__":
    controller = ScamFlowController()
    controller.run_autonomous()
