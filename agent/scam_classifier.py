import re


class ScamClassifier:
    def classify(self, message: str) -> str:
        msg = message.lower()

        patterns = {
            "bank_scam": [
                "bank", "kyc", "account", "upi", "blocked", "verify"
            ],
            "prize_scam": [
                "won", "prize", "lottery", "reward", "gift"
            ],
            "job_scam": [
                "job", "hiring", "salary", "interview"
            ],
            "tech_support": [
                "virus", "support", "technical", "computer"
            ],
            "investment_scam": [
                "investment", "crypto", "profit", "trading"
            ],
            "otp_scam": [
                "otp", "code", "verification"
            ],
        }

        for scam_type, keywords in patterns.items():
            if any(word in msg for word in keywords):
                return scam_type

        return "unknown"
