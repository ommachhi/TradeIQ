"""
Prediction helper that loads a trained model and computes next-day price and trend.
"""
import os
import pickle
from datetime import datetime

import yfinance as yf
import numpy as np

# simple cache so model is loaded once
_model = None
_scaler = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model.pkl')


def _load_model():
    global _model, _scaler
    if _model is not None or _scaler is not None:
        return

    try:
        with open(MODEL_PATH, 'rb') as f:
            loaded = pickle.load(f)
        if isinstance(loaded, tuple) and len(loaded) == 2:
            _model, _scaler = loaded
        else:
            _model, _scaler = loaded, None
    except Exception:
        _model, _scaler = None, None


def _build_feature_vector(input_data: dict) -> np.ndarray:
    return np.array([[
        float(input_data.get('open') or 0),
        float(input_data.get('high') or 0),
        float(input_data.get('low') or 0),
        float(input_data.get('volume') or 0),
    ]], dtype=float)


def _derive_recommendation(predicted_price: float, current_price: float) -> tuple[str, str]:
    if current_price and predicted_price > current_price * 1.02:
        return 'UP', 'BUY'
    if current_price and predicted_price < current_price * 0.98:
        return 'DOWN', 'SELL'
    return 'HOLD', 'HOLD'


def make_prediction(input_data: dict) -> dict:
    """Return prediction dictionary given validated features.

    input_data should include open/high/low/volume fields and may contain symbol.
    """
    _load_model()

    symbol = input_data.get('symbol')
    current_price = float(input_data.get('close') or input_data.get('open') or 0)
    input_features = {
        'open': input_data.get('open'),
        'high': input_data.get('high'),
        'low': input_data.get('low'),
        'volume': input_data.get('volume'),
    }
    technical_indicators = {
        key: input_data.get(key)
        for key in ('ma_5', 'ma_10', 'ma_20', 'daily_return')
        if input_data.get(key) is not None
    }

    result = {
        'symbol': symbol,
        'current_price': current_price,
        'predicted_price': current_price,
        'trend': 'HOLD',
        'recommendation': 'HOLD',
        'timestamp': datetime.utcnow().isoformat(),
        'input_features': input_features,
    }
    if technical_indicators:
        result['technical_indicators'] = technical_indicators

    if _model is not None:
        try:
            features = _build_feature_vector(input_data)
            if _scaler is not None:
                features = _scaler.transform(features)
            predicted_price = float(_model.predict(features)[0])
            trend, recommendation = _derive_recommendation(predicted_price, current_price)
            result['predicted_price'] = predicted_price
            result['trend'] = trend
            result['recommendation'] = recommendation
        except Exception as e:
            result['error'] = f"model prediction failed: {e}"
    elif symbol:
        try:
            hist = yf.Ticker(symbol).history(period='5d')
            if not hist.empty:
                latest_close = float(hist['Close'].iloc[-1])
                trend, recommendation = _derive_recommendation(latest_close, latest_close)
                result['current_price'] = latest_close
                result['predicted_price'] = latest_close
                result['trend'] = trend
                result['recommendation'] = recommendation
        except Exception as e:
            result['error'] = f"price lookup failed: {e}"

    return result
