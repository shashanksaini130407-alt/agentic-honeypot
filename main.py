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

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Card styling */
    .card-container {
        background: rgba(30, 58, 138, 0.3);
        border: 2px solid rgba(59, 130, 246, 0.5);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4);
    }
    
    /* Text area styling */
    textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #e0e7ff !important;
        border: 2px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Metric styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(99, 102, 241, 0.2));
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Embedded Mock Scammer Generator
class MockScammerGenerator:
    """Generates realistic scam messages"""
    
    scam_templates = {
        "bank": [
            "🏦 Hello, this is your bank. Suspicious activity detected on your account. Please confirm your OTP immediately.",
            "🚨 Your bank account will be locked in 24 hours unless you verify your details here: {url}",
            "⚠️ Alert: Unauthorized payment attempt. Click to confirm: {url}",
            "🔐 This is XYZ Bank security. Your account needs verification. Reply with your account number.",
        ],
        "payment": [
            "💳 Payment failed! Update your UPI/card details urgently: {url}",
            "🔒 Your Amazon Pay wallet is locked. Verify here: {url}",
            "❌ Transaction declined. Please update payment info immediately.",
            "📱 Google Pay: Your account has suspicious activity. Confirm your PIN: {url}",
        ],
        "tech_support": [
            "🦠 Your device has a virus! Click here to fix: {url}",
            "🛡️ Microsoft Support: Critical system error detected. Download fix: {url}",
            "📱 Apple Security Alert: Your iPhone has 47 viruses! Clean now: {url}",
            "💻 Windows Defender: Malware detected! Scan now: {url}",
        ],
        "prize": [
            "🎉 Congratulations! You won $5000! Claim here: {url}",
            "🏆 You've been selected for Amazon prize draw! Verify: {url}",
            "🎁 WINNER! Free iPhone 15 for you! Click: {url}",
            "💰 You qualify for a government grant! Apply now: {url}",
        ],
        "investment": [
            "📈 Make $10,000/month with crypto! Join now: {url}",
            "💹 Stock tips: Guaranteed 100% returns! Subscribe: {url}",
            "📊 Binary options: Easy money! Register: {url}",
            "💵 Forex trading: Turn $100 into $1000! Learn: {url}",
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

# Page configuration
st.set_page_config(
    page_title="🕷️ Agentic Honeypot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Section
st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <h1 style="font-size: 3em; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🕷️ Agentic Honeypot
        </h1>
        <p style="color: #c7d2fe; font-size: 1.2em; margin: 10px 0;">
            AI-Powered Scam Detection & Engagement System
        </p>
        <p style="color: #a5b4fc; font-size: 0.95em;">
            🤖 Detects • 🎯 Engages • 📊 Analyzes
        </p>
    </div>
""", unsafe_allow_html=True)

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
    st.markdown("### ⚙️ System Info")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len(st.session_state.conversation_history))
    with col2:
        st.metric("Status", "🟢 Active")
    
    st.divider()
    
    st.markdown("### 📋 Features")
    st.write("""
    ✅ Real-time fraud detection
    ✅ AI-powered responses
    ✅ Message generation
    ✅ Conversation tracking
    ✅ Analytics dashboard
    """)
    
    st.divider()
    
    st.markdown("### 🔧 Configuration")
    st.write("**Model:** Groq Llama 3.1 8B")
    st.write("**Framework:** Streamlit")
    st.write("**Status:** Fully Functional ✨")
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()

# Main content tabs with better styling
tab1, tab2, tab3 = st.tabs(["🔄 Mock Scammer API", "✍️ Manual Analysis", "📈 Analytics"])

# Tab 1: Mock Scammer API
with tab1:
    st.markdown("### 📨 Mock Scammer Message Generator")
    st.write("Click the button below to generate and analyze realistic scam messages in real-time.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Generate & Analyze Message", key="mock_fetch", use_container_width=True):
            # Generate message
            scammer_msg = MockScammerGenerator.generate()
            st.session_state.conversation_history.append(scammer_msg)
            
            # Display scammer message
            st.markdown("#### 📧 Incoming Message")
            st.markdown(f"""
            <div class="card-container">
                <code style="color: #fca5a5; font-size: 0.95em;">{scammer_msg}</code>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("🔍 Analyzing..."):
                # Fraud detection
                fraud_result = st.session_state.fraud_agent.analyze(scammer_msg)
                
                # Display results
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if fraud_result["is_scam"]:
                        st.error("⚠️ SCAM DETECTED")
                    else:
                        st.success("✅ LEGITIMATE")
                
                with col_b:
                    confidence = fraud_result['confidence']
                    color = "🔴" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🟢"
                    st.metric("Confidence", f"{color} {confidence:.1%}")
                
                with col_c:
                    st.metric("Decision", fraud_result['decision'][:10])
                
                st.divider()
                
                # Honeypot reply
                if fraud_result["is_scam"]:
                    honeypot_reply = st.session_state.honeypot_agent.reply(scammer_msg)
                    st.markdown("#### 🤖 Honeypot Response")
                    st.markdown(f"""
                    <div class="card-container">
                        <p style="color: #86efac; font-size: 1.05em;"><i>"{honeypot_reply}"</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Full details
                with st.expander("📊 Detailed Analysis"):
                    st.json(fraud_result)
    
    with col2:
        st.markdown("### 📂 Categories")
        st.write("""
        - 🏦 Banking
        - 💳 Payment
        - 🛡️ Tech Support
        - 🎁 Prize/Lottery
        - 📈 Investment
        """)

# Tab 2: Manual Analysis
with tab2:
    st.markdown("### ✍️ Manual Message Analysis")
    st.write("Paste or type a scammer message to analyze it:")
    
    user_message = st.text_area(
        "Enter message:",
        placeholder="Paste a suspicious message here...",
        height=120,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Analyze Message", key="manual_analyze", use_container_width=True):
            if user_message.strip():
                st.session_state.conversation_history.append(user_message)
                
                with st.spinner("Processing..."):
                    fraud_result = st.session_state.fraud_agent.analyze(user_message)
                    
                    # Results display
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if fraud_result["is_scam"]:
                            st.error("⚠️ SCAM DETECTED")
                        else:
                            st.success("✅ LEGITIMATE")
                    
                    with col2:
                        confidence = fraud_result['confidence']
                        color = "🔴" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🟢"
                        st.metric("Confidence", f"{color} {confidence:.1%}")
                    
                    with col3:
                        st.metric("Stage", fraud_result.get('stage', 'N/A'))
                    
                    st.divider()
                    
                    # Honeypot response
                    if fraud_result["is_scam"]:
                        honeypot_reply = st.session_state.honeypot_agent.reply(user_message)
                        st.markdown("#### 🤖 Honeypot Response")
                        st.markdown(f"""
                        <div class="card-container">
                            <p style="color: #86efac;"><i>"{honeypot_reply}"</i></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Details
                    with st.expander("📋 Full Analysis Details"):
                        st.json(fraud_result)
            else:
                st.warning("⚠️ Please enter a message first!")
    
    with col2:
        st.markdown("### 💡 Tips")
        st.info("""
        **Common Scam Indicators:**
        - Urgent language
        - Requests for OTP/passwords
        - Suspicious links
        - Impersonation
        - Time pressure
        """)

# Tab 3: Analytics
with tab3:
    st.markdown("### 📊 Conversation Analytics")
    
    if st.session_state.conversation_history:
        # Statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4 style="margin: 0; color: #60a5fa;">Total Messages</h4>
                <p style="font-size: 2.5em; margin: 10px 0; color: #fff;">""" + 
                str(len(st.session_state.conversation_history)) + 
                """</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_length = sum(len(msg) for msg in st.session_state.conversation_history) // len(st.session_state.conversation_history)
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0; color: #60a5fa;">Avg Message Length</h4>
                <p style="font-size: 2.5em; margin: 10px 0; color: #fff;">{avg_length} chars</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0; color: #60a5fa;">Session Status</h4>
                <p style="font-size: 2.5em; margin: 10px 0; color: #10b981;">🟢 Active</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Message history
        st.markdown("### 📝 Message History")
        
        for i, msg in enumerate(st.session_state.conversation_history[-10:], 1):
            with st.expander(f"📌 Message {i}: {msg[:50]}...", expanded=False):
                st.write(msg)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 50px 20px;">
            <h3 style="color: #94a3b8;">📭 No Messages Yet</h3>
            <p style="color: #64748b;">Start analyzing messages using the tabs above!</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; padding: 20px; color: #64748b;">
        <p>🕷️ <b>Agentic Honeypot</b> • Powered by Groq AI • v1.0</p>
        <p style="font-size: 0.85em;">🔒 Secure • 🚀 Fast • 🎯 Accurate</p>
    </div>
""", unsafe_allow_html=True)
