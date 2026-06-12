from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from utils.constants import PREDICTION_PERIODS


def horizon_days(label: str) -> int:
    return PREDICTION_PERIODS.get(label, 1)


def future_business_index(history_index: pd.Index, steps: int) -> pd.DatetimeIndex:
    last_date = pd.to_datetime(history_index[-1])
    return pd.bdate_range(last_date + pd.tseries.offsets.BDay(1), periods=steps)


def regression_metrics(y_true, y_pred, baseline_values=None) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else 0.0,
    }
    if baseline_values is not None:
        baseline = np.asarray(baseline_values, dtype=float)
        actual_direction = np.sign(y_true - baseline)
        pred_direction = np.sign(y_pred - baseline)
        metrics["accuracy"] = float((actual_direction == pred_direction).mean() * 100)
    else:
        metrics["accuracy"] = None
    return metrics


def make_forecast_frame(history: pd.DataFrame, forecast_values: np.ndarray) -> pd.DataFrame:
    forecast_index = future_business_index(history.index, len(forecast_values))
    return pd.DataFrame({"Date": forecast_index, "Predicted": forecast_values}).set_index("Date")


def smooth_forecast(current_price: float, target_price: float, steps: int) -> np.ndarray:
    if steps <= 1:
        return np.array([target_price], dtype=float)
    return np.linspace(current_price, target_price, steps + 1, dtype=float)[1:]
