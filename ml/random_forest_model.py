from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from ml.common import make_forecast_frame, regression_metrics, smooth_forecast
from ml.indicators import feature_frame


def forecast(df: pd.DataFrame, horizon_days: int) -> dict:
    dataset, feature_columns = feature_frame(df, horizon=horizon_days)
    if dataset.empty or len(dataset) < 80:
        raise ValueError("Not enough historical data to train the Random Forest model.")

    split = max(int(len(dataset) * 0.8), 40)
    train = dataset.iloc[:split]
    test = dataset.iloc[split:]

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=8,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[feature_columns], train["target_direction"])

    probability_index = 1 if len(model.classes_) > 1 else 0
    probability_test = model.predict_proba(test[feature_columns])[:, probability_index] if not test.empty else np.array([])
    predicted_direction = (probability_test >= 0.5).astype(int) if not test.empty else np.array([])
    accuracy = float(accuracy_score(test["target_direction"], predicted_direction) * 100) if not test.empty else None

    avg_abs_move = float(dataset["Return_1"].abs().tail(30).mean())
    if avg_abs_move <= 0:
        avg_abs_move = 0.01

    current_prices = test["Close"].to_numpy(dtype=float) if not test.empty else np.array([])
    predicted_returns = np.clip((probability_test - 0.5) * 2 * avg_abs_move * horizon_days, -0.2, 0.2)
    test_price_predictions = current_prices * (1 + predicted_returns) if not test.empty else np.array([])
    metrics = regression_metrics(
        test["target_price"],
        test_price_predictions,
        baseline_values=test["Close"],
    ) if not test.empty else {"rmse": None, "mae": None, "r2": None, "accuracy": None}
    metrics["accuracy"] = accuracy

    latest_features = dataset.iloc[[-1]][feature_columns]
    latest_prob = float(model.predict_proba(latest_features)[:, probability_index][0])
    current_price = float(dataset.iloc[-1]["Close"])
    expected_return = np.clip((latest_prob - 0.5) * 2 * avg_abs_move * horizon_days, -0.2, 0.2)
    target_price = current_price * (1 + expected_return)
    forecast_values = smooth_forecast(current_price, target_price, horizon_days)

    return {
        "model": "Random Forest",
        "backend": "random_forest",
        "current_price": current_price,
        "predicted_price": float(forecast_values[-1]),
        "forecast": make_forecast_frame(df, forecast_values),
        "metrics": metrics,
    }