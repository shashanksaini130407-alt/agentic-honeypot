from flask import Flask, jsonify, request
import random
import pandas as pd
import os
from faker import Faker
import uuid

app = Flask(__name__)
fake = Faker()

# ----------------------------
# Load Dataset
# ----------------------------

BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "master_fraud_dataset.csv")

df = pd.read_csv(DATA_PATH)
scam_texts = df[df["label"] == 1]["text"].dropna().tolist()

print(f"✅ Loaded {len(scam_texts)} real scam samples")

# ----------------------------
# Personas
# ----------------------------

PERSONAS = {
    "bank_officer": {
        "tone": ["official", "urgent"],
        "openers": [
            "This is your bank security department",
            "We detected suspicious activity",
        ]
    },
    "tech_support": {
        "tone": ["technical", "helpful"],
        "openers": [
            "This is Microsoft technical support",
            "Your device is compromised",
        ]
    },
    "lottery_agent": {
        "tone": ["excited", "persuasive"],
        "openers": [
            "Congratulations you won a lottery",
            "You are selected for a prize reward",
        ]
    }
}

# ----------------------------
# Phishing URL Generator
# ----------------------------

def generate_phishing_url():
    brands = ["paypal", "amazon", "banksecure", "google", "microsoft"]
    brand = random.choice(brands)
    domain = f"{brand}-verify-{uuid.uuid4().hex[:6]}.com"
    return f"http://{domain}/login"

# ----------------------------
# Channel Simulator
# ----------------------------

CHANNELS = ["sms", "email", "twitter"]

def format_by_channel(message, channel):

    if channel == "sms":
        return f"[SMS ALERT] {message}"

    if channel == "email":
        return f"Subject: Urgent Notice\n\n{message}"

    if channel == "twitter":
        return f"@user ⚠️ {message}"

    return message

# ----------------------------
# Synthetic Scam Generator
# ----------------------------

def generate_synthetic_scam():

    templates = [
        "Your {brand} account is locked. Verify at {url}",
        "Unauthorized login detected. Confirm immediately: {url}",
        "Payment failed. Update details here: {url}",
    ]

    brand = random.choice(["Bank", "PayPal", "Amazon", "Google"])
    url = generate_phishing_url()

    template = random.choice(templates)

    return template.format(brand=brand, url=url)

# ----------------------------
# Reinforcement Escalation
# ----------------------------

conversation_state = {
    "persona": random.choice(list(PERSONAS.keys())),
    "pressure_level": 0
}

def escalate(user_reply):

    if any(w in user_reply.lower() for w in ["wait", "later"]):
        conversation_state["pressure_level"] += 1

    if conversation_state["pressure_level"] > 2:
        return "Failure to respond will result in account suspension"

    return None

# ----------------------------
# Message Generator
# ----------------------------

def generate_message(user_reply=""):

    escalation = escalate(user_reply)
    if escalation:
        return escalation

    persona = PERSONAS[conversation_state["persona"]]

    if random.random() < 0.5:
        message = random.choice(scam_texts)
    else:
        message = generate_synthetic_scam()

    opener = random.choice(persona["openers"])

    final_message = f"{opener}. {message}"

    channel = random.choice(CHANNELS)

    return format_by_channel(final_message, channel)

# ----------------------------
# Continuous Streaming Generator
# ----------------------------

def generate_stream(count=10):
    return [generate_message() for _ in range(count)]

# ----------------------------
# API Endpoints
# ----------------------------

@app.route("/mock_scammer", methods=["GET", "POST"])
def mock_scammer():

    user_reply = ""

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        user_reply = data.get("reply", "")

    message = generate_message(user_reply)

    return jsonify({"message": message})

@app.route("/generate_bulk", methods=["GET"])
def generate_bulk():

    count = int(request.args.get("count", 1000))

    bulk_messages = generate_stream(count)

    return jsonify({"messages": bulk_messages})

# ----------------------------
# Run Server
# ----------------------------

if __name__ == "__main__":
    print("🚨 Ultimate Mock Scammer Engine running:")
    print("👉 http://localhost:5000/mock_scammer")
    print("👉 http://localhost:5000/generate_bulk?count=10000")
    app.run(port=5000)
