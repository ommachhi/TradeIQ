"""
Train and save the ML model for stock price prediction
This script trains a Random Forest model on historical stock data
and saves it as model.pkl
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Load the dataset
df = pd.read_csv('Datasets/TradeIQ_stock_data.csv')

print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Prepare features and target
# We'll predict 'Close' price based on 'Open', 'High', 'Low', 'Volume'
features = ['Open', 'High', 'Low', 'Volume']
target = 'Close'

# Check if all required columns exist
if all(col in df.columns for col in features + [target]):
    X = df[features].copy()
    y = df[target].copy()
    
    # Handle missing values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())
    
    print(f"\nTraining data shape: {X.shape}")
    print(f"Target data shape: {y.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train Random Forest model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"\nModel Performance:")
    print(f"Training R² Score: {train_score:.4f}")
    print(f"Testing R² Score: {test_score:.4f}")
    
    # Save the model
    with open('tradeiq_backend/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("\n✓ Model saved successfully as 'tradeiq_backend/model.pkl'")
else:
    print("Error: Required columns not found in dataset")
    print("Available columns:", df.columns.tolist())
