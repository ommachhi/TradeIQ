"""
Train and save the ML model for stock price prediction with proper feature scaling.
This version saves both the Random Forest model AND the StandardScaler.
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load the dataset
df = pd.read_csv('Datasets/TradeIQ_stock_data.csv')

print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Prepare features and target
features_cols = ['Open', 'High', 'Low', 'Volume']
target_col = 'Close'

# Check if all required columns exist
if all(col in df.columns for col in features_cols + [target_col]):
    X = df[features_cols].copy()
    y = df[target_col].copy()
    
    # Handle missing values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())
    
    print(f"\nTraining data shape: {X.shape}")
    print(f"Target data shape: {y.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Feature scaler for model input columns
    feature_scaler = StandardScaler()
    X_train_scaled = feature_scaler.fit_transform(X_train)
    X_test_scaled = feature_scaler.transform(X_test)

    # Target scaler for Close column only
    target_scaler = StandardScaler()
    y_train_scaled = target_scaler.fit_transform(y_train.values.reshape(-1, 1)).ravel()
    y_test_scaled = target_scaler.transform(y_test.values.reshape(-1, 1)).ravel()
    
    # Train Random Forest model on scaled features
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train_scaled)
    
    # Evaluate model on both scaled datasets
    train_pred_scaled = model.predict(X_train_scaled).reshape(-1, 1)
    test_pred_scaled = model.predict(X_test_scaled).reshape(-1, 1)
    train_pred = target_scaler.inverse_transform(train_pred_scaled).ravel()
    test_pred = target_scaler.inverse_transform(test_pred_scaled).ravel()
    
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    print(f"\nModel Performance:")
    print(f"Training RMSE: {train_rmse:.4f}")
    print(f"Testing RMSE: {test_rmse:.4f}")
    print(f"Training R² Score: {train_r2:.4f}")
    print(f"Testing R² Score: {test_r2:.4f}")
    
    # Save model + feature scaler + target scaler as tuple
    model_path = 'tradeiq_backend/model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump((model, feature_scaler, target_scaler), f)
    
    print(f"\n[SUCCESS] Model and scaler saved successfully to '{model_path}'")
    print("  - Model type: RandomForestRegressor")
    print("  - Feature scaler: StandardScaler")
    print("  - Target scaler (Close only): StandardScaler")
    print("  - Features: [Open, High, Low, Volume]")
    print("  - Target: Close")
else:
    print("Error: Required columns not found in dataset")
    print("Available columns:", df.columns.tolist())
