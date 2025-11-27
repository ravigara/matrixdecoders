import pandas as pd
import numpy as np
import random
import requests
from datetime import datetime, timedelta

class EnergySimulator:
    def __init__(self):
        self.base_load = 0.5  # kW (Always on)
        self.abnormal_mode = False 
        # 🔑 PASTE YOUR OPENWEATHER KEY BELOW
        self.weather_api_key = "11a5f911c186409494452fe5851c58fb" 
        
    def get_live_readings(self):
        noise = random.uniform(-0.1, 0.2)
        current_load = self.base_load + noise
        
        appliances = {
            "Fridge": {"status": "ON", "power": 0.2},
            "AC": {"status": "OFF", "power": 0.0},
            "Washing Machine": {"status": "OFF", "power": 0.0},
            "EV Charger": {"status": "OFF", "power": 0.0}
        }
        
        if random.random() > 0.7: 
            appliances["AC"]["status"] = "ON"
            appliances["AC"]["power"] = 1.5
            current_load += 1.5
            
        if self.abnormal_mode:
            current_load += 4.0 
            
        return {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "total_load_kw": round(current_load, 2),
            "voltage": round(random.uniform(218, 225), 1),
            "cost_per_hour": round(current_load * 0.12, 2),
            "appliances": appliances,
            "anomaly": self.abnormal_mode
        }

    def get_real_weather_forecast(self, city="Hubballi"):
        if self.weather_api_key == "YOUR_OPENWEATHER_API_KEY_HERE":
            return self._get_dummy_forecast()

        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url).json()
            
            if response.get("cod") != "200":
                return self._get_dummy_forecast()

            forecast_data = []
            seen_dates = set()
            
            for item in response['list']:
                dt_txt = item['dt_txt']
                date_str = dt_txt.split(" ")[0]
                
                if date_str not in seen_dates:
                    temp = item['main']['temp']
                    predicted_kwh = 10.0 
                    if temp > 25: predicted_kwh += (temp - 25) * 0.8 
                    elif temp < 18: predicted_kwh += (18 - temp) * 0.6
                        
                    forecast_data.append({
                        "date": date_str,
                        "temp_c": round(temp, 1),
                        "predicted_kwh": round(predicted_kwh, 2)
                    })
                    seen_dates.add(date_str)
                    if len(forecast_data) >= 5: break
            
            return forecast_data
        except Exception as e:
            return self._get_dummy_forecast()

    def _get_dummy_forecast(self):
        dates = [datetime.now() + timedelta(days=i) for i in range(5)]
        return [{"date": d.strftime("%Y-%m-%d"), "temp_c": 28, "predicted_kwh": 12} for d in dates]

    def trigger_anomaly(self, status: bool):
        self.abnormal_mode = status
        return {"status": "Anomaly mode set to " + str(status)}

sim_engine = EnergySimulator()