import streamlit as st
from datetime import datetime
import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your existing agents
from agent.fraud_agent import FraudDetectionAgent
from agent.llm_honeypot_agent import LLMHoneypotAgent

MOCK_SCAMMER_API = "http://localhost:5000/mock_scammer"

# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="Agentic Honeypot Dashboard", layout="wide")
st.title("🚦 Agentic Honeypot - Scam Flow Controller")

# Initialize agents (cached for session)
if "controller_initialized" not in st.session_state:
    st.session_state.fraud_agent = FraudDetectionAgent()
    st.session_state.honeypot_agent = LLMHoneypotAgent()
    st.session_state.controller_initialized = True
    st.success("✅ Scam Flow Controller Initialized!")

# ------------------------
# Manual message test
# ------------------------
st.subheader("Send a Test Message to the Controller")
message_input = st.text_area("Enter scammer message here:")

if st.button("Process Message"):
    fraud_result = st.session_state.fraud_agent.analyze(message_input)
    st.write("**Fraud Check:**", fraud_result)

    if fraud_result["is_scam"]:
        reply = st.session_state.honeypot_agent.reply(message_input)
        st.write("**Honeypot Reply:**", reply)
    else:
        st.write("This message is not a scam.")

# ------------------------
# Autonomous fetch from Mock Scammer API
# ------------------------
st.subheader("Autonomous Scam Monitoring")
if st.button("Fetch Message from Mock API"):
    try:
        resp = requests.get(MOCK_SCAMMER_API, timeout=10)
        msg = resp.json().get("message", "")
        if msg:
            st.write("**Scammer Message:**", msg)
            fraud_result = st.session_state.fraud_agent.analyze(msg)
            st.write("**Fraud Result:**", fraud_result)
            if fraud_result["is_scam"]:
                reply = st.session_state.honeypot_agent.reply(msg)
                st.write("**Honeypot Reply:**", reply)
        else:
            st.info("No more messages from mock API.")
    except Exception as e:
        st.error(f"Error fetching message: {e}")

# ------------------------
# Optionally, log messages
# ------------------------
st.subheader("Scam Logs")
if st.button("Show Last 5 Logs"):
    try:
        with open("scam_flow_logs.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-5:]:
                st.json(json.loads(line))
    except FileNotFoundError:
        st.info("No logs yet.")
