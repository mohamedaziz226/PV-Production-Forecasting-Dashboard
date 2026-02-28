"""
Model Loading and Prediction Utilities
Loads the trained XGBoost model and handles predictions
"""
#model
import pandas as pd
import numpy as np
import pickle
import joblib
from typing import Dict, List, Tuple
from pathlib import Path
from config import FEATURE_COLUMNS_EXOGENOUS, FEATURE_COLUMNS_TIMESTAMP_ONLY

class ModelManager:
    """Manages model loading and predictions"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize model manager
        
        Args:
            model_path: Path to the trained model file
        """
        self.model = None
        self.scaler = None
        self.model_type = 'exogenous'  # Default to fine-tuned exogenous model
        
        if model_path:
            self.load_model(model_path)
        else:
            # Try default paths first
            for default_path in ['best_model_exogenous.pkl', 'project_model.pkl']:
                if Path(default_path).exists():
                    self.load_model(default_path)
                    if self.model is not None:
                        return
            # Fall back to notebook if files don't exist
            self._load_from_notebook()
    
    def _load_from_notebook(self):
        """
        Try to load model from notebook execution context
        This requires the notebook kernel to be running
        """
        try:
            # Try to get model from notebook variables
            import sys
            if 'notebook' in sys.modules:
                # Get the best_model_exogenous from notebook
                notebook = sys.modules['notebook']
                if hasattr(notebook, 'best_model_exogenous'):
                    self.model = notebook.best_model_exogenous
                    self.model_type = 'exogenous_finetuned'
                    print("[OK] Loaded fine-tuned exogenous model from notebook")
                    return
        except Exception as e:
            print(f"[INFO] Could not load from notebook: {e}")
        
        print("[WARN] Model not loaded. Will attempt to use a default model.")
    
    def load_model(self, model_path: str):
        """
        Load model from file
        
        Args:
            model_path: Path to model file
        """
        try:
            # Try joblib first (for sklearn/xgboost)
            self.model = joblib.load(model_path)
            self.model_type = 'exogenous_finetuned'
            print(f"[OK] Loaded fine-tuned exogenous model from {model_path}")
            return True
        except Exception as e:
            try:
                # Try pickle
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.model_type = 'exogenous_finetuned'
                print(f"[OK] Loaded fine-tuned exogenous model from {model_path}")
                return True
            except Exception as e2:
                print(f"[WARN] Could not load model from {model_path}: {e2}")
                self.model = None
                return False
    
    def prepare_features(self, weather_data: Dict) -> pd.DataFrame:
        """
        Prepare features for model prediction
        
        Args:
            weather_data: Weather data formatted for model (from WeatherDataFetcher.format_for_model)
        
        Returns:
            DataFrame with features in correct order
        """
        # Create DataFrame from the formatted weather data
        df = pd.DataFrame([weather_data])
        
        # Select only the columns needed for the model
        feature_cols = FEATURE_COLUMNS_EXOGENOUS
        
        # Ensure all required columns exist with 0 as default
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0
        
        # Return only the required columns in the correct order
        return df[feature_cols].astype({
            'hour': 'int32',
            'Vitesse vent(m/s)': 'float32',
            'Humidité ambiante(%RH)': 'float32',
            'Température ambiante(℃)': 'float32',
            'Irradiation transitoire pente(W/㎡)': 'float32',
            'day_Friday': 'int32',
            'day_Monday': 'int32',
            'day_Saturday': 'int32',
            'day_Sunday': 'int32',
            'day_Thursday': 'int32',
            'day_Tuesday': 'int32',
            'day_Wednesday': 'int32'
        })
    
    def predict(self, weather_data: Dict) -> float:
        """
        Make a prediction based on weather data
        
        Args:
            weather_data: Weather data formatted for model
        
        Returns:
            Predicted power output in kW
        """
        if self.model is None:
            print("⚠ Model not loaded. Returning dummy prediction.")
            return 0.5
        
        try:
            X = self.prepare_features(weather_data)
            prediction = self.model.predict(X)[0]
            return max(0, float(prediction))  # Ensure non-negative
        except Exception as e:
            print(f"✗ Prediction error: {e}")
            return 0.0
    
    def predict_batch(self, weather_data_list: List[Dict]) -> List[float]:
        """
        Make predictions for multiple time periods
        
        Args:
            weather_data_list: List of weather data dictionaries
        
        Returns:
            List of predictions
        """
        predictions = []
        for weather_data in weather_data_list:
            predictions.append(self.predict(weather_data))
        return predictions


def create_mock_model():
    """
    Create a simple mock model for demonstration when real model is not available
    
    Returns:
        Simple sklearn estimator
    """
    from sklearn.ensemble import RandomForestRegressor
    
    # Create a simple model for demo purposes
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    
    # Train on dummy data
    X_dummy = np.random.randn(100, 12)  # 12 features
    y_dummy = np.random.uniform(0, 2, 100)  # Power 0-2 kW
    
    model.fit(X_dummy, y_dummy)
    return model


class DemoPredictionEngine:
    """Simple prediction engine for demo without requiring actual model"""
    
    @staticmethod
    def predict(weather_data: Dict) -> float:
        """
        Make prediction based on irradiation and weather
        
        Args:
            weather_data: Weather data with irradiation estimate
        
        Returns:
            Predicted power in kW
        """
        irradiation = weather_data.get('irradiation', 0)
        temperature = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 60)
        
        # Simple heuristic model
        # Irradiation has strongest effect
        power = irradiation / 400  # Normalize irradiation
        
        # Temperature effect (optimal around 25°C)
        temp_factor = 1 - abs(temperature - 25) / 100
        power *= max(0.3, temp_factor)
        
        # Humidity slightly reduces efficiency
        humidity_factor = 1 - (humidity / 100) * 0.1
        power *= humidity_factor
        
        return max(0, min(power, 2.0))  # Cap at 2 kW
    
    @staticmethod
    def predict_batch(weather_data_list: List[Dict]) -> List[float]:
        """
        Make batch predictions
        
        Args:
            weather_data_list: List of weather dictionaries
        
        Returns:
            List of predictions
        """
        return [DemoPredictionEngine.predict(data) for data in weather_data_list]
