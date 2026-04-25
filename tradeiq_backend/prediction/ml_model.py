"""
Machine Learning Model Management Module

This module handles loading, using, and retraining the ML model for stock price predictions.
"""

import os
import pickle
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


class StockPricePredictor:
    """
    Load and use the pre-trained Random Forest model for stock price predictions.
    """

    def __init__(self):
        """Initialize and load the model from pickle file."""
        self.model = None
        self.scaler = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')
        self.default_dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TradeIQ_stock_data.csv')
        self.load_model()

    def load_model(self):
        """
        Load the model and scaler from pickle files.

        Raises:
            FileNotFoundError: if model.pkl doesn't exist.
        """
        try:
            self.model = joblib.load(self.model_path)
            print(f"Model loaded successfully from {self.model_path}")

            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print(f"Scaler loaded successfully from {self.scaler_path}")
            else:
                print("Scaler not found, will work without scaling")

        except FileNotFoundError:
            print(f"Model file not found: {self.model_path}")
            raise
        except Exception as exc:
            print(f"Error loading model: {exc}")
            print("Attempting to retrain model due to compatibility issues...")
            try:
                if not os.path.exists(self.default_dataset_path):
                    raise FileNotFoundError(f"Default dataset not found: {self.default_dataset_path}")
                self.train_model(self.default_dataset_path, "TradeIQ_RF_v2")
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path) if os.path.exists(self.scaler_path) else None
                print("Model retrained successfully")
            except Exception as retrain_error:
                print(f"Failed to retrain model: {retrain_error}")
                raise exc

    def predict(self, open_price, high_price, low_price, volume, ma_5=None, ma_10=None, ma_20=None, daily_return=None):
        """
        Predict stock price based on input features.

        Args:
            open_price (float): Opening price of the stock.
            high_price (float): Highest price of the stock.
            low_price (float): Lowest price of the stock.
            volume (int): Trading volume.
            ma_5 (float): 5-day moving average.
            ma_10 (float): 10-day moving average.
            ma_20 (float): 20-day moving average.
            daily_return (float): Daily return percentage.

        Returns:
            dict: Prediction results with price, recommendation, and metrics.
        """
        if self.model is None:
            raise ValueError("Model not loaded. Please initialize the predictor properly.")

        try:
            features = [open_price, high_price, low_price, volume]

            features = np.array([features])

            if self.scaler:
                features = self.scaler.transform(features)

            prediction = self.model.predict(features)[0]
            predicted_price = round(float(prediction), 2)

            if predicted_price > open_price * 1.02:
                recommendation = "BUY"
            elif predicted_price < open_price * 0.98:
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
                    'daily_return': daily_return,
                },
            }

        except Exception as exc:
            print(f"Error during prediction: {exc}")
            raise ValueError(f"Prediction failed: {exc}")

    @staticmethod
    def train_model(dataset_path, model_name="Trained Model"):
        """
        Train a new model from dataset.

        Args:
            dataset_path (str): Path to CSV dataset.
            model_name (str): Name for the trained model.

        Returns:
            dict: Training results with metrics and model info.
        """
        try:
            df = pd.read_csv(dataset_path)
            print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.sort_values('Date', na_position='last')

            df = df.reset_index(drop=True)

            # Train only on same-day market inputs so retraining does not leak
            # target-derived indicators such as rolling close averages.
            feature_columns = ['Open', 'High', 'Low', 'Volume']
            target_column = 'Close'

            if not all(col in df.columns for col in feature_columns + [target_column]):
                raise ValueError(f"Dataset must contain columns: {feature_columns + [target_column]}")

            df = df.dropna(subset=feature_columns + [target_column]).copy()
            if len(df) < 30:
                raise ValueError("Dataset must contain at least 30 clean rows for retraining")

            x_data = df[feature_columns].astype(float)
            y_data = df[target_column].astype(float)

            print(f"Features: {feature_columns}")
            print(f"Training data shape: {x_data.shape}")

            # Chronological split avoids look-ahead bias for time-series data.
            split_index = max(int(len(df) * 0.8), 1)
            if split_index >= len(df):
                split_index = len(df) - 1
            if split_index < 1 or len(df) - split_index < 1:
                raise ValueError("Dataset split failed. Add more historical rows and try again.")

            x_train, x_test = x_data.iloc[:split_index], x_data.iloc[split_index:]
            y_train, y_test = y_data.iloc[:split_index], y_data.iloc[split_index:]

            scaler = StandardScaler()
            x_train_scaled = scaler.fit_transform(x_train)
            x_test_scaled = scaler.transform(x_test)

            model = RandomForestRegressor(
                n_estimators=250,
                max_depth=12,
                min_samples_split=12,
                min_samples_leaf=6,
                max_features='sqrt',
                bootstrap=True,
                random_state=42,
                n_jobs=1,
            )

            model.fit(x_train_scaled, y_train)

            train_predictions = model.predict(x_train_scaled)
            test_predictions = model.predict(x_test_scaled)

            train_rmse = np.sqrt(mean_squared_error(y_train, train_predictions))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
            train_r2 = r2_score(y_train, train_predictions)
            test_r2 = r2_score(y_test, test_predictions)
            overfit_gap = float(train_r2 - test_r2)

            print(f"Training RMSE: {train_rmse:.4f}, R2: {train_r2:.4f}")
            print(f"Testing RMSE: {test_rmse:.4f}, R2: {test_r2:.4f}")

            model_dir = os.path.dirname(os.path.dirname(__file__))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            model_filename = f"model_{timestamp}.pkl"
            scaler_filename = f"scaler_{timestamp}.pkl"

            model_path = os.path.join(model_dir, 'prediction', model_filename)
            scaler_path = os.path.join(model_dir, 'prediction', scaler_filename)
            active_prediction_model_path = os.path.join(model_dir, 'prediction', 'model.pkl')
            active_prediction_scaler_path = os.path.join(model_dir, 'prediction', 'scaler.pkl')
            active_runtime_model_path = os.path.join(model_dir, 'model.pkl')

            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            joblib.dump(model, active_prediction_model_path)
            joblib.dump(scaler, active_prediction_scaler_path)

            with open(active_runtime_model_path, 'wb') as runtime_bundle:
                pickle.dump((model, scaler, None), runtime_bundle)

            return {
                'model_name': model_name,
                'model_path': model_filename,
                'scaler_path': scaler_filename,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'overfit_gap': overfit_gap,
                'feature_count': len(feature_columns),
                'training_samples': len(x_train),
                'testing_samples': len(x_test),
            }

        except Exception as exc:
            print(f"Error during training: {exc}")
            raise ValueError(f"Training failed: {exc}")


try:
    stock_predictor = StockPricePredictor()
except Exception as exc:
    print(f"Warning: Could not initialize stock predictor: {exc}")
    stock_predictor = None
