import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time
import random
import threading
import io
import speech_recognition as sr
import pyttsx3
from streamlit_option_menu import option_menu
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="WattQ - Smart Energy", page_icon="⚡", layout="wide")

# --- CUSTOM CSS (POLISHED UI) ---
st.markdown("""
<style>
    /* Main Background */
    .main { background-color: #050505; }
    
    /* Metric Cards */
    div.stMetric {
        background: linear-gradient(135deg, #1e1e1e, #2a2a2a);
        border: 1px solid #444;
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    div.stMetric:hover {
        transform: translateY(-5px);
        border-color: #00FF7F;
    }
    
    /* Headers */
    h1 { 
        background: -webkit-linear-gradient(left, #00FF7F, #00C3FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
    }
    h2, h3 { color: #E0E0E0; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111;
        border-right: 1px solid #333;
    }
    
    /* Quote Styling */
    .quote-text {
        font-style: italic;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    
    /* Tip Card */
    .tip-card {
        background-color: #1a1a1a;
        border-left: 5px solid #00C3FF;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- TEXT TO SPEECH ---
engine_lock = threading.Lock()
def speak_text(text):
    def run_speech():
        with engine_lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            except: pass 
    t = threading.Thread(target=run_speech)
    t.start()

# --- HELPER: COLOR LOGIC ---
def get_status_color(load):
    if load < 1.0: return "#00FF7F"  # Low: Green
    elif load < 3.0: return "#FFD700" # Optimal: Yellow/Gold
    else: return "#FF4B4B"           # High: Red

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933886.png", width=80)
    st.title("WattQ")
    st.markdown("*Intelligent Energy Monitor*")
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Smart Tips", "Appliance DNA", "Community Rank", "AI Forecast", "Voice Assist", "Admin Control"],
        icons=["speedometer", "lightbulb", "cpu", "trophy", "graph-up-arrow", "mic", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#00994C"},
        }
    )
    st.divider()
    st.info("Status: Connected 🟢")

# --- FETCH DATA ---
def fetch_live_data():
    try: return requests.get(f"{API_URL}/api/live").json()
    except: return None

# --- PAGE 1: DASHBOARD ---
if selected == "Dashboard":
    st.title("⚡ WattQ Dashboard")
    st.markdown('<p class="quote-text">"Energy saved is energy generated."</p>', unsafe_allow_html=True)
    
    data = fetch_live_data()
    
    if data:
        if data['anomaly']:
            st.error("🚨 CRITICAL WARNING: ABNORMAL SURGE DETECTED! FIRE RISK.", icon="🔥")
        
        load = data['total_load_kw']
        color_hex = get_status_color(load)
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Current Load", f"{load} kW", "Live")
        k2.metric("Voltage", f"{data['voltage']} V", "Stable")
        k3.metric("Cost Rate", f"₹{data['cost_per_hour']}/hr", "Est.")
        k4.metric("Grid Health", "99%", "Optimal")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Real-Time Consumption")
            chart_data = pd.DataFrame({
                'Time': pd.date_range(start='now', periods=20, freq='s'),
                'Load (kW)': [load + (x*0.02) for x in range(20)]
            })
            fig_area = px.area(chart_data, x='Time', y='Load (kW)')
            fig_area.update_traces(line_color=color_hex, fillcolor=color_hex)
            fig_area.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)", 
                font_color="#ccc",
                yaxis=dict(range=[0, max(5, load+1)])
            )
            st.plotly_chart(fig_area, use_container_width=True)
            
        with col2:
            st.subheader("Active Units")
            apps = data['appliances']
            active_count = sum(1 for x in apps.values() if x['status'] == "ON")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = active_count,
                title = {'text': "Devices ON"},
                gauge = {
                    'axis': {'range': [None, 10]}, 
                    'bar': {'color': color_hex}, 
                    'bgcolor': "#222"
                }
            ))
            fig_gauge.update_layout(height=250, margin=dict(t=30,b=10), paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_gauge, use_container_width=True)

# --- PAGE 2: SMART TIPS (NEW FEATURE) ---
elif selected == "Smart Tips":
    st.title("💡 Personalized Recommendations")
    st.markdown("AI-driven insights based on your **Live Usage** and **Local Weather**.")
    
    col_in, col_btn = st.columns([2, 1])
    with col_in:
        city = st.text_input("Confirm Location for Weather Analysis", value="Hubballi")
    with col_btn:
        st.write("") # Spacer
        st.write("") # Spacer
        gen_btn = st.button("✨ Generate AI Tips", use_container_width=True)
    
    if gen_btn:
        with st.spinner("Analyzing your home's DNA..."):
            try:
                # Call Backend API
                res = requests.get(f"{API_URL}/api/recommendations?city={city}").json()
                tips_text = res.get('tips', "No recommendations available.")
                
                st.success("Analysis Complete!")
                st.divider()
                
                # Display Tips
                st.markdown(tips_text)
                
            except Exception as e:
                st.error("AI Service is currently busy. Please try again.")

    # Static Fallback / Examples if no generation yet
    if not gen_btn:
        st.info("Click the button above to analyze your real-time data.")
        st.markdown("### Why this matters:")
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Savings", "₹450", "Monthly")
        c2.metric("Carbon Footprint", "-12%", "Reduced")
        c3.metric("Grid Efficiency", "98%", "Optimized")

# --- PAGE 3: APPLIANCE DNA ---
elif selected == "Appliance DNA":
    st.title("🔍 Appliance DNA")
    st.markdown("### Identify & Optimize")
    
    device_catalog = {
        "Kitchen 🍳": ["Refrigerator", "Microwave", "Dishwasher", "Induction"],
        "Living Room 🛋️": ["Air Conditioner", "TV", "Smart Speaker", "Fan"],
        "Utility 🧺": ["Washing Machine", "Geyser", "Inverter", "Pump"],
        "Outdoor 🚗": ["EV Charger", "Garden Lights"]
    }

    if "my_appliances" not in st.session_state:
        st.session_state.my_appliances = ["Refrigerator", "Air Conditioner", "TV", "Fan"]

    with st.expander("📝 Device Manager (Click to Edit)", expanded=False):
        cols = st.columns(4)
        selected_temp = []
        for i, (category, devices) in enumerate(device_catalog.items()):
            with cols[i]:
                st.markdown(f"**{category}**")
                for dev in devices:
                    is_checked = dev in st.session_state.my_appliances
                    if st.checkbox(dev, value=is_checked, key=f"chk_{dev}"):
                        selected_temp.append(dev)
        if st.button("Update Profile"):
            st.session_state.my_appliances = selected_temp
            st.rerun()

    st.divider()
    
    if st.session_state.my_appliances:
        device_data = []
        total_load = 0
        for dev in st.session_state.my_appliances:
            status = "ON" if random.random() > 0.4 else "OFF"
            power = 0.05
            if dev in ["EV Charger", "Geyser", "Air Conditioner"]: power = random.uniform(1.5, 3.0)
            elif dev in ["Refrigerator", "Washing Machine"]: power = random.uniform(0.3, 1.0)
            
            actual = power if status == "ON" else 0.01
            total_load += actual
            device_data.append({"Device": dev, "Status": status, "Power": actual})
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            df_chart = pd.DataFrame(device_data)
            fig = px.pie(df_chart, values='Power', names='Device', hole=0.6, color_discrete_sequence=px.colors.sequential.Tealgrn)
            fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", font_color="white", title="Load Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("#### Live Insights")
            for item in device_data:
                status_color = "#00FF7F" if item["Status"] == "ON" else "#888"
                status_html = f'<span style="color:{status_color}; font-weight:bold;">{item["Status"]}</span>'
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 2, 2])
                    col_a.markdown(f"**{item['Device']}**")
                    col_b.markdown(status_html, unsafe_allow_html=True)
                    col_c.markdown(f"{item['Power']:.2f} kW")
                    st.divider()

# --- PAGE 4: COMMUNITY RANK ---
elif selected == "Community Rank":
    st.title("🏆 WattQ Leaderboard")
    st.markdown("Compare efficiency with your neighborhood.")
    
    neighbors = []
    for i in range(1, 8):
        load = round(random.uniform(0.5, 4.0), 2)
        score = int((10 - load) * 100)
        neighbors.append({"id": f"Neighbor #{random.randint(100,999)}", "load": load, "score": score, "is_user": False})
    
    try:
        user_load = requests.get(f"{API_URL}/api/live", timeout=1).json()['total_load_kw']
    except: user_load = 1.5
    
    neighbors.append({"id": "YOU (WattQ Home)", "load": user_load, "score": int((10-user_load)*100), "is_user": True})
    neighbors.sort(key=lambda x: x['load'])
    
    for idx, n in enumerate(neighbors): n['rank'] = idx + 1
    
    df = pd.DataFrame(neighbors)
    
    user_row = df[df['is_user'] == True]
    if not user_row.empty:
        user_rank = user_row.iloc[0]['rank']
        user_score = user_row.iloc[0]['score']
        m1, m2 = st.columns(2)
        m1.metric("Your Rank", f"#{user_rank}")
        m2.metric("Eco Score", f"{user_score} pts")
    
    st.subheader("Top Savers")
    display_df = df[['rank', 'id', 'load', 'score']].copy()
    display_df.columns = ["Rank", "Household", "Avg Load (kW)", "Score"]
    
    def highlight_row(row):
        return ['background-color: #006633' if "YOU" in row['Household'] else '' for _ in row]
    
    st.dataframe(display_df.style.apply(highlight_row, axis=1), use_container_width=True, hide_index=True)
    
    colors = ['#00FF7F' if x['is_user'] else '#444' for x in neighbors]
    fig = px.bar(df, x='id', y='load', title="Comparison (Lower is Better)")
    fig.update_traces(marker_color=colors)
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 5: FORECAST ---
elif selected == "AI Forecast":
    st.title("📈 FutureCast")
    st.markdown("Predictive insights based on **Hyper-local Weather**.")
    
    city = st.text_input("📍 Location", value="Hubballi")
    
    try:
        res = requests.get(f"{API_URL}/api/forecast?city={city}").json()
        df = pd.DataFrame(res)
        
        avg_temp = df['temp_c'].mean()
        total_units = df['predicted_kwh'].sum()
        est_cost = total_units * 10
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Temp", f"{avg_temp:.1f}°C")
        c2.metric("Pred. Units", f"{total_units:.1f} kWh")
        c3.metric("Est. Bill (5 Days)", f"₹{est_cost:.0f}")
        
        st.divider()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['date'], y=df['predicted_kwh'], name="Units (kWh)", marker_color='#00C3FF'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['temp_c'], name="Temp (°C)", yaxis="y2", line=dict(color='#FFD700', width=3)))
        
        fig.update_layout(
            yaxis=dict(title="Units (kWh)"),
            yaxis2=dict(title="Temp (°C)", overlaying="y", side="right"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white",
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except:
        st.error("Weather Service Unreachable.")

# --- PAGE 6: VOICE ASSISTANT ---
elif selected == "Voice Assist":
    st.title("🎙️ WattQ Voice")
    st.markdown("Ask: *'How much is my bill in Rupees?'*")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image("https://cdn-icons-png.flaticon.com/512/3747/3747161.png", width=120)
        
        # --- FIXED: Added format="wav" to ensure compatibility ---
        audio = mic_recorder(
            start_prompt="🔴 Tap to Speak",
            stop_prompt="⏹️ Stop",
            key="recorder",
            format="wav",  # <--- CRITICAL FIX
            use_container_width=True
        )
        
        if audio:
            st.info("Processing audio...")
            r = sr.Recognizer()
            try:
                # Convert bytes to audio source
                audio_data = sr.AudioFile(io.BytesIO(audio['bytes']))
                with audio_data as source:
                    r.adjust_for_ambient_noise(source) # Remove background noise
                    audio_content = r.record(source)
                
                # Transcribe
                text = r.recognize_google(audio_content)
                st.session_state.last_q = text
                
                # Send to Backend
                res = requests.post(f"{API_URL}/api/voice_assistant", json={"text": text}).json()
                st.session_state.last_a = res['response']
                speak_text(res['response'])
                
            except sr.UnknownValueError:
                st.error("Could not understand audio. Please speak clearly.")
            except sr.RequestError as e:
                st.error(f"Connection Error: {e}")
            except Exception as e:
                st.error(f"System Error: {e}")

    with c2:
        st.subheader("Conversation Log")
        chat_container = st.container(border=True)
        with chat_container:
            if "last_q" in st.session_state:
                with st.chat_message("user"):
                    st.write(st.session_state.last_q)
            
            if "last_a" in st.session_state:
                with st.chat_message("assistant"):
                    st.markdown(f"**WattQ:** {st.session_state.last_a}")
            
            if "last_q" not in st.session_state:
                st.caption("Waiting for voice input...")
# --- PAGE 7: ADMIN ---
elif selected == "Admin Control":
    st.title("⚙️ System Override")
    c1, c2 = st.columns(2)
    if c1.button("🔥 Simulate Surge"): requests.post(f"{API_URL}/api/simulate_danger?enable=true"); st.toast("Surge Active!")
    if c2.button("✅ Normalize Grid"): requests.post(f"{API_URL}/api/simulate_danger?enable=false"); st.toast("Grid Stable")