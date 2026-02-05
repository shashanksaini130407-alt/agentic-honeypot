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

# Advanced Custom CSS for Premium Graphics
st.markdown("""
<style>
    /* Base styling */
    body, html, .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1a1a3e 100%);
        border-right: 2px solid rgba(96, 165, 250, 0.2);
    }
    
    /* Main headers */
    h1, h2, h3 {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(90deg, rgba(30, 58, 138, 0.4), rgba(55, 48, 163, 0.4));
        border-bottom: 2px solid rgba(96, 165, 250, 0.3);
        border-radius: 12px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: #fff;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.95em;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }
    
    /* Input boxes */
    textarea, input {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #e0e7ff !important;
        border: 2px solid rgba(96, 165, 250, 0.3) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 1em !important;
        transition: all 0.3s ease !important;
    }
    
    textarea:focus, input:focus {
        border-color: rgba(96, 165, 250, 0.8) !important;
        box-shadow: 0 0 20px rgba(96, 165, 250, 0.3) !important;
    }
    
    /* Premium Cards */
    .premium-card {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(55, 48, 163, 0.4));
        border: 2px solid rgba(96, 165, 250, 0.4);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
        transition: all 0.3s ease;
    }
    
    .premium-card:hover {
        border-color: rgba(96, 165, 250, 0.8);
        box-shadow: 0 12px 48px rgba(59, 130, 246, 0.25);
        transform: translateY(-4px);
    }
    
    /* Scam message card */
    .scam-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
        border: 2px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
    
    /* Honeypot response card */
    .honeypot-card {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(22, 163, 74, 0.1));
        border: 2px solid rgba(34, 197, 94, 0.4);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
    
    /* Confidence meter */
    .confidence-meter {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        border-radius: 10px;
        overflow: hidden;
        height: 8px;
        margin: 10px 0;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #ec4899 0%, #f97316 50%, #22c55e 100%);
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Metric cards */
    .metric-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
        border: 2px solid rgba(96, 165, 250, 0.4);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(96, 165, 250, 0.3);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.9em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Conversation item */
    .conversation-item {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.3), rgba(55, 48, 163, 0.3));
        border-left: 4px solid #60a5fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .conversation-item:hover {
        border-left-color: #a78bfa;
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.5), rgba(55, 48, 163, 0.5));
    }
    
    /* Divider */
    .divider-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.5), transparent);
        margin: 25px 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
        border-radius: 8px;
        padding: 12px !important;
    }
    
    /* Text styling */
    p, span {
        color: #e2e8f0;
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
        return template.format(url=url), category

# Page configuration
st.set_page_config(
    page_title="🕷️ Agentic Honeypot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Section with Premium Graphics
st.markdown("""
    <div style="text-align: center; padding: 40px 20px; margin: -20px -20px 0 -20px; 
                background: linear-gradient(135deg, #1e3a8a 0%, #312e81 50%, #1e3a8a 100%);
                border-bottom: 3px solid rgba(96, 165, 250, 0.5);">
        <h1 style="font-size: 3.5em; margin: 0; text-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);">
            🕷️ AGENTIC HONEYPOT
        </h1>
        <p style="color: #c7d2fe; font-size: 1.3em; margin: 15px 0 5px 0; font-weight: 600;">
            Advanced Scam Detection & Engagement System
        </p>
        <p style="color: #a5b4fc; font-size: 1em; margin: 0;">
            🤖 AI-Powered • 🎯 Real-time Detection • 📊 Analytics
        </p>
    </div>
""", unsafe_allow_html=True)

# Initialize agents and session state
if "controller_initialized" not in st.session_state:
    st.session_state.fraud_agent = FraudDetectionAgent()
    st.session_state.honeypot_agent = LLMHoneypotAgent()
    st.session_state.conversation_history = []
    st.session_state.analysis_results = []
    st.session_state.controller_initialized = True

# Ensure conversation_history exists
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []

# Sidebar with Premium Design
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1)); 
                border-radius: 12px; padding: 20px; margin-bottom: 20px; 
                border: 2px solid rgba(96, 165, 250, 0.3);">
        <h3 style="color: #60a5fa; margin-top: 0;">🎛️ CONTROL PANEL</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Total Messages</div>
            <div class="metric-value">{len(st.session_state.conversation_history)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Scams Detected</div>
            <div class="metric-value">{len([r for r in st.session_state.analysis_results if r.get('is_scam')])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="color: #cbd5e1;">
        <p style="font-weight: 600; color: #60a5fa; margin-bottom: 10px;">✨ FEATURES</p>
        <ul style="margin: 0; padding-left: 20px;">
            <li>Real-time Detection</li>
            <li>AI Responses</li>
            <li>Message Analytics</li>
            <li>Confidence Scoring</li>
            <li>History Tracking</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="color: #cbd5e1;">
        <p style="font-weight: 600; color: #a78bfa; margin-bottom: 5px;">⚙️ CONFIGURATION</p>
        <p style="font-size: 0.9em; margin: 5px 0;">Model: Groq Llama 3.1</p>
        <p style="font-size: 0.9em; margin: 5px 0;">Framework: Streamlit</p>
        <p style="font-size: 0.9em; margin: 5px 0; color: #22c55e;">Status: 🟢 Active</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.analysis_results = []
        st.rerun()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Auto Generate", "✍️ Manual Input", "💬 Conversations", "📈 Analytics"])

# Tab 1: Mock Scammer API with Confidence Score
with tab1:
    st.markdown("### 📨 AUTO-GENERATED SCAM MESSAGES")
    
    col_main, col_sidebar = st.columns([2, 1])
    
    with col_sidebar:
        st.markdown("### 📂 CATEGORIES")
        st.markdown("""
        🏦 **BANKING**
        - Account alerts
        - OTP requests
        
        💳 **PAYMENT**
        - Card updates
        - UPI scams
        
        🛡️ **TECH**
        - Virus alerts
        - Updates
        
        🎁 **PRIZE**
        - Fake wins
        - Lottery
        
        📈 **INVEST**
        - Crypto scams
        - Options
        """)
    
    with col_main:
    
    with col_main:
        st.write("Click to generate and analyze realistic scam messages:")
        
        if st.button("🔄 GENERATE & ANALYZE", key="mock_fetch", use_container_width=True):
            # Generate message
            scammer_msg, category = MockScammerGenerator.generate()
            st.session_state.conversation_history.append(scammer_msg)
            
            # Display scammer message
            st.markdown("""
            <div class="scam-card">
                <p style="font-weight: 600; color: #ef4444; margin: 0 0 10px 0; font-size: 0.95em;">📧 INCOMING MESSAGE</p>
                <p style="color: #fca5a5; font-family: monospace; font-size: 1em; margin: 0; line-height: 1.6;">""" + 
                scammer_msg + 
                """</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("🔍 Analyzing with AI..."):
                # Fraud detection
                fraud_result = st.session_state.fraud_agent.analyze(scammer_msg)
                st.session_state.analysis_results.append(fraud_result)
                
                # Display results in premium boxes
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if fraud_result["is_scam"]:
                        st.markdown("""
                        <div class="metric-box" style="border-color: rgba(239, 68, 68, 0.6);">
                            <p style="margin: 0; font-size: 2em;">🚨</p>
                            <p style="margin: 10px 0 0 0; font-weight: 700; color: #ef4444;">SCAM DETECTED</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="metric-box" style="border-color: rgba(34, 197, 94, 0.6);">
                            <p style="margin: 0; font-size: 2em;">✅</p>
                            <p style="margin: 10px 0 0 0; font-weight: 700; color: #22c55e;">LEGITIMATE</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_b:
                    confidence = fraud_result['confidence']
                    confidence_percent = confidence * 100
                    color = "#ef4444" if confidence > 0.7 else "#f97316" if confidence > 0.5 else "#22c55e"
                    st.markdown(f"""
                    <div class="metric-box">
                        <p class="metric-label">CONFIDENCE SCORE</p>
                        <p class="metric-value" style="color: {color};">{confidence_percent:.1f}%</p>
                        <div class="confidence-meter">
                            <div class="confidence-fill" style="width: {confidence_percent}%"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_c:
                    st.markdown(f"""
                    <div class="metric-box">
                        <p class="metric-label">CATEGORY</p>
                        <p style="font-size: 1.8em; margin: 15px 0; color: #a78bfa;">{category.upper()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)
                
                # Honeypot reply
                if fraud_result["is_scam"]:
                    honeypot_reply = st.session_state.honeypot_agent.reply(scammer_msg)
                    st.markdown("""
                    <div class="honeypot-card">
                        <p style="font-weight: 600; color: #22c55e; margin: 0 0 10px 0; font-size: 0.95em;">🤖 HONEYPOT RESPONSE</p>
                        <p style="color: #86efac; font-style: italic; font-size: 1em; margin: 0; line-height: 1.6;">""" + 
                        honeypot_reply + 
                        """</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed analysis
                with st.expander("📊 DETAILED ANALYSIS"):
                    col_d, col_e = st.columns(2)
                    with col_d:
                        st.write("**Detection Results:**")
                        st.json({
                            "is_scam": fraud_result["is_scam"],
                            "confidence": f"{fraud_result['confidence']:.2%}",
                            "decision": fraud_result.get("decision", "N/A"),
                            "category": category
                        })
                    with col_e:
                        st.write("**Message Info:**")
                        st.write(f"Length: {len(scammer_msg)} characters")
                        st.write(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    
    with col_sidebar:
        pass

# Tab 2: Manual Input
with tab2:
    st.markdown("### ✍️ MANUAL MESSAGE ANALYSIS")
    st.write("Paste or type any message to analyze:")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 💡 TIPS")
        st.info("""
        **Common Scam Indicators:**
        - Urgent language
        - Requests for OTP/passwords
        - Suspicious links
        - Impersonation
        - Time pressure
        """)
    
    with col1:
        user_message = st.text_area(
            "Message input:",
            placeholder="Enter a message to analyze...",
            height=140,
            label_visibility="collapsed"
        )
        
        if st.button("🔍 ANALYZE MESSAGE", use_container_width=True):
            if user_message.strip():
                st.session_state.conversation_history.append(user_message)
                
                with st.spinner("Processing analysis..."):
                    fraud_result = st.session_state.fraud_agent.analyze(user_message)
                    st.session_state.analysis_results.append(fraud_result)
                    
                    # Results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if fraud_result["is_scam"]:
                            st.markdown("""
                            <div class="metric-box" style="border-color: rgba(239, 68, 68, 0.6);">
                                <p style="margin: 0; font-size: 2em;">🚨</p>
                                <p style="margin: 10px 0 0 0; font-weight: 700; color: #ef4444;">SCAM</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="metric-box" style="border-color: rgba(34, 197, 94, 0.6);">
                                <p style="margin: 0; font-size: 2em;">✅</p>
                                <p style="margin: 10px 0 0 0; font-weight: 700; color: #22c55e;">SAFE</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        confidence = fraud_result['confidence']
                        confidence_percent = confidence * 100
                        color = "#ef4444" if confidence > 0.7 else "#f97316" if confidence > 0.5 else "#22c55e"
                        st.markdown(f"""
                        <div class="metric-box">
                            <p class="metric-label">CONFIDENCE</p>
                            <p class="metric-value" style="color: {color};">{confidence_percent:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-box">
                            <p class="metric-label">STAGE</p>
                            <p style="font-size: 1.8em; margin: 15px 0; color: #a78bfa;">{fraud_result.get('stage', 'N/A').upper()[:8]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)
                    
                    if fraud_result["is_scam"]:
                        honeypot_reply = st.session_state.honeypot_agent.reply(user_message)
                        st.markdown(f"""
                        <div class="honeypot-card">
                            <p style="font-weight: 600; color: #22c55e; margin: 0 0 10px 0;">🤖 AI RESPONSE</p>
                            <p style="color: #86efac; font-style: italic; margin: 0;">"{honeypot_reply}"</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with st.expander("📋 Full Results"):
                        st.json(fraud_result)
            else:
                st.warning("⚠️ Please enter a message first!")
        else:
            st.warning("⚠️ Please enter a message first!")

# Tab 3: Conversations History
with tab3:
    st.markdown("### 💬 CONVERSATION HISTORY")
    st.write(f"Total: {len(st.session_state.conversation_history)} messages | Scams: {len([r for r in st.session_state.analysis_results if r.get('is_scam')])}")
    
    if st.session_state.conversation_history:
        for i, (msg, result) in enumerate(zip(st.session_state.conversation_history, st.session_state.analysis_results), 1):
            is_scam = result.get("is_scam", False)
            confidence = result.get("confidence", 0)
            
            badge_color = "🔴" if is_scam else "🟢"
            badge_text = "SCAM" if is_scam else "SAFE"
            
            st.markdown(f"""
            <div class="conversation-item">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: 700; color: #60a5fa;">Message #{i}</span>
                    <span style="font-size: 0.9em; color: #a0aec0;">Confidence: {confidence:.1%}</span>
                </div>
                <p style="margin: 8px 0; color: #e2e8f0; font-size: 0.95em;">{msg[:120]}...</p>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <span style="background: linear-gradient(135deg, #ef4444, #dc2626) if {is_scam} else linear-gradient(135deg, #22c55e, #16a34a); 
                                 padding: 4px 12px; border-radius: 20px; color: white; font-size: 0.85em; font-weight: 600;">
                        {badge_color} {badge_text}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <p style="font-size: 2em; color: #94a3b8; margin: 0;">📭</p>
            <p style="color: #94a3b8; font-size: 1.1em; margin: 10px 0;">No conversations yet</p>
            <p style="color: #64748b; font-size: 0.95em;">Start analyzing messages to see them here!</p>
        </div>
        """, unsafe_allow_html=True)

# Tab 4: Analytics Dashboard
with tab4:
    st.markdown("### 📈 ADVANCED ANALYTICS")
    
    if st.session_state.conversation_history:
        # Stats
        total_msgs = len(st.session_state.conversation_history)
        scam_count = len([r for r in st.session_state.analysis_results if r.get('is_scam')])
        safe_count = total_msgs - scam_count
        avg_confidence = sum([r.get('confidence', 0) for r in st.session_state.analysis_results]) / len(st.session_state.analysis_results) if st.session_state.analysis_results else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">Total Messages</p>
                <p class="metric-value">{total_msgs}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box" style="border-color: rgba(239, 68, 68, 0.6);">
                <p class="metric-label">Scams Found</p>
                <p class="metric-value" style="color: #ef4444;">{scam_count}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box" style="border-color: rgba(34, 197, 94, 0.6);">
                <p class="metric-label">Safe Messages</p>
                <p class="metric-value" style="color: #22c55e;">{safe_count}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">Avg Confidence</p>
                <p class="metric-value" style="color: #a78bfa;">{avg_confidence:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)
        
        # Detailed breakdown
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.write("**Detection Breakdown:**")
            st.markdown(f"""
            <div class="premium-card">
                <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                    <span style="color: #e2e8f0;">🔴 Scams Detected</span>
                    <span style="color: #ef4444; font-weight: 700; font-size: 1.2em;">{scam_count}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: rgba(34, 197, 94, 0.1); border-radius: 8px;">
                    <span style="color: #e2e8f0;">🟢 Legitimate</span>
                    <span style="color: #22c55e; font-weight: 700; font-size: 1.2em;">{safe_count}</span>
                </div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(96, 165, 250, 0.2);">
                    <p style="color: #a0aec0; font-size: 0.9em; margin: 0;">Detection Rate: <span style="color: #60a5fa; font-weight: 700;">{(scam_count/total_msgs*100):.1f}%</span></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_right:
            st.write("**Confidence Metrics:**")
            high_conf = len([r for r in st.session_state.analysis_results if r.get('confidence', 0) > 0.8])
            med_conf = len([r for r in st.session_state.analysis_results if 0.5 <= r.get('confidence', 0) <= 0.8])
            low_conf = len([r for r in st.session_state.analysis_results if r.get('confidence', 0) < 0.5])
            
            st.markdown(f"""
            <div class="premium-card">
                <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                    <span style="color: #e2e8f0;">🔴 High (>80%)</span>
                    <span style="color: #ef4444; font-weight: 700; font-size: 1.2em;">{high_conf}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: rgba(249, 115, 22, 0.1); border-radius: 8px;">
                    <span style="color: #e2e8f0;">🟡 Medium (50-80%)</span>
                    <span style="color: #f97316; font-weight: 700; font-size: 1.2em;">{med_conf}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: rgba(34, 197, 94, 0.1); border-radius: 8px;">
                    <span style="color: #e2e8f0;">🟢 Low (<50%)</span>
                    <span style="color: #22c55e; font-weight: 700; font-size: 1.2em;">{low_conf}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 80px 20px;">
            <p style="font-size: 2.5em; color: #94a3b8; margin: 0;">📊</p>
            <p style="color: #94a3b8; font-size: 1.2em; margin: 15px 0;">Analytics Coming Soon</p>
            <p style="color: #64748b;">Generate or analyze messages to see analytics</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; padding: 30px 20px; margin-top: 40px; 
                border-top: 2px solid rgba(96, 165, 250, 0.2);">
        <p style="color: #64748b; margin: 0; font-weight: 600;">
            🕷️ <span style="color: #60a5fa;">AGENTIC HONEYPOT</span> v1.0 • Powered by Groq AI
        </p>
        <p style="color: #475569; font-size: 0.9em; margin: 8px 0 0 0;">
            🔒 Secure • 🚀 Fast • 🎯 Accurate • 📊 Advanced Analytics
        </p>
    </div>
""", unsafe_allow_html=True)
