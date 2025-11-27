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
    return {"status": "WattQ System Operational"}

@app.get("/api/live")
def live_metrics():
    return sim_engine.get_live_readings()

@app.get("/api/forecast")
def forecast_data(city: str = "Hubballi"):
    return sim_engine.get_real_weather_forecast(city)

@app.get("/api/recommendations")
def get_smart_tips(city: str = "Hubballi"):
    """
    Generates personalized energy saving tips based on:
    1. Live Load (Simulator)
    2. Active Appliances (Simulator)
    3. Current Weather (OpenWeather)
    """
    # 1. Gather Data
    live_data = sim_engine.get_live_readings()
    weather_data = sim_engine.get_real_weather_forecast(city)
    
    # Get current weather (first item in forecast list)
    current_temp = weather_data[0]['temp_c'] if weather_data else 30
    active_appliances = [k for k, v in live_data['appliances'].items() if v['status'] == 'ON']
    
    # 2. Construct AI Prompt
    prompt = f"""
    Act as an expert energy consultant.
    Analyze this household scenario and give 3 specific, actionable energy-saving recommendations.
    
    DATA:
    - Current Load: {live_data['total_load_kw']} kW
    - Active Devices: {', '.join(active_appliances) if active_appliances else 'None'}
    - External Temperature: {current_temp}°C
    - Cost Rate: ₹{live_data['cost_per_hour']}/hr
    
    OUTPUT FORMAT:
    Return exactly 3 bullet points. Each point must have a bold title and a short explanation.
    Example:
    * **Adjust AC:** It's 32°C outside, set AC to 24°C to save ₹200.
    """
    
    try:
        response = model.generate_content(prompt)
        return {"tips": response.text}
    except Exception as e:
        return {"tips": "Unable to generate tips. Please check connection."}

@app.post("/api/simulate_danger")
def trigger_danger(enable: bool):
    return sim_engine.trigger_anomaly(enable)

@app.post("/api/voice_assistant")
def process_voice_gemini(query: VoiceQuery):
    live_data = sim_engine.get_live_readings()
    active_appliances = [k for k, v in live_data['appliances'].items() if v['status'] == 'ON']
    
    system_instruction = f"""
    You are WattQ, an intelligent home energy assistant designed for Indian households.
    
    CURRENT STATUS:
    - Total Load: {live_data['total_load_kw']} kW
    - Active Appliances: {', '.join(active_appliances) if active_appliances else 'None'}
    - Voltage: {live_data['voltage']} V
    - Estimated Cost per Hour: ₹{live_data['cost_per_hour']}
    - Safety Status: {'CRITICAL WARNING' if live_data['anomaly'] else 'Normal'}
    
    USER QUESTION: "{query.text}"
    
    INSTRUCTIONS: 
    - Answer briefly (under 30 words).
    - Use Indian Rupees (₹) for costs.
    - Be helpful and friendly.
    """
    try:
        response = model.generate_content(system_instruction)
        return {"response": response.text}
    except Exception as e:
        return {"response": f"Brain connection error: {str(e)}"}