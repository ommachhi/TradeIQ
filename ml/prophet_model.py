from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from ml.common import future_business_index, regression_metrics


def _fallback_prophet_like(train: pd.DataFrame, future_dates: pd.DatetimeIndex) -> pd.DataFrame:
    frame = train.copy()
    frame["t"] = np.arange(len(frame), dtype=float)
    frame["sin_week"] = np.sin(2 * np.pi * frame["t"] / 5)
    frame["cos_week"] = np.cos(2 * np.pi * frame["t"] / 5)

    model = LinearRegression()
    model.fit(frame[["t", "sin_week", "cos_week"]], frame["y"])

    future_t = np.arange(len(frame), len(frame) + len(future_dates), dtype=float)
    future_frame = pd.DataFrame(
        {
            "ds": future_dates,
            "t": future_t,
            "sin_week": np.sin(2 * np.pi * future_t / 5),
            "cos_week": np.cos(2 * np.pi * future_t / 5),
        }
    )
    future_frame["yhat"] = model.predict(future_frame[["t", "sin_week", "cos_week"]])
    residual_std = float((frame["y"] - model.predict(frame[["t", "sin_week", "cos_week"]])).std())
    future_frame["yhat_lower"] = future_frame["yhat"] - 1.96 * residual_std
    future_frame["yhat_upper"] = future_frame["yhat"] + 1.96 * residual_std
    return future_frame


def forecast(df: pd.DataFrame, horizon_days: int) -> dict:
    history = df.reset_index()[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})
    history["ds"] = pd.to_datetime(history["ds"]).dt.tz_localize(None)
    if len(history) < 80:
        raise ValueError("Not enough historical data to train the Prophet model.")

    split = max(int(len(history) * 0.8), 40)
    train = history.iloc[:split].copy()
    test = history.iloc[split:].copy()

    backend = "prophet"
    forecast_frame = None

    try:
        from prophet import Prophet  # type: ignore

        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
        )
        model.fit(train)
        test_future = pd.DataFrame({"ds": test["ds"]})
        test_predictions = model.predict(test_future)
        metrics = regression_metrics(test["y"], test_predictions["yhat"], baseline_values=test["y"].shift(1).bfill())

        future = model.make_future_dataframe(periods=horizon_days, freq="B")
        forecast_frame = model.predict(future).tail(horizon_days)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    except Exception:
        backend = "linear_seasonal_fallback"
        test_predictions = _fallback_prophet_like(train, test["ds"])
        metrics = regression_metrics(test["y"], test_predictions["yhat"], baseline_values=test["y"].shift(1).bfill())
        future_dates = future_business_index(df.index, horizon_days)
        forecast_frame = _fallback_prophet_like(history, future_dates)

    forecast_frame = forecast_frame.copy()
    forecast_frame["Date"] = pd.to_datetime(forecast_frame["ds"])
    forecast_frame["Predicted"] = forecast_frame["yhat"]
    forecast_frame["Lower"] = forecast_frame["yhat_lower"]
    forecast_frame["Upper"] = forecast_frame["yhat_upper"]
    forecast_frame = forecast_frame.set_index("Date")[["Predicted", "Lower", "Upper"]]

    return {
        "model": "Prophet",
        "backend": backend,
        "current_price": float(history["y"].iloc[-1]),
        "predicted_price": float(forecast_frame["Predicted"].iloc[-1]),
        "forecast": forecast_frame,
        "metrics": metrics,
    }
