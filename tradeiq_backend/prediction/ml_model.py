"""
Machine Learning Model Management Module

This module handles loading, using, and retraining the ML model for stock price predictions.
"""

import pickle
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from datetime import datetime


class StockPricePredictor:
    """
    Load and use the pre-trained Random Forest model for stock price predictions
    """

    def __init__(self):
        """Initialize and load the model from pickle file"""
        self.model = None
        self.scaler = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')
        self.load_model()

    def load_model(self):
        """
        Load the model and scaler from pickle files
        Raises: FileNotFoundError if model.pkl doesn't exist
        """
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✓ Model loaded successfully from {self.model_path}")

            # Try to load scaler if it exists
            if os.path.exists(self.scaler_path):
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print(f"✓ Scaler loaded successfully from {self.scaler_path}")
            else:
                print("⚠ Scaler not found, will work without scaling")

        except FileNotFoundError:
            print(f"✗ Model file not found: {self.model_path}")
            raise
        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            print("Attempting to retrain model due to compatibility issues...")
            try:
                self.train_model()
                print("✓ Model retrained successfully")
            except Exception as retrain_error:
                print(f"✗ Failed to retrain model: {str(retrain_error)}")
                raise e  # Raise original error

    def predict(self, open_price, high_price, low_price, volume, ma_5=None, ma_10=None, ma_20=None, daily_return=None):
        """
        Predict stock price based on input features

        Args:
            open_price (float): Opening price of the stock
            high_price (float): Highest price of the stock
            low_price (float): Lowest price of the stock
            volume (int): Trading volume
            ma_5 (float): 5-day moving average
            ma_10 (float): 10-day moving average
            ma_20 (float): 20-day moving average
            daily_return (float): Daily return percentage

        Returns:
            dict: Prediction results with price, recommendation, and metrics
        """
        if self.model is None:
            raise ValueError("Model not loaded. Please initialize the predictor properly.")

        try:
            # Prepare features in the same order as training
            features = [open_price, high_price, low_price, volume]

            # Add technical indicators if provided
            if ma_5 is not None:
                features.append(ma_5)
            if ma_10 is not None:
                features.append(ma_10)
            if ma_20 is not None:
                features.append(ma_20)
            if daily_return is not None:
                features.append(daily_return)

            features = np.array([features])

            # Apply scaling if scaler exists
            if self.scaler:
                features = self.scaler.transform(features)

            # Make prediction
            prediction = self.model.predict(features)[0]
            predicted_price = round(float(prediction), 2)

            # Determine recommendation based on predicted vs open price
            if predicted_price > open_price * 1.02:  # 2% threshold for BUY
                recommendation = "BUY"
            elif predicted_price < open_price * 0.98:  # 2% threshold for SELL
                recommendation = "SELL"
            else:
                recommendation = "HOLD"

            return {
                'predicted_price': predicted_price,
                'recommendation': recommendation,
                'input_features': {
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'volume': volume,
                    'ma_5': ma_5,
                    'ma_10': ma_10,
                    'ma_20': ma_20,
                    'daily_return': daily_return
                }
            }

        except Exception as e:
            print(f"✗ Error during prediction: {str(e)}")
            raise ValueError(f"Prediction failed: {str(e)}")

    @staticmethod
    def train_model(dataset_path, model_name="Trained Model"):
        """
        Train a new model from dataset

        Args:
            dataset_path (str): Path to CSV dataset
            model_name (str): Name for the trained model

        Returns:
            dict: Training results with metrics and model info
        """
        try:
            # Load dataset
            df = pd.read_csv(dataset_path)
            print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            # Prepare features and target
            feature_columns = ['Open', 'High', 'Low', 'Volume']
            target_column = 'Close'

            # Check if required columns exist
            if not all(col in df.columns for col in feature_columns + [target_column]):
                raise ValueError(f"Dataset must contain columns: {feature_columns + [target_column]}")

            # Add technical indicators
            df['MA_5'] = df['Close'].rolling(window=5).mean()
            df['MA_10'] = df['Close'].rolling(window=10).mean()
            df['MA_20'] = df['Close'].rolling(window=20).mean()
            df['Daily_Return'] = df['Close'].pct_change()

            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)

            # Extended feature set
            extended_features = feature_columns + ['MA_5', 'MA_10', 'MA_20', 'Daily_Return']
            X = df[extended_features]
            y = df[target_column]

            print(f"Features: {extended_features}")
            print(f"Training data shape: {X.shape}")

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train Random Forest model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )

            model.fit(X_train_scaled, y_train)

            # Evaluate model
            train_predictions = model.predict(X_train_scaled)
            test_predictions = model.predict(X_test_scaled)

            train_rmse = np.sqrt(mean_squared_error(y_train, train_predictions))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
            train_r2 = r2_score(y_train, train_predictions)
            test_r2 = r2_score(y_test, test_predictions)

            print(f"Training RMSE: {train_rmse:.4f}, R²: {train_r2:.4f}")
            print(f"Testing RMSE: {test_rmse:.4f}, R²: {test_r2:.4f}")

            # Save model and scaler
            model_dir = os.path.dirname(os.path.dirname(__file__))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            model_filename = f"model_{timestamp}.pkl"
            scaler_filename = f"scaler_{timestamp}.pkl"

            model_path = os.path.join(model_dir, 'prediction', model_filename)
            scaler_path = os.path.join(model_dir, 'prediction', scaler_filename)

            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)

            return {
                'model_name': model_name,
                'model_path': model_filename,
                'scaler_path': scaler_filename,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'feature_count': len(extended_features),
                'training_samples': len(X_train),
                'testing_samples': len(X_test)
            }

        except Exception as e:
            print(f"✗ Error during training: {str(e)}")
            raise ValueError(f"Training failed: {str(e)}")


# Create a global instance of the predictor
try:
    stock_predictor = StockPricePredictor()
except Exception as e:
    print(f"Warning: Could not initialize stock predictor: {str(e)}")
    stock_predictor = None
