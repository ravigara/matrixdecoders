# ⚡ WattQ: Intelligent Energy Monitor

> *"Energy saved is energy generated."*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)

WattQ transforms the traditional "dumb" electricity meter into an intelligent, proactive energy consultant. Built for Indian households, it uses Generative AI and Real-Time Weather data to help users reduce bills, identify power-hungry appliances, and prevent electrical hazards—all without needing expensive smart plugs for every socket.

---

🛑 The Problem
We all dread the end of the month when the electricity bill arrives. We stare at the cost, wondering, *"Was it the AC? The Geyser? Or did I leave the lights on?"* Current meters tell you **how much** you owe, but never **why**.

💡 The Solution
WattQ is a real-time dashboard that acts as a digital twin for your home's energy.
1.  **Visualizes** consumption in real-time (Green/Yellow/Red status).
2.  **Identifies** which appliances are running using NILM logic.
3.  **Predicts** bills based on local weather forecasts.
4.  **Advises** you on how to save money using GenAI.

---
🚀 Key Features

 1. Live Dashboard (INR Support)
* **Real-Time Metrics:** Tracks Load (kW), Voltage, and Grid Health.
* **Dynamic Costing:** Instantly converts usage to **Indian Rupees (₹)**.
* **Visual Feedback:** The interface shifts colors based on load intensity:
    * 🟢 **Green:** Eco-friendly (< 1kW)
    * 🟡 **Yellow:** Standard Usage
    * 🔴 **Red:** High Consumption (> 3kW)

2. Appliance DNA (NILM)
* **Virtual Disaggregation:** Estimates which devices (AC, Fridge, Geyser) are active from a single power source.
* **Health Insights:** Detects anomalies like "Compressor Strain" or "Door Left Open" without extra hardware.

🧠 3. Smart Recommendations (Weather-Aware)
* Integrates with **OpenWeatherMap** to analyze local temperature.
* **Gemini AI** combines Weather + Live Load to give specific tips.
    * *Example:* "It's 32°C outside. Set AC to 24°C to save ₹450/month."

4. WattQ Voice Assistant
* A browser-native voice interface powered by Google Speech-to-Text and Gemini.
* **Context-Aware:** You can ask *"How much is my bill?"* and it reads the live sensors to give an accurate answer.

5. Community Leaderboard
* Gamifies energy saving by comparing your efficiency with anonymized "neighbors."
* Ranks users based on a calculated "Eco Score."

6. Safety & Simulation
* **Anomaly Detection:** Instantly flags short circuits or fire hazards.
* **Simulation Mode:** Includes a robust simulation engine to demonstrate "Disaster Modes" (Surges) during hackathon pitches.

---
🛠️ How to Run Locally

### Prerequisites
* Python 3.9 or higher.
* API Keys for **Google Gemini** and **OpenWeatherMap**.

1. Clone & Install

git clone https://github.com/ravigara/matrixdecoders.git
cd wattq
pip install -r requirements.txt

2. Configure Keys
Open backend/main.py and backend/simulator.py and paste your API keys:

Gemini Key: Inside backend/main.py

Weather Key: Inside backend/simulator.py

3. Launch the System
You need to run the Backend (Brain) and Frontend (UI) in separate terminals.

Terminal 1: Backend
uvicorn backend.main:app --reload

Terminal 2: Frontend
streamlit run frontend/app.py

Team Members
Raviteja G
Sanket Khot
