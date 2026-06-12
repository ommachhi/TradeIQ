from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler

from ml.common import make_forecast_frame, regression_metrics, smooth_forecast


WINDOW = 60


def _build_sequences(values: np.ndarray, horizon_days: int):
    X, y, baseline = [], [], []
    for start in range(len(values) - WINDOW - horizon_days + 1):
        end = start + WINDOW
        target_index = end + horizon_days - 1
        X.append(values[start:end])
        y.append(values[target_index])
        baseline.append(values[end - 1])
    return np.array(X), np.array(y), np.array(baseline)


def forecast(df: pd.DataFrame, horizon_days: int) -> dict:
    close = df["Close"].dropna().to_numpy(dtype=float)
    if len(close) < WINDOW + horizon_days + 30:
        raise ValueError("Not enough historical data to train the LSTM model.")

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(close.reshape(-1, 1)).flatten()
    X, y, baseline = _build_sequences(scaled, horizon_days)
    split = max(int(len(X) * 0.8), 20)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    baseline_test = baseline[split:]

    backend = "tensorflow"
    dependency_warning = None

    try:
        import tensorflow as tf  # type: ignore

        tf.random.set_seed(42)
        X_train_tf = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test_tf = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

        model = tf.keras.Sequential(
            [
                tf.keras.layers.Input(shape=(WINDOW, 1)),
                tf.keras.layers.LSTM(64, return_sequences=True),
                tf.keras.layers.Dropout(0.1),
                tf.keras.layers.LSTM(32),
                tf.keras.layers.Dense(16, activation="relu"),
                tf.keras.layers.Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
        ]
        validation_split = 0.1 if len(X_train_tf) >= 20 else 0.0
        fit_kwargs = {"epochs": 8, "batch_size": 32, "verbose": 0, "callbacks": callbacks}
        if validation_split:
            fit_kwargs["validation_split"] = validation_split
        model.fit(X_train_tf, y_train, **fit_kwargs)
        test_predictions_scaled = model.predict(X_test_tf, verbose=0).flatten() if len(X_test_tf) else np.array([])
        latest_sequence = scaled[-WINDOW:].reshape(1, WINDOW, 1)
        latest_prediction_scaled = float(model.predict(latest_sequence, verbose=0).flatten()[0])
    except Exception:
        backend = "mlp_fallback"
        dependency_warning = "TensorFlow is not installed in this environment; using a real scikit-learn fallback."
        model = MLPRegressor(hidden_layer_sizes=(128, 64), random_state=42, max_iter=500)
        model.fit(X_train, y_train)
        test_predictions_scaled = model.predict(X_test) if len(X_test) else np.array([])
        latest_prediction_scaled = float(model.predict(scaled[-WINDOW:].reshape(1, -1))[0])

    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten() if len(y_test) else np.array([])
    baseline_actual = scaler.inverse_transform(baseline_test.reshape(-1, 1)).flatten() if len(baseline_test) else np.array([])
    test_predictions = scaler.inverse_transform(np.asarray(test_predictions_scaled).reshape(-1, 1)).flatten() if len(test_predictions_scaled) else np.array([])
    metrics = regression_metrics(y_test_actual, test_predictions, baseline_values=baseline_actual) if len(y_test_actual) else {
        "rmse": None,
        "mae": None,
        "r2": None,
        "accuracy": None,
    }

    target_price = float(scaler.inverse_transform(np.array([[latest_prediction_scaled]])).flatten()[0])
    current_price = float(close[-1])
    forecast_values = smooth_forecast(current_price, target_price, horizon_days)

    result = {
        "model": "LSTM",
        "backend": backend,
        "current_price": current_price,
        "predicted_price": float(forecast_values[-1]),
        "forecast": make_forecast_frame(df, forecast_values),
        "metrics": metrics,
    }
    if dependency_warning:
        result["dependency_warning"] = dependency_warning
    return result
