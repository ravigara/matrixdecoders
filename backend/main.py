import os
from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from .simulator import sim_engine

app = FastAPI()

# 🔑 PASTE YOUR GEMINI API KEY BELOW
os.environ["GOOGLE_API_KEY"] = "AIzaSyBHk3IAxqMuQ4H4vFudBuOSLB6buOLXbIU"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

class VoiceQuery(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "System Operational"}

@app.get("/api/live")
def live_metrics():
    return sim_engine.get_live_readings()

@app.get("/api/forecast")
def forecast_data(city: str = "Hubballi"):
    return sim_engine.get_real_weather_forecast(city)

@app.post("/api/simulate_danger")
def trigger_danger(enable: bool):
    return sim_engine.trigger_anomaly(enable)

@app.post("/api/voice_assistant")
def process_voice_gemini(query: VoiceQuery):
    live_data = sim_engine.get_live_readings()
    active_appliances = [k for k, v in live_data['appliances'].items() if v['status'] == 'ON']
    
    system_instruction = f"""
    You are EcoSense, an intelligent home energy assistant.
    CURRENT HOME STATUS:
    - Total Load: {live_data['total_load_kw']} kW
    - Active Appliances: {', '.join(active_appliances) if active_appliances else 'None'}
    - Voltage: {live_data['voltage']} V
    - Cost per Hour: ${live_data['cost_per_hour']}
    - Safety Status: {'CRITICAL WARNING' if live_data['anomaly'] else 'Normal'}
    USER QUESTION: "{query.text}"
    INSTRUCTIONS: Answer briefly (under 30 words). Be helpful.
    """
    try:
        response = model.generate_content(system_instruction)
        return {"response": response.text}
    except Exception as e:
        return {"response": f"Brain connection error: {str(e)}"}