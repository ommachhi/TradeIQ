from __future__ import annotations

import pandas as pd

from ml.common import horizon_days
from ml.linear_model import forecast as linear_forecast
from ml.lstm_model import forecast as lstm_forecast
from ml.prophet_model import forecast as prophet_forecast
from ml.random_forest_model import forecast as random_forest_forecast
from ml.xgboost_model import forecast as xgboost_forecast
from utils.helpers import annualized_volatility, compute_signal, compute_trend, confidence_from_metrics


MODEL_MAP = {
    "Random Forest": random_forest_forecast,
    "LSTM": lstm_forecast,
    "Prophet": prophet_forecast,
    "XGBoost": xgboost_forecast,
    "LinReg": linear_forecast,
}


def _model_score(result: dict) -> tuple[float, float]:
    metrics = result.get("metrics") or {}
    accuracy = metrics.get("accuracy")
    r2 = metrics.get("r2")
    return (
        float(accuracy) if accuracy is not None else -1.0,
        float(r2) if r2 is not None else -1.0,
    )


def _best_prediction(df: pd.DataFrame, steps: int) -> dict:
    candidates: list[dict] = []
    for model_name in MODEL_MAP:
        try:
            candidates.append(MODEL_MAP[model_name](df, steps))
        except Exception:
            continue
    if not candidates:
        raise ValueError("No prediction model could produce a forecast.")
    candidates.sort(key=_model_score, reverse=True)
    return candidates[0]


def run_prediction(df: pd.DataFrame, model_name: str, horizon_label: str) -> dict:
    steps = horizon_days(horizon_label)
    if model_name == "Best Accuracy":
        result = _best_prediction(df, steps)
    elif model_name not in MODEL_MAP:
        raise ValueError(f"Unsupported model: {model_name}")
    else:
        result = MODEL_MAP[model_name](df, steps)
    current_price = float(result["current_price"])
    predicted_price = float(result["predicted_price"])
    metrics = result.get("metrics") or {}
    confidence = confidence_from_metrics(
        metrics.get("r2"),
        (metrics.get("rmse") or 0.0) / current_price if current_price else None,
    )

    result["horizon_days"] = steps
    result["confidence"] = confidence
    result["signal"] = compute_signal(current_price, predicted_price)
    result["trend"] = compute_trend(current_price, predicted_price)
    result["volatility"] = annualized_volatility(df["Close"])
    return result


def compare_models(df: pd.DataFrame, horizon_label: str) -> tuple[list[dict], list[str]]:
    comparisons: list[dict] = []
    warnings: list[str] = []

    for model_name in MODEL_MAP:
        try:
            result = run_prediction(df, model_name, horizon_label)
            metrics = result["metrics"]
            comparisons.append(
                {
                    "Model": result["model"],
                    "RMSE": metrics.get("rmse"),
                    "MAE": metrics.get("mae"),
                    "R²": metrics.get("r2"),
                    "Accuracy": metrics.get("accuracy"),
                    "Confidence": result["confidence"],
                }
            )
            if result.get("dependency_warning"):
                warnings.append(f"{result['model']}: {result['dependency_warning']}")
        except Exception as exc:
            warnings.append(f"{model_name}: {exc}")

    return comparisons, warnings
