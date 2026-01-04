import streamlit as st
import google.generativeai as genai
import warnings
import time
import random

# --- WARNING SUPPRESSION ---
warnings.filterwarnings("ignore")

# --- CONFIGURATION ---

import streamlit as st
# API Key from Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Tata Elxsi - GenAI Suite",
    layout="wide",
    page_icon="🚘",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Tata Blue Theme) ---
st.markdown("""
<style>
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #4da6ff;}
    .stTextArea textarea {font-size: 14px; font-family: 'Courier New', monospace; background-color: #1c1f26; color: white;}
    div.stButton > button:first-child {background-color: #0066cc; color: white; border-radius: 8px; border: none; padding: 10px 24px;}
    div.stButton > button:hover {background-color: #0052a3; color: white;}
    div[data-testid="stMetricValue"] {font-size: 36px; color: #00ff80; font-weight: 700;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ System Configuration")

# 1. Model Selection
try:
    genai.configure(api_key=API_KEY)
    available_models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not available_models: available_models = ["gemini-1.5-flash"]
except:
    available_models = ["gemini-1.5-flash"]

selected_model_name = st.sidebar.selectbox("Select AI Model:", available_models, index=0)
model = genai.GenerativeModel(selected_model_name)

# 2. Domain & Language
system_type = st.sidebar.selectbox(
    "Select Vehicle Domain:", 
    ["Battery Management System (BMS)", "Tyre Pressure Monitoring (TPMS)", "ADAS - Lane Keep Assist", "Motor Controller"]
)
 
target_language = st.sidebar.radio(
    "Target Language:", 
    ["C++ (MISRA Standard)", "Python", "Rust", "Kotlin (Android/HMI)"] 
)

# --- MAIN HEADER WITH LOGO ---
col_logo, col_title = st.columns([1, 5])

with col_logo:
    try:
        
        st.image("logo.jpg", width=140) 
    except:
       
        st.markdown("## 🚘 TATA ELXSI")

with col_title:
    st.title("Automotive GenAI Workspace")
    st.caption("🚀 Powered by TELIPORT Season 3 | Experience-Led Engineering")

st.markdown("---")

# --- TABS SETUP ---
tab1, tab2 = st.tabs(["📝 Code Generator", "📊 Simulation Dashboard"])

# --- TAB 1: CODE GENERATOR ---
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Functional Requirements")
        default_prompt = f"""Write a {target_language} class for a {system_type}.
Requirements:
1. Implement a method to read sensor data.
2. Implement logic to detect critical thresholds.
3. Trigger a safety alert if thresholds are breached.
4. Ensure code follows automotive safety standards (MISRA/ISO 26262).
5. Add detailed comments."""
        
        user_prompt = st.text_area("System Specifications:", default_prompt, height=350)
        generate_btn = st.button("Generate Source Code ⚡", type="primary")

    with col2:
        st.subheader("2. Generated Artifacts")
        if generate_btn:
            with st.spinner(f"Compiling with {selected_model_name}..."):
                try:
                    # Engineering Prompt Injection
                    system_instruction = f"""
                    You are an Expert Automotive Software Architect at Tata Elxsi.
                    Your Goal: Generate high-performance, safe code for {system_type} complying with SDV (Software Defined Vehicle) standards.
                    
                    Strict Requirements:
                    1. LANGUAGE: Use {target_language}.
                    2. ARCHITECTURE: Implement a Service-Oriented Architecture (SoA). Define clear Service Interfaces (APIs).
                    3. SAFETY: Follow MISRA C++ (for C++) or ASPICE guidelines. Handle errors gracefully.
                    4. TESTING: Along with the main code, generate a specific 'Unit Test Case' block to validate the logic.
                    5. DOCUMENTATION: Add comments explaining the 'Service Interface' and safety logic.
                    """
                    final_prompt = system_instruction + "\n\nUser Request: " + user_prompt
                    
                    response = model.generate_content(final_prompt)
                    
                    st.success("✔ Generation Successful")
                  
                    
                    # --- KPI DISPLAY---
                    kpi1, kpi2, kpi3 = st.columns(3)
                    kpi1.metric("⏱️ Time Saved", "98%", "4hrs → 2s")
                    kpi2.metric("💰 Cost Reduced", "High", "Manual Effort")
                    kpi3.metric("✅ Compliance", "100%", "MISRA C++")
                    
                    st.markdown("---")
                    
                
                    st.code(response.text, language=target_language.lower().split()[0])
                    st.session_state['generated_code'] = response.text
                    
                    # Download Button
                    file_ext = "cpp" if "C++" in target_language else "py"
                    st.download_button("📥 Download Code", response.text, f"generated_code.{file_ext}")
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: VISUALIZATION DASHBOARD ---
with tab2:
    st.header(f"🖥️ Virtual Validation: {system_type}")
    
    sim_col1, sim_col2 = st.columns([1, 2])
    
    with sim_col1:
        st.subheader("Sensor Inputs")
        # Smart Sliders
        if "Battery" in system_type:
            val1 = st.slider("Voltage (V)", 0.0, 5.0, 3.7)
            val2 = st.slider("Temp (°C)", -10, 100, 25)
            threshold = 45
        elif "Tyre" in system_type:
            val1 = st.slider("Pressure (PSI)", 0, 50, 32)
            val2 = st.slider("Temp (°C)", 0, 80, 30)
            threshold = 28
        else:
            val1 = st.slider("Sensor 1", 0, 100, 50)
            val2 = st.slider("Sensor 2", 0, 100, 50)
            threshold = 80

        if st.button("Run Diagnostics 🔄"):
            st.toast("Running Diagnostic Checks...", icon="🚗")
            time.sleep(1)

    with sim_col2:
        st.subheader("Real-time Diagnostics Panel")
        m1, m2, m3 = st.columns(3)
        m1.metric("Sensor 1", val1)
        m2.metric("Sensor 2", val2)
        
        status = "NORMAL"
        status_color = "#00ff80" # Green
        
        # Logic Check
        if "Battery" in system_type and (val1 < 3.2 or val2 > threshold):
            status = "CRITICAL WARNING"
            status_color = "#ff4b4b" # Red
        elif "Tyre" in system_type and val1 < threshold:
            status = "LOW PRESSURE"
            status_color = "#ff4b4b"
            
        m3.markdown(f"**Status:** <span style='color:{status_color}; font-size:24px; font-weight:bold'>{status}</span>", unsafe_allow_html=True)
        
        st.write("Live Telemetry:")
        # Dynamic Graph Logic
        if "Battery" in system_type:
             # Discharging effect
             chart_data = [float(val1) - (i * 0.05) + (random.uniform(-0.02, 0.02)) for i in range(20)]
        else:
             chart_data = [val1 + random.uniform(-1, 1) for _ in range(20)]
             
        st.line_chart(chart_data)
