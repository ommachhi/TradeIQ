from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.common import make_forecast_frame, regression_metrics, smooth_forecast
from ml.indicators import feature_frame


def forecast(df: pd.DataFrame, horizon_days: int) -> dict:
    dataset, feature_columns = feature_frame(df, horizon=horizon_days)
    if dataset.empty or len(dataset) < 60:
        raise ValueError("Not enough historical data to train the linear regression model.")

    split = max(int(len(dataset) * 0.8), 30)
    train = dataset.iloc[:split]
    test = dataset.iloc[split:]

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", LinearRegression()),
        ]
    )
    model.fit(train[feature_columns], train["target_price"])

    test_predictions = model.predict(test[feature_columns]) if not test.empty else np.array([])
    metrics = regression_metrics(
        test["target_price"],
        test_predictions,
        baseline_values=test["Close"],
    ) if not test.empty else {"rmse": None, "mae": None, "r2": None, "accuracy": None}

    latest_features = dataset.iloc[[-1]][feature_columns]
    target_price = float(model.predict(latest_features)[0])
    current_price = float(dataset.iloc[-1]["Close"])
    forecast_values = smooth_forecast(current_price, target_price, horizon_days)

    return {
        "model": "Linear Regression",
        "current_price": current_price,
        "predicted_price": float(forecast_values[-1]),
        "forecast": make_forecast_frame(df, forecast_values),
        "metrics": metrics,
    }
