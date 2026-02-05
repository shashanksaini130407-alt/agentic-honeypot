import streamlit as st
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Check if API key is set
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ Missing GROQ_API_KEY environment variable!")
    st.info("Please set GROQ_API_KEY in your environment or .env file")
    st.stop()

# Import your existing agents
from agent.fraud_agent import FraudDetectionAgent
from agent.llm_honeypot_agent import LLMHoneypotAgent

# Embedded Mock Scammer Generator
class MockScammerGenerator:
    """Generates realistic scam messages"""
    
    scam_templates = {
        "bank": [
            "Hello, this is your bank. Suspicious activity detected on your account. Please confirm your OTP immediately.",
            "Your bank account will be locked in 24 hours unless you verify your details here: {url}",
            "Alert: Unauthorized payment attempt. Click to confirm: {url}",
            "This is XYZ Bank security. Your account needs verification. Reply with your account number.",
        ],
        "payment": [
            "Payment failed! Update your UPI/card details urgently: {url}",
            "Your Amazon Pay wallet is locked. Verify here: {url}",
            "Transaction declined. Please update payment info immediately.",
            "Google Pay: Your account has suspicious activity. Confirm your PIN: {url}",
        ],
        "tech_support": [
            "Your device has a virus! Click here to fix: {url}",
            "Microsoft Support: Critical system error detected. Download fix: {url}",
            "Apple Security Alert: Your iPhone has 47 viruses! Clean now: {url}",
            "Windows Defender: Malware detected! Scan now: {url}",
        ],
        "prize": [
            "Congratulations! You won $5000! Claim here: {url}",
            "You've been selected for Amazon prize draw! Verify: {url}",
            "WINNER! Free iPhone 15 for you! Click: {url}",
            "You qualify for a government grant! Apply now: {url}",
        ],
        "investment": [
            "Make $10,000/month with crypto! Join now: {url}",
            "Stock tips: Guaranteed 100% returns! Subscribe: {url}",
            "Binary options: Easy money! Register: {url}",
            "Forex trading: Turn $100 into $1000! Learn: {url}",
        ],
    }
    
    urls = [
        "http://secure-verify-123.com/login",
        "http://bank-confirm-456.com",
        "http://update-details-789.com",
        "http://verify-account-000.com",
    ]
    
    @staticmethod
    def generate():
        """Generate a random scam message"""
        category = random.choice(list(MockScammerGenerator.scam_templates.keys()))
        template = random.choice(MockScammerGenerator.scam_templates[category])
        url = random.choice(MockScammerGenerator.urls)
        return template.format(url=url)

# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="Agentic Honeypot Dashboard", layout="wide")
st.title("🚦 Agentic Honeypot - Scam Flow Controller")
st.markdown("AI-powered honeypot that detects and engages with scammers")

# Initialize agents and session state
if "controller_initialized" not in st.session_state:
    st.session_state.fraud_agent = FraudDetectionAgent()
    st.session_state.honeypot_agent = LLMHoneypotAgent()
    st.session_state.conversation_history = []
    st.session_state.controller_initialized = True

# Ensure conversation_history exists
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("Honeypot features:")
    st.write("- 🔍 Fraud detection")
    st.write("- 🤖 AI-powered responses")
    st.write("- 📊 Conversation analytics")
    st.divider()
    st.write("**Model:** Groq llama-3.1-8b-instant")

# Main tabs
tab1, tab2, tab3 = st.tabs(["📨 Mock Scammer API", "📝 Manual Input", "📊 Analytics"])

# Tab 1: Mock Scammer API
with tab1:
    st.subheader("Mock Scammer - Auto-Generated Messages")
    st.write("Click below to fetch a randomly generated scam message:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Fetch New Message from Mock Scammer", key="mock_fetch"):
            # Generate message
            scammer_msg = MockScammerGenerator.generate()
            st.session_state.conversation_history.append(scammer_msg)
            
            st.write("### 📧 Scammer Message:")
            st.code(scammer_msg)
            
            with st.spinner("Analyzing..."):
                # Fraud detection
                fraud_result = st.session_state.fraud_agent.analyze(scammer_msg)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if fraud_result["is_scam"]:
                        st.error("⚠️ SCAM DETECTED")
                    else:
                        st.success("✅ NOT A SCAM")
                
                with col_b:
                    st.metric("Confidence", f"{fraud_result['confidence']:.1%}")
                
                st.info(f"**Decision:** {fraud_result['decision']}")
                
                # Honeypot reply
                if fraud_result["is_scam"]:
                    honeypot_reply = st.session_state.honeypot_agent.reply(scammer_msg)
                    st.write("### 🤖 Honeypot Response:")
                    st.markdown(f"> *{honeypot_reply}*")
    
    with col2:
        st.write("### Message Categories:")
        st.write("""
        - **Bank:** Account verification, alerts
        - **Payment:** UPI, card updates
        - **Tech Support:** Virus/malware warnings
        - **Prize:** Fake winnings
        - **Investment:** Get-rich-quick schemes
        """)

# Tab 2: Manual Input
with tab2:
    st.subheader("Manual Message Input")
    user_message = st.text_area("Enter a scammer message:")
    
    if st.button("📤 Process Manual Message"):
        if user_message.strip():
            st.session_state.conversation_history.append(user_message)
            
            with st.spinner("Analyzing..."):
                fraud_result = st.session_state.fraud_agent.analyze(user_message)
                
                col1, col2 = st.columns(2)
                with col1:
                    if fraud_result["is_scam"]:
                        st.error("⚠️ SCAM DETECTED")
                    else:
                        st.success("✅ NOT A SCAM")
                
                with col2:
                    st.metric("Confidence", f"{fraud_result['confidence']:.1%}")
                
                st.info(f"**Decision:** {fraud_result['decision']}")
                st.json(fraud_result)
                
                if fraud_result["is_scam"]:
                    honeypot_reply = st.session_state.honeypot_agent.reply(user_message)
                    st.write("### 🤖 Response:")
                    st.markdown(f"> {honeypot_reply}")
        else:
            st.warning("Please enter a message!")

# Tab 3: Analytics
with tab3:
    st.subheader("📊 Conversation Analytics")
    
    if st.session_state.conversation_history:
        st.write(f"**Total messages processed:** {len(st.session_state.conversation_history)}")
        
        st.write("### Recent Messages:")
        for i, msg in enumerate(st.session_state.conversation_history[-10:], 1):
            with st.expander(f"Message {i}: {msg[:60]}..."):
                st.write(msg)
    else:
        st.info("No messages processed yet. Start with the Mock Scammer or Manual Input!")
