# config
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from config import WEATHER_API_KEY, WEATHER_API_BASE_URL, WEATHER_FORECAST_URL

class WeatherDataFetcher:
    """Fetch and process weather data from OpenWeatherMap API"""
    
    def __init__(self, api_key: str = WEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = WEATHER_API_BASE_URL
        self.forecast_url = WEATHER_FORECAST_URL
    
    def get_current_weather(self, city: str, country_code: str = "") -> Dict:
        """
        Fetch current weather for a location
        
        Args:
            city: City name
            country_code: ISO 3166 country code (optional)
        
        Returns:
            Dictionary with weather data
        """
        location = f"{city},{country_code}" if country_code else city
        
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'status': 'success',
                'data': {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'description': data['weather'][0]['description'],
                    'condition': data['weather'][0]['main'],
                    'pressure': data['main']['pressure'],
                    'clouds': data['clouds']['all'],
                    'timestamp': datetime.fromtimestamp(data['dt'])
                }
            }
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_forecast(self, city: str, country_code: str = "", hours: int = 48) -> Dict:
        """
        Fetch weather forecast for next hours
        
        Args:
            city: City name
            country_code: ISO 3166 country code (optional)
            hours: Number of hours to forecast (5 days max with free tier)
        
        Returns:
            Dictionary with forecast data
        """
        location = f"{city},{country_code}" if country_code else city
        
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': min(hours // 3, 40)  # API returns 3-hour intervals
        }
        
        try:
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_data = []
            for item in data['list']:
                forecast_data.append({
                    'timestamp': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                    'description': item['weather'][0]['description'],
                    'condition': item['weather'][0]['main'],
                    'clouds': item['clouds']['all'],
                    'rain': item.get('rain', {}).get('3h', 0),
                    'visibility': item.get('visibility', 10000)
                })
            
            return {
                'status': 'success',
                'data': forecast_data
            }
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': str(e)}
    
    def estimate_irradiation(self, cloud_percentage: float, hour: int) -> float:
        """
        Estimate irradiation based on cloud coverage and hour of day
        This is a simplified model - in production use a proper solar irradiation model
        
        Args:
            cloud_percentage: Cloud coverage 0-100%
            hour: Hour of day (0-23)
        
        Returns:
            Estimated irradiation in W/m²
        """
        # Base irradiation curve for clear sky (simplified)
        if hour < 6 or hour > 18:
            base_irradiation = 0
        elif 6 <= hour < 9:
            base_irradiation = (hour - 6) * 100
        elif 9 <= hour < 12:
            base_irradiation = 300 + (hour - 9) * 100
        elif 12 <= hour < 15:
            base_irradiation = 600 + (hour - 12) * 50
        elif 15 <= hour < 18:
            base_irradiation = 750 - (hour - 15) * 100
        else:
            base_irradiation = 0
        
        # Apply cloud reduction factor
        cloud_reduction = 1 - (cloud_percentage / 100) * 0.9
        estimated = base_irradiation * max(cloud_reduction, 0)
        
        return max(estimated, 0)
    
    def format_for_model(self, weather_data: Dict) -> Dict:
        """
        Format weather data to match model input columns
        
        Args:
            weather_data: Weather data dictionary from API
        
        Returns:
            Dictionary with columns matching the ML model
        """
        timestamp = weather_data['timestamp']
        
        # Calculate hour of day
        hour = timestamp.hour
        
        # One-hot encode day of week
        day_name = timestamp.strftime('%A')
        day_columns = {
            'day_Friday': 1 if day_name == 'Friday' else 0,
            'day_Monday': 1 if day_name == 'Monday' else 0,
            'day_Saturday': 1 if day_name == 'Saturday' else 0,
            'day_Sunday': 1 if day_name == 'Sunday' else 0,
            'day_Thursday': 1 if day_name == 'Thursday' else 0,
            'day_Tuesday': 1 if day_name == 'Tuesday' else 0,
            'day_Wednesday': 1 if day_name == 'Wednesday' else 0,
        }
        
        # Estimate irradiation
        irradiation = self.estimate_irradiation(
            weather_data['clouds'],
            hour
        )
        
        formatted_data = {
            'hour': hour,
            'Vitesse vent(m/s)': weather_data['wind_speed'],
            'Humidité ambiante(%RH)': weather_data['humidity'],
            'Température ambiante(℃)': weather_data['temperature'],
            'Irradiation transitoire pente(W/㎡)': irradiation,
            **day_columns,
            'timestamp': timestamp,
            'weather_condition': weather_data['condition'],
            'cloud_coverage': weather_data['clouds']
        }
        
        return formatted_data

def get_weather_data(city: str, country_code: str = "") -> Tuple[Dict, Dict]:
    """
    Convenience function to fetch current weather and forecast
    
    Args:
        city: City name
        country_code: ISO 3166 country code (optional)
    
    Returns:
        Tuple of (current_weather, forecast)
    """
    fetcher = WeatherDataFetcher()
    current = fetcher.get_current_weather(city, country_code)
    forecast = fetcher.get_forecast(city, country_code)
    return current, forecast
