from agent.fraud_agent import FraudDetectionAgent

agent = FraudDetectionAgent()

tests = [
    "Congratulations! You won a lottery. Send your UPI ID to claim.",
    "Hey bro, are we meeting tomorrow?",
    "Your bank account is blocked. Click this link to verify."
]

for msg in tests:
    result = agent.analyze(msg)
    print("\nResult:")
    for k, v in result.items():
        print(f"{k}: {v}")
