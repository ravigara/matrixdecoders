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
st.set_page_config(page_title="EcoSense AI", page_icon="⚡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main { background-color: #0E1117; }
    div.stMetric {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    div.stMetric:hover { border-color: #00FF7F; }
    h1, h2, h3 { color: #00FF7F; font-family: 'Segoe UI', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- TEXT TO SPEECH SETUP ---
engine_lock = threading.Lock()

def speak_text(text):
    """Function to make the computer speak the response"""
    def run_speech():
        with engine_lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            except:
                pass 
    t = threading.Thread(target=run_speech)
    t.start()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3103/3103446.png", width=100)
    st.title("EcoSense AI")
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Appliance DNA", "Community Rank", "AI Forecast", "Voice Assist", "Admin Control"],
        icons=["speedometer2", "cpu", "trophy", "graph-up", "mic", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#1E1E1E"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#00994C"},
        }
    )
    st.divider()
    st.info("System Status: Online 🟢")

# --- HELPER: FETCH DATA ---
def fetch_live_data():
    try:
        response = requests.get(f"{API_URL}/api/live")
        return response.json()
    except:
        return None

# --- PAGE 1: DASHBOARD ---
if selected == "Dashboard":
    st.title("🏠 Live Energy Monitor")
    
    data = fetch_live_data()
    
    if data:
        if data['anomaly']:
            st.error("🚨 CRITICAL ALERT: ABNORMAL POWER SPIKE DETECTED! POTENTIAL FIRE HAZARD.", icon="🔥")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Current Load", f"{data['total_load_kw']} kW", "Live")
        kpi2.metric("Voltage", f"{data['voltage']} V", "Stable")
        kpi3.metric("Est. Cost/Hr", f"${data['cost_per_hour']}", "USD")
        kpi4.metric("Grid Health", "98%", "Excellent")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("⚡ Real-Time Consumption Trend")
            chart_data = pd.DataFrame({
                'Time': pd.date_range(start='now', periods=20, freq='s'),
                'Power (kW)': [data['total_load_kw'] + (x*0.05) for x in range(20)]
            })
            fig_area = px.area(chart_data, x='Time', y='Power (kW)', color_discrete_sequence=['#00FF7F'])
            fig_area.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_area, use_container_width=True)
            
        with col2:
            st.subheader("🔌 Active Devices")
            apps = data['appliances']
            active_count = sum(1 for x in apps.values() if x['status'] == "ON")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = active_count,
                title = {'text': "Devices ON"},
                gauge = {'axis': {'range': [None, 10]}, 'bar': {'color': "#00FF7F"}}
            ))
            fig_gauge.update_layout(height=250, margin=dict(l=20,r=20,t=50,b=20), paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_gauge, use_container_width=True)

# --- PAGE 2: APPLIANCE DNA (Restored "Old Good Style") ---
elif selected == "Appliance DNA":
    st.title("🔍 Non-Intrusive Load Monitoring (NILM)")
    st.markdown("### 🛠️ Device Configuration & Analysis")
    
    # Categorized Device List
    device_catalog = {
        "Kitchen 🍳": ["Refrigerator", "Microwave", "Dishwasher", "Induction Cooktop", "Toaster"],
        "Living Room 🛋️": ["Air Conditioner", "Television", "Smart Speaker", "Ceiling Fan"],
        "Laundry & Utility 🧺": ["Washing Machine", "Dryer", "Water Heater", "Vacuum Cleaner"],
        "Garage & Outdoor 🚗": ["EV Charger", "Pool Pump", "Lawn Mower"]
    }

    if "my_appliances" not in st.session_state:
        st.session_state.my_appliances = ["Refrigerator", "Air Conditioner", "Television", "Washing Machine"]

    # The Expander Style you liked
    with st.expander("📝 Manage Device List (Click to Edit)", expanded=False):
        st.info("Select the appliances currently connected to your smart meter.")
        cols = st.columns(4)
        selected_temp = []
        
        for i, (category, devices) in enumerate(device_catalog.items()):
            with cols[i]:
                st.markdown(f"**{category}**")
                for dev in devices:
                    is_checked = dev in st.session_state.my_appliances
                    if st.checkbox(dev, value=is_checked, key=f"chk_{dev}"):
                        selected_temp.append(dev)
        
        if st.button("💾 Update Monitored Devices"):
            st.session_state.my_appliances = selected_temp
            st.success("Device list updated successfully!")
            time.sleep(1)
            st.rerun()

    st.divider()
    st.subheader(f"📊 Live Analysis: {len(st.session_state.my_appliances)} Devices Monitored")

    if not st.session_state.my_appliances:
        st.warning("⚠️ No devices selected. Please configure your device list above.")
    else:
        total_dummy_load = 0
        device_data = []
        for dev in st.session_state.my_appliances:
            status = "ON" if random.random() > 0.4 else "OFF"
            base_power = 0.05
            if dev in ["EV Charger", "Water Heater", "Air Conditioner"]: base_power = random.uniform(1.5, 3.5)
            elif dev in ["Refrigerator", "Washing Machine", "Dishwasher"]: base_power = random.uniform(0.3, 1.2)
            
            actual_power = base_power if status == "ON" else 0.005
            total_dummy_load += actual_power
            device_data.append({"Device": dev, "Status": status, "Power (kW)": round(actual_power, 3), "Usage %": 0})
        
        for d in device_data:
            d["Usage %"] = round((d["Power (kW)"] / total_dummy_load) * 100, 1) if total_dummy_load > 0 else 0

        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.markdown("#### ⚡ Real-Time Load Breakdown")
            df_chart = pd.DataFrame(device_data)
            df_active = df_chart[df_chart["Power (kW)"] > 0.01]
            if not df_active.empty:
                fig = px.pie(df_active, values='Power (kW)', names='Device', hole=0.5, color_discrete_sequence=px.colors.sequential.Tealgrn)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("All devices are currently in Standby/OFF mode.")

        with col2:
            st.markdown("#### 🔍 Device Health & Patterns")
            for item in device_data:
                color = "green" if item["Status"] == "ON" else "grey"
                alert = None
                if item["Device"] == "Air Conditioner" and item["Status"] == "ON" and random.random() > 0.8: alert = "⚠️ Compressor strain detected"
                elif item["Device"] == "Refrigerator" and random.random() > 0.9: alert = "❄️ Door likely left open"

                with st.container():
                    c1, c2, c3 = st.columns([2, 1, 2])
                    c1.markdown(f"**{item['Device']}**")
                    c2.markdown(f":{color}[{item['Status']}]")
                    c3.markdown(f"**{item['Power (kW)']} kW**")
                    if alert: st.error(alert)
                    st.progress(int(item["Usage %"]) if item["Usage %"] < 100 else 100)
                    st.divider()

# --- PAGE 3: COMMUNITY RANK (Restored Leaderboard + Chart) ---
elif selected == "Community Rank":
    st.title("🏆 Community Energy Benchmarking")
    st.markdown("Compare your efficiency with similar households anonymously.")
    
    # 1. GENERATE LOCAL DATA (Safe Mode)
    neighbors = []
    for i in range(1, 8):
        n_load = round(random.uniform(0.5, 4.0), 2)
        score = int((10 - n_load) * 100)
        neighbors.append({
            "id": f"Neighbor #{random.randint(1000, 9999)}",
            "usage_kw": n_load,
            "score": score,
            "is_user": False,
            "rank": 0
        })
    
    # Get user load safely
    try:
        live = requests.get(f"{API_URL}/api/live", timeout=0.5).json()
        user_load = live['total_load_kw']
    except:
        user_load = 1.2
        
    neighbors.append({
        "id": "YOU (My Home)",
        "usage_kw": user_load,
        "score": int((10 - user_load) * 100),
        "is_user": True,
        "rank": 0
    })
    
    # Sort
    neighbors.sort(key=lambda x: x['usage_kw'])
    for idx, item in enumerate(neighbors):
        item['rank'] = idx + 1
        
    df_comm = pd.DataFrame(neighbors)
    user_entry = next((item for item in neighbors if item["is_user"]), None)
    
    # 2. TOP METRICS
    st.info(f"🔒 Privacy Note: All neighbor identities are anonymized. You are viewing 'Live' comparisons.")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Your Community Rank", f"#{user_entry['rank']}", delta="Top 20%" if user_entry['rank'] <=3 else "- Needs Improvement")
    with c2:
        st.metric("Your Green Score", f"{user_entry['score']} pts", "High Efficiency" if user_entry['score'] > 800 else "Average")

    # 3. LEADERBOARD TABLE (RESTORED)
    st.subheader("🏅 Top Energy Savers (Live Leaderboard)")
    
    def highlight_user(row):
        return ['background-color: #2E8B57; color: white' if row['Household ID'] == "YOU (My Home)" else '' for _ in row]

    display_df = df_comm[['rank', 'id', 'usage_kw', 'score']].copy()
    display_df.columns = ["Rank", "Household ID", "Current Usage (kW)", "Green Score"]
    
    st.dataframe(
        display_df.style.apply(highlight_user, axis=1),
        use_container_width=True,
        hide_index=True
    )

    # 4. CHART
    st.subheader("📊 You vs The Neighborhood")
    colors = ['#00FF7F' if x == "YOU (My Home)" else '#555555' for x in df_comm['id']]
    
    fig = px.bar(
        df_comm, 
        x='id', 
        y='usage_kw', 
        title="Real-Time Load Comparison",
        labels={'usage_kw': 'Power Usage (kW)', 'id': 'Household'},
        text_auto=True
    )
    fig.update_traces(marker_color=colors)
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 4: AI FORECAST (Real Weather Version) ---
elif selected == "AI Forecast":
    st.title("📈 Smart Consumption Forecasting")
    st.markdown("Predicts energy usage based on **Real-Time Weather**.")
    
    col_input, col_status = st.columns([1, 2])
    with col_input:
        city = st.text_input("📍 Your Location", value="Hubballi")
    
    try:
        res = requests.get(f"{API_URL}/api/forecast?city={city}").json()
        df = pd.DataFrame(res)
        
        avg_temp = df['temp_c'].mean()
        total_pred = df['predicted_kwh'].sum()
        
        with col_status:
            m1, m2, m3 = st.columns(3)
            m1.metric("Avg Temp (5 Days)", f"{avg_temp:.1f}°C")
            m2.metric("Predicted Usage", f"{total_pred:.1f} kWh")
            m3.metric("Cost Est.", f"${total_pred * 0.12:.2f}")
            
        st.divider()
        st.subheader(f"Weather vs Energy Trend for {city}")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['date'], y=df['predicted_kwh'], name="Predicted Energy (kWh)", marker_color='#00FF7F'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['temp_c'], name="Temperature (°C)", yaxis="y2", line=dict(color='#FF5733', width=3)))
        
        fig.update_layout(
            yaxis=dict(title="Energy (kWh)"),
            yaxis2=dict(title="Temp (°C)", overlaying="y", side="right"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white",
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if avg_temp > 28: st.warning("🔥 High Temperatures predicted! AC usage will likely increase your bill by ~15%.")
        elif avg_temp < 18: st.info("❄️ Cold weather ahead. Heating load detected.")
        else: st.success("✅ Moderate weather. Optimal energy efficiency expected.")
            
    except Exception as e:
        st.error(f"Could not fetch weather data. Check API Key or City Name. Error: {e}")

# --- PAGE 5: VOICE ASSISTANT (Restored Full Version) ---
elif selected == "Voice Assist":
    st.title("🎙️ Gemini Eco-Assistant")
    st.markdown("### Interactive Energy Advisor")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3747/3747161.png", width=150)
        st.info("💡 Tip: Click the mic, allow permission, and ask: *'How much did I spend today?'*")
        
        st.write("### 🗣️ Speak Now:")
        audio_data = mic_recorder(
            start_prompt="🔴 Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            format="wav",
            key="recorder"
        )
        
        if audio_data:
            st.success("✅ Audio Captured! Processing...")
            audio_bytes = audio_data['bytes']
            r = sr.Recognizer()
            try:
                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio_content = r.record(source)
                    user_text = r.recognize_google(audio_content)
                
                st.session_state.last_voice_query = user_text
                
                # SEND TO BACKEND
                payload = {"text": user_text}
                try:
                    res = requests.post(f"{API_URL}/api/voice_assistant", json=payload)
                    bot_reply = res.json()['response']
                    st.session_state.last_voice_reply = bot_reply
                    speak_text(bot_reply)
                except Exception as e:
                    st.error(f"Backend Error: {e}")
            except sr.UnknownValueError:
                st.warning("Could not understand audio.")
            except sr.RequestError:
                st.error("Speech Recognition Service down.")

    with col2:
        st.subheader("Conversation Log")
        chat_container = st.container(border=True)
        with chat_container:
            if "last_voice_query" in st.session_state:
                with st.chat_message("user"):
                    st.write(st.session_state.last_voice_query)
            if "last_voice_reply" in st.session_state:
                with st.chat_message("assistant"):
                    st.markdown(f"**Gemini:** {st.session_state.last_voice_reply}")
            if "last_voice_query" not in st.session_state:
                st.caption("Waiting for voice input...")

# --- PAGE 6: ADMIN CONTROL ---
elif selected == "Admin Control":
    st.title("⚙️ Demo Controls")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Trigger Emergency")
        if st.button("Simulate Overload (Fire Hazard)"):
            requests.post(f"{API_URL}/api/simulate_danger?enable=true")
            st.toast("Emergency Mode ACTIVATED!", icon="🚨")
    with col2:
        st.subheader("✅ Reset System")
        if st.button("Restore Normal Operation"):
            requests.post(f"{API_URL}/api/simulate_danger?enable=false")
            st.toast("System Normalized", icon="✅")