import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

df = pd.read_csv('Datasets/TradeIQ_stock_data.csv')
X = df[['Open', 'High', 'Low', 'Volume']].fillna(df[['Open', 'High', 'Low', 'Volume']].mean())
y = df['Close'].fillna(df['Close'].mean())

_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with open('tradeiq_backend/model.pkl', 'rb') as f:
    loaded = pickle.load(f)

model = None
feature_scaler = None
target_scaler = None

if isinstance(loaded, tuple):
    if len(loaded) == 3:
        model, feature_scaler, target_scaler = loaded
    elif len(loaded) == 2:
        model, feature_scaler = loaded
    elif len(loaded) > 0:
        model = loaded[0]
elif isinstance(loaded, dict):
    model = loaded.get('model')
    feature_scaler = loaded.get('feature_scaler') or loaded.get('scaler')
    target_scaler = loaded.get('target_scaler')
else:
    model = loaded

X_eval = X_test
if feature_scaler is not None:
    X_eval = feature_scaler.transform(X_eval)

pred = model.predict(X_eval)
if target_scaler is not None:
    pred = target_scaler.inverse_transform(np.array(pred).reshape(-1, 1)).ravel()

rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
mae = float(mean_absolute_error(y_test, pred))
r2 = float(r2_score(y_test, pred))

denom = np.where(np.abs(y_test.values) < 1e-8, 1e-8, np.abs(y_test.values))
mape = float(np.mean(np.abs((y_test.values - pred) / denom)) * 100)
acc = max(0.0, 100.0 - mape)

print(f'R2={r2:.4f}')
print(f'RMSE={rmse:.4f}')
print(f'MAE={mae:.4f}')
print(f'MAPE={mape:.4f}%')
print(f'PseudoAccuracy={acc:.4f}%')
