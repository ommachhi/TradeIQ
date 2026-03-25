"""
Prediction helper that loads a trained model and computes next-day price and trend.
"""
import os
import pickle
from datetime import datetime

import numpy as np
from prediction.symbols import resolve_symbol_with_history

# simple cache so model is loaded once
_model = None
_scaler = None
_target_scaler = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model.pkl')


def _load_model():
    global _model, _scaler, _target_scaler
    if _model is not None or _scaler is not None or _target_scaler is not None:
        return

    try:
        with open(MODEL_PATH, 'rb') as f:
            loaded = pickle.load(f)
        if isinstance(loaded, tuple) and len(loaded) == 3:
            _model, _scaler, _target_scaler = loaded
        elif isinstance(loaded, tuple) and len(loaded) == 2:
            _model, _scaler = loaded
            _target_scaler = None
        elif isinstance(loaded, dict):
            _model = loaded.get('model')
            _scaler = loaded.get('feature_scaler') or loaded.get('scaler')
            _target_scaler = loaded.get('target_scaler')
        else:
            _model, _scaler, _target_scaler = loaded, None, None
    except Exception:
        _model, _scaler, _target_scaler = None, None, None


def _build_feature_vector(input_data: dict) -> np.ndarray:
    """Build feature vector [open, high, low, volume]"""
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


def _trend_from_mas(ma_5: float, ma_10: float, ma_20: float) -> tuple[str, str]:
    if ma_5 > ma_10 > ma_20:
        return 'Uptrend', 'BUY'
    if ma_5 < ma_10 < ma_20:
        return 'Downtrend', 'SELL'
    return 'Sideways', 'HOLD'


def _combine_recommendation(signal_rec: str, trend_bias: str) -> str:
    if signal_rec == trend_bias:
        return signal_rec
    if signal_rec == 'HOLD' and trend_bias in {'BUY', 'SELL'}:
        return trend_bias
    if trend_bias == 'HOLD':
        return signal_rec
    return 'HOLD'


def _change_percent(predicted_price: float, current_price: float) -> float:
    if not current_price:
        return 0.0
    return ((predicted_price - current_price) / current_price) * 100.0


def _confidence_from_change(abs_change_pct: float) -> str:
    if abs_change_pct < 2.0:
        return 'HIGH'
    if abs_change_pct <= 5.0:
        return 'MEDIUM'
    return 'LOW'


def _validation_from_change(abs_change_pct: float) -> tuple[bool, str | None]:
    if abs_change_pct > 10.0:
        return False, 'Unreliable Prediction'
    return True, None


def _predict_from_history(hist) -> tuple[float, dict]:
    """Predict next close using recent trend + moving-average mean reversion.

    This keeps outputs in a realistic range for symbols with very different
    absolute price scales (for example, Indian large-cap stocks).
    """
    closes = hist['Close'].dropna()
    if closes.empty:
        return 0.0, {}

    current_price = float(closes.iloc[-1])
    ma_5 = float(closes.rolling(window=5).mean().iloc[-1]) if len(closes) >= 5 else current_price
    ma_10 = float(closes.rolling(window=10).mean().iloc[-1]) if len(closes) >= 10 else current_price
    ma_20 = float(closes.rolling(window=20).mean().iloc[-1]) if len(closes) >= 20 else current_price

    daily_return = 0.0
    if len(closes) >= 2 and closes.iloc[-2] != 0:
        daily_return = float((closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2])

    momentum_5 = 0.0
    if len(closes) >= 6 and closes.iloc[-6] != 0:
        momentum_5 = float((closes.iloc[-1] - closes.iloc[-6]) / closes.iloc[-6])

    returns = closes.pct_change().dropna()
    volatility_20 = float(returns.tail(20).std()) if not returns.empty else 0.01

    # Weighted blend: current level + short/medium averages + near-term momentum.
    momentum_target = current_price * (1.0 + 0.6 * momentum_5 + 0.4 * daily_return)
    raw_prediction = (
        0.45 * current_price
        + 0.25 * ma_5
        + 0.15 * ma_10
        + 0.10 * ma_20
        + 0.05 * momentum_target
    )

    # Clamp move to volatility-aware band to avoid unrealistic jumps.
    max_move = min(0.12, max(0.02, 2.2 * volatility_20))
    lower = current_price * (1.0 - max_move)
    upper = current_price * (1.0 + max_move)
    predicted_price = float(np.clip(raw_prediction, lower, upper))

    indicators = {
        'ma_5': ma_5,
        'ma_10': ma_10,
        'ma_20': ma_20,
        'daily_return': daily_return,
    }
    return predicted_price, indicators


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
        'trend': 'Sideways',
        'recommendation': 'HOLD',
        'change_percent': 0.0,
        'confidence': 'LOW',
        'is_reliable': True,
        'timestamp': datetime.utcnow().isoformat(),
        'input_features': input_features,
    }
    if technical_indicators:
        result['technical_indicators'] = technical_indicators

    # For symbol-driven predictions, prefer live-history based forecasting so
    # the output aligns with current market regime and MA values.
    if symbol:
        try:
            resolved_symbol, hist = resolve_symbol_with_history(symbol, period='2y')
            if hist is not None and not hist.empty:
                predicted_price, live_indicators = _predict_from_history(hist)
                latest_close = float(hist['Close'].iloc[-1])
                ma_5 = float(live_indicators.get('ma_5', latest_close))
                ma_10 = float(live_indicators.get('ma_10', latest_close))
                ma_20 = float(live_indicators.get('ma_20', latest_close))
                trend_label, trend_bias = _trend_from_mas(ma_5, ma_10, ma_20)
                _, signal_recommendation = _derive_recommendation(predicted_price, latest_close)
                final_recommendation = _combine_recommendation(signal_recommendation, trend_bias)
                change_pct = _change_percent(predicted_price, latest_close)
                abs_change_pct = abs(change_pct)
                confidence = _confidence_from_change(abs_change_pct)
                is_reliable, warning = _validation_from_change(abs_change_pct)

                result['symbol'] = resolved_symbol
                result['current_price'] = latest_close
                result['predicted_price'] = predicted_price
                result['trend'] = trend_label
                result['recommendation'] = final_recommendation
                result['change_percent'] = change_pct
                result['confidence'] = confidence
                result['is_reliable'] = is_reliable
                if warning:
                    result['warning'] = warning
                if live_indicators:
                    result['technical_indicators'] = live_indicators
                return result
        except Exception as e:
            result['error'] = f"price lookup failed: {e}"

    if _model is not None:
        try:
            features = _build_feature_vector(input_data)
            # Scale features if scaler is available (required for trained model)
            if _scaler is not None:
                features = _scaler.transform(features)
            predicted_price = float(_model.predict(features)[0])
            # Inverse-transform prediction if a close-price scaler is available.
            if _target_scaler is not None:
                predicted_price = float(_target_scaler.inverse_transform(np.array([[predicted_price]])).ravel()[0])
            # Ensure prediction is reasonable; fallback to current price if not
            if np.isnan(predicted_price) or np.isinf(predicted_price):
                predicted_price = current_price
            # Sanity check: if prediction is too far from current price (>30%), use weighted average
            # This handles model overfitting or scale mismatch issues
            if current_price > 0:
                deviation_pct = abs(predicted_price - current_price) / current_price
                if deviation_pct > 0.30:
                    # Use 70% current price + 30% predicted for more stable output
                    predicted_price = 0.7 * current_price + 0.3 * predicted_price

            ma_5 = float(technical_indicators.get('ma_5', current_price or predicted_price))
            ma_10 = float(technical_indicators.get('ma_10', current_price or predicted_price))
            ma_20 = float(technical_indicators.get('ma_20', current_price or predicted_price))
            trend_label, trend_bias = _trend_from_mas(ma_5, ma_10, ma_20)
            _, signal_recommendation = _derive_recommendation(predicted_price, current_price)
            recommendation = _combine_recommendation(signal_recommendation, trend_bias)
            change_pct = _change_percent(predicted_price, current_price)
            abs_change_pct = abs(change_pct)
            confidence = _confidence_from_change(abs_change_pct)
            is_reliable, warning = _validation_from_change(abs_change_pct)

            result['predicted_price'] = predicted_price
            result['trend'] = trend_label
            result['recommendation'] = recommendation
            result['change_percent'] = change_pct
            result['confidence'] = confidence
            result['is_reliable'] = is_reliable
            if warning:
                result['warning'] = warning
        except Exception as e:
            result['error'] = f"model prediction failed: {e}"

    return result
