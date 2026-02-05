import joblib
import os
import numpy as np

BASE_DIR = os.getcwd()
MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")


class FraudDetectionAgent:
    def __init__(self):
        # Load trained model and vectorizer
        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        print("🤖 Fraud Detection Agent initialized")

        # High-risk scam keywords for boosting
        self.high_risk_keywords = [
            "otp", "transfer", "upi", "bank", "account", "payment",
            "lottery", "reward", "verify", "blocked", "processing fee"
        ]

    def analyze(self, message: str):
        """
        Analyze a message for scam likelihood.
        Uses ML model probability and keyword-based boosting.
        Confidence is capped at 0.95 for realism.
        """
        # Transform message
        vector = self.vectorizer.transform([message])

        # Base ML prediction and probability
        prediction = self.model.predict(vector)[0]  # 0 or 1
        probability = self.model.predict_proba(vector)[0][1]  # probability of scam

        # Count high-risk keywords in message
        matches = sum(k in message.lower() for k in self.high_risk_keywords)

        # ----- Keyword-based boosting -----
        if matches > 0:
            # Each keyword boosts probability by 0.1
            # Max probability capped at 0.95
            boost = 0.1 * matches
            probability = min(probability + boost, 0.95)

            # If 2 or more keywords, ensure prediction = scam
            if matches >= 2:
                prediction = 1

        # Build result dictionary
        result = {
            "message": message,
            "is_scam": bool(prediction),
            "confidence": round(float(probability), 3),
            "decision": "ENGAGE_SCAMMER" if prediction == 1 else "IGNORE"
        }

        return result
