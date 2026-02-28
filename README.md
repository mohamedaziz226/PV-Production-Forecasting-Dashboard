# ☀️ PV Production Forecasting Dashboard

A real-time solar power production forecasting application with AI-powered battery management recommendations.

## 📋 Quick Overview

This project provides:
- **Real-time weather data** from OpenWeatherMap API
- **ML-powered solar production forecasts** using XGBoost
- **Interactive dashboard** built with Streamlit
- **AI decision support** from Gemini, Claude, or GPT-4

**Status**: ✅ Fully operational and tested

---

## 🚀 Getting Started (5 minutes)

### 1. Prerequisites
- Python 3.8+ (verify: `python --version`)
- Virtual environment activated: `.venv\Scripts\activate`
- OpenWeatherMap API key (free tier available)

### 2. Get Your Weather API Key
1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Copy your API key from the dashboard

### 3. Configure Your Environment
Open or create `.env` file in the project root:
```env
WEATHER_API_KEY=your_openweathermap_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=optional_openai_key
ANTHROPIC_API_KEY=optional_anthropic_key
```

**Required**: `WEATHER_API_KEY` only

**Optional LLM Keys** (for AI recommendations, pick ONE):
- **Gemini** (Free): https://ai.google.dev/ → Click "Get API Key"
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com

### 4. Install Dependencies
```bash
pip install -r requirements_dashboard.txt
```

### 5. Launch the Dashboard
```bash
streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`

---

## 💡 How to Use the Dashboard

### Basic Workflow
1. **Enter Location**: Type a city name and country code (e.g., "Sfax, TN" or "Paris, FR")
2. **Fetch Data**: Click "Fetch Weather & Predict"
3. **View Results**:
   - Current weather conditions
   - 24-hour production forecast chart
   - 48-hour weather forecast
4. **Optional AI Analysis**: Enable "AI Decision Agent" for battery recommendations

### Dashboard Features

#### Weather Display
- **Current Conditions**: Temperature, humidity, wind speed, cloud coverage
- **Forecast**: 5-day hourly forecast data
- **Location**: Latitude/longitude confirmation

#### Production Forecast
- **24-hour Chart**: Predicted solar production output (kW)
- **Accuracy**: Based on XGBoost model trained on historical data
- **Model Features**:
  - Timestamp: Hour of day + Day of week
  - **Température ambiante(℃)** - Ambient temperature
  - **Humidité ambiante(%RH)** - Ambient humidity
  - **Vitesse vent(m/s)** - Wind speed
  - **Irradiation transitoire pente(W/㎡)** - Solar irradiance

#### AI Decision Agent
Enable with the sidebar toggle to get:
- **Charging Recommendations**: When to charge battery storage
- **Discharging Recommendations**: When to use stored energy
- **Weather Analysis**: Impact of forecast conditions
- **Risk Assessment**: Potential production drops

**Available LLM Providers** (choose one):
- **Gemini** (Google) - Free tier, recommended
- **Claude** (Anthropic) - Paid subscription
- **GPT-4** (OpenAI) - Paid subscription

---

## 📁 Project Structure

```
.
├── app.py                          # Main Streamlit dashboard
├── config.py                       # Configuration and constants
├── weather_api.py                  # OpenWeatherMap integration
├── model_utils.py                  # ML model inference engine
├── llm_agent.py                    # LLM-based recommendations
│
├── best_model_exogenous.pkl        # Trained XGBoost model
├── project_model.pkl               # Alternative model backup
│
├── projet_ML (1).ipynb             # Original ML training notebook
├── BDDCorrigeManuellement.xlsx     # Training data
│
├── requirements_dashboard.txt      # Python dependencies
├── .env                            # API keys (not in git)
└── README.md                       # This file
── demo.mp4                        # demo

```

---

## 🔧 Configuration Options

### Model Features
The ML model uses these 5 input features (plus timestamp):
- **Température ambiante(℃)** - From weather API
- **Humidité ambiante(%RH)** - From weather API
- **Vitesse vent(m/s)** - From weather API
- **Irradiation transitoire pente(W/㎡)** - Estimated from cloud coverage
- **Timestamp** - Encoded as hour (0-23) + day of week (7 one-hot columns)

### Dashboard Customization
In `app.py`, modify:
- Colors and styling in CSS section
- Chart layouts and configurations
- Sidebar controls and parameters

### LLM Configuration
To enable AI recommendations:
1. Get a free API key from https://ai.google.dev/
2. Add to `.env`: `GEMINI_API_KEY=your_actual_key_here`
3. Restart the dashboard
4. Enable "AI Decision Agent" toggle in sidebar

**Alternative providers**:
- **OpenAI GPT-4**: https://platform.openai.com/api-keys
- **Anthropic Claude**: https://console.anthropic.com

---

## 🐛 Troubleshooting

### Dashboard Won't Load
```bash
# Clear cache and restart
pip install --upgrade -r requirements_dashboard.txt
streamlit run app.py --logger.level=debug
```

### "Weather API Error"
- ✓ Verify API key in `.env` is correct
- ✓ Check internet connection
- ✓ Ensure API key has monthly quota remaining

### "Model Not Found"
- ✓ Check `best_model_exogenous.pkl` exists
- ✓ Verify file isn't corrupted: regenerate from `projet_ML (1).ipynb`

### "ImportError: google.generativeai"
```bash
pip install google-generativeai
```

### LLM Recommendations Not Showing
- ✓ **Verify API key is valid**: Get a fresh key from https://ai.google.dev/
- ✓ Paste the actual key in `.env`: `GEMINI_API_KEY=your_actual_key_here`
- ✓ Restart the dashboard (Ctrl+C, then run again)
- ✓ Check internet connectivity
- ✓ Ensure account has remaining API quota

---

## 🎯 Use Cases

### Solar Farm Operators
- Forecast daily production for planning
- Optimize battery charging/discharging
- Plan maintenance windows

### Energy Storage Managers
- Predict when to charge/discharge storage
- Maximize revenue from load shifting
- Meet grid demand forecasts

### Researchers
- Analyze weather impact on production
- Validate ML model predictions
- Develop improved forecasting models

---

## 📊 Example Predictions

Given weather input:
```
Temperature: 28°C
Humidity: 45%
Wind Speed: 3.2 m/s
Cloud Coverage: 20%
Hour: 14:00
```

Expected output:
```
Predicted Power: 4.8 kW
Confidence: High (sunny conditions)
```

---

## 🔐 Security Notes

1. **Never commit `.env` file** to git (it's ignored)
2. **Keep API keys private** - regenerate if exposed
3. **Use environment variables** in production
4. **Monitor API usage** to avoid unexpected charges

---

## 📚 Documentation Files

- **README.md** (this file) - Complete usage guide
- **projet_ML (1).ipynb** - ML model training and validation
- **config.py** - All configuration constants
- **Code comments** - Inline documentation

---





