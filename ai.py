import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 🔑 Set your Groq API key in environment variable: GROQ_API_KEY
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Hello, are you working?"}],
    "temperature": 0.7
}

try:
    response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    print("✅ Groq API works! Response snippet:")
    print(data.get("choices", [{}])[0].get("message", {}).get("content", "No content"))
except requests.exceptions.HTTPError as e:
    print("❌ HTTP Error:", e)
    print(response.text)
except requests.exceptions.RequestException as e:
    print("❌ Request failed:", e)
