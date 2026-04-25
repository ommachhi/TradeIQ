"""Research panel helpers for stock overview, indicators, news, and AI insights."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timedelta
from math import sqrt

import numpy as np
import pandas as pd
import yfinance as yf

from .symbols import resolve_symbol_with_history

_RESEARCH_CACHE: dict[tuple[str, str], tuple[dict, datetime]] = {}
_RESEARCH_TTL_SECONDS = 90
_PROVIDER_TIMEOUT_SECONDS = 4

_RANGE_CONFIG = {
    '1d': {'period': '1d', 'interval': '15m', 'display': '1D'},
    '1w': {'period': '5d', 'interval': '60m', 'display': '1W'},
    '1m': {'period': '1mo', 'interval': None, 'display': '1M'},
    '1y': {'period': '1y', 'interval': None, 'display': '1Y'},
}

_POSITIVE_WORDS = {
    'beat', 'beats', 'growth', 'gain', 'gains', 'surge', 'surges', 'record', 'strong', 'upgrade',
    'outperform', 'bullish', 'expands', 'expansion', 'profit', 'profits', 'optimistic', 'partnership',
    'buyback', 'momentum', 'rebound', 'rise', 'rises', 'upside', 'launch', 'approval', 'winner'
}
_NEGATIVE_WORDS = {
    'miss', 'misses', 'drop', 'drops', 'fall', 'falls', 'cut', 'cuts', 'downgrade', 'lawsuit',
    'probe', 'weak', 'warning', 'bearish', 'slowdown', 'decline', 'declines', 'loss', 'losses',
    'risk', 'risks', 'delay', 'delays', 'crash', 'selloff', 'investigation', 'concern', 'pressure'
}


def _run_with_timeout(func, *args, timeout_seconds=_PROVIDER_TIMEOUT_SECONDS, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError as exc:
            raise TimeoutError(f"Research provider timeout after {timeout_seconds}s") from exc


def _cache_get(symbol: str, range_key: str):
    cached = _RESEARCH_CACHE.get((symbol, range_key))
    if not cached:
        return None
    payload, expires_at = cached
    if datetime.utcnow() >= expires_at:
        _RESEARCH_CACHE.pop((symbol, range_key), None)
        return None
    return payload


def _cache_set(symbol: str, range_key: str, payload: dict):
    _RESEARCH_CACHE[(symbol, range_key)] = (
        payload,
        datetime.utcnow() + timedelta(seconds=_RESEARCH_TTL_SECONDS),
    )


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _format_news_timestamp(value):
    if value in (None, ''):
        return None

    if isinstance(value, (int, float)):
        try:
            return datetime.utcfromtimestamp(value).isoformat() + 'Z'
        except (OverflowError, OSError, ValueError):
            return None

    if isinstance(value, str):
        normalized = value.replace('Z', '+00:00')
        try:
            return datetime.fromisoformat(normalized).isoformat()
        except ValueError:
            return value

    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return None


def _compact_news_item(item: dict) -> dict | None:
    content = item.get('content') if isinstance(item.get('content'), dict) else {}
    provider = content.get('provider') if isinstance(content.get('provider'), dict) else {}
    canonical = content.get('canonicalUrl') if isinstance(content.get('canonicalUrl'), dict) else {}

    headline = (
        item.get('title')
        or content.get('title')
        or content.get('description')
        or ''
    ).strip()
    if not headline:
        return None

    source = (
        item.get('publisher')
        or provider.get('displayName')
        or content.get('publisher')
        or 'Market Wire'
    )
    url = item.get('link') or canonical.get('url') or content.get('clickThroughUrl', {}).get('url')
    published_at = _format_news_timestamp(item.get('providerPublishTime') or content.get('pubDate'))

    return {
        'headline': headline,
        'source': source,
        'url': url,
        'published_at': published_at,
    }


def _classify_sentiment(*parts: str) -> tuple[str, int]:
    tokens = ' '.join(filter(None, parts)).lower().replace('-', ' ').split()
    score = 0
    for token in tokens:
        if token in _POSITIVE_WORDS:
            score += 1
        elif token in _NEGATIVE_WORDS:
            score -= 1

    if score > 0:
        return 'Positive', score
    if score < 0:
        return 'Negative', score
    return 'Neutral', score


def _fetch_company_snapshot(symbol: str) -> tuple[dict, list[dict]]:
    ticker = yf.Ticker(symbol)

    info = {}
    fast_info = {}
    news = []

    try:
        get_info = getattr(ticker, 'get_info', None)
        info = _run_with_timeout(get_info if callable(get_info) else lambda: ticker.info) or {}
    except Exception:
        info = {}

    try:
        fast_info_obj = _run_with_timeout(lambda: ticker.fast_info)
        fast_info = dict(fast_info_obj or {})
    except Exception:
        fast_info = {}

    try:
        get_news = getattr(ticker, 'get_news', None)
        raw_news = _run_with_timeout(get_news if callable(get_news) else lambda: ticker.news) or []
        news = raw_news[:8]
    except Exception:
        news = []

    return {'info': info, 'fast_info': fast_info}, news


def _rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_value = 100 - (100 / (1 + rs))
    return _safe_float(rsi_value.iloc[-1], 50.0)


def _macd(series: pd.Series) -> dict:
    ema_12 = series.ewm(span=12, adjust=False).mean()
    ema_26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        'macd': _safe_float(macd_line.iloc[-1]),
        'signal': _safe_float(signal_line.iloc[-1]),
        'histogram': _safe_float(histogram.iloc[-1]),
    }


def _trend_label(latest_close: float, ema_20: float, ema_50: float, rsi_value: float, macd_hist: float) -> str:
    if latest_close > ema_20 > ema_50 and rsi_value >= 55 and macd_hist >= 0:
        return 'Uptrend'
    if latest_close < ema_20 < ema_50 and rsi_value <= 45 and macd_hist <= 0:
        return 'Downtrend'
    return 'Sideways'


def _volatility_pct(close: pd.Series) -> float:
    returns = close.pct_change().dropna()
    if returns.empty:
        return 0.0
    realized = returns.tail(30).std() * sqrt(252) * 100
    return _safe_float(realized, 0.0)


def _confidence_pct(confidence: str, change_percent: float, is_reliable: bool) -> int:
    base = {'HIGH': 84, 'MEDIUM': 68, 'LOW': 52}.get((confidence or 'LOW').upper(), 52)
    adjustment = min(12, int(abs(change_percent) // 2))
    total = base - adjustment
    if not is_reliable:
        total -= 12
    return max(30, min(95, total))


def _risk_profile(volatility_pct: float, change_percent: float, is_reliable: bool) -> tuple[int, str]:
    raw_score = min(100, max(8, (volatility_pct * 3.5) + abs(change_percent) * 2.2 + (15 if not is_reliable else 0)))
    if raw_score < 35:
        return int(round(raw_score)), 'Low'
    if raw_score < 65:
        return int(round(raw_score)), 'Medium'
    return int(round(raw_score)), 'High'


def _direction_from_prediction(predicted_price: float, current_price: float) -> str:
    if current_price <= 0:
        return 'Sideways'
    if predicted_price > current_price * 1.01:
        return 'Up'
    if predicted_price < current_price * 0.99:
        return 'Down'
    return 'Sideways'


def _news_payload(raw_news: list[dict]) -> tuple[list[dict], dict]:
    news_items = []
    counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}

    for raw_item in raw_news:
        item = _compact_news_item(raw_item if isinstance(raw_item, dict) else {})
        if not item:
            continue
        sentiment, score = _classify_sentiment(item['headline'])
        counts[sentiment] += 1
        news_items.append({
            **item,
            'sentiment': sentiment,
            'sentiment_score': score,
        })
        if len(news_items) == 6:
            break

    if not news_items:
        summary = {
            'overall': 'Neutral',
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'summary': 'No recent headlines were available from the market feed.',
        }
        return [], summary

    overall = max(counts, key=lambda key: (counts[key], key == 'Neutral'))
    summary = {
        'overall': overall,
        'positive': counts['Positive'],
        'negative': counts['Negative'],
        'neutral': counts['Neutral'],
        'summary': f"{counts['Positive']} positive, {counts['Negative']} negative, and {counts['Neutral']} neutral headlines in the latest feed.",
    }
    return news_items, summary


def _recommendation_payload(trend: str, rsi_value: float, macd_hist: float, prediction: dict, sentiment_summary: dict, risk_level: str) -> dict:
    score = 0
    reasons = []

    direction = prediction['direction']
    if direction == 'Up':
        score += 1
        reasons.append('AI projection points to upside from current price.')
    elif direction == 'Down':
        score -= 1
        reasons.append('AI projection points to downside pressure.')

    if trend == 'Uptrend':
        score += 1
        reasons.append('Price structure remains above key EMAs.')
    elif trend == 'Downtrend':
        score -= 1
        reasons.append('Price structure remains below key EMAs.')

    if rsi_value < 35:
        score += 1
        reasons.append('RSI is near oversold territory, which can support a rebound.')
    elif rsi_value > 70:
        score -= 1
        reasons.append('RSI is stretched, so upside may be limited short term.')

    if macd_hist > 0:
        score += 1
    elif macd_hist < 0:
        score -= 1

    overall_sentiment = sentiment_summary.get('overall', 'Neutral')
    if overall_sentiment == 'Positive':
        score += 1
        reasons.append('News flow is leaning positive.')
    elif overall_sentiment == 'Negative':
        score -= 1
        reasons.append('News flow is leaning negative.')

    if risk_level == 'High':
        score -= 1
        reasons.append('Short-term risk remains elevated.')

    if score >= 2:
        action = 'BUY'
    elif score <= -2:
        action = 'SELL'
    else:
        action = 'HOLD'

    if not reasons:
        reasons.append('Signals are mixed, so waiting for stronger confirmation is safer.')

    return {
        'action': action,
        'score': score,
        'reason': ' '.join(reasons[:3]),
    }


def _chart_points(hist: pd.DataFrame, range_key: str) -> list[dict]:
    points = []
    intraday = range_key in {'1d', '1w'}

    for index, row in hist.iterrows():
        timestamp = pd.Timestamp(index)
        label = timestamp.strftime('%d %b %H:%M') if intraday else timestamp.strftime('%d %b')
        points.append({
            'label': label,
            'timestamp': timestamp.isoformat(),
            'open': _safe_float(row.get('Open')),
            'high': _safe_float(row.get('High')),
            'low': _safe_float(row.get('Low')),
            'close': _safe_float(row.get('Close')),
            'volume': _safe_int(row.get('Volume')),
        })
    return points


def build_research_panel(symbol: str, range_key: str = '1m') -> dict:
    cleaned_symbol = (symbol or '').strip().upper()
    selected_range = (range_key or '1m').strip().lower()
    if selected_range not in _RANGE_CONFIG:
        raise ValueError('Invalid research range selected.')

    cached = _cache_get(cleaned_symbol, selected_range)
    if cached:
        return cached

    chart_config = _RANGE_CONFIG[selected_range]
    resolved_symbol, chart_hist = resolve_symbol_with_history(
        cleaned_symbol,
        period=chart_config['period'],
        interval=chart_config['interval'],
    )
    base_symbol, base_hist = resolve_symbol_with_history(cleaned_symbol, period='1y')

    resolved_symbol = resolved_symbol or base_symbol
    if resolved_symbol is None or base_hist is None or base_hist.empty:
        raise LookupError('Unable to load research data for this symbol.')

    if chart_hist is None or chart_hist.empty:
        chart_hist = base_hist.copy()

    company_snapshot, raw_news = _fetch_company_snapshot(resolved_symbol)
    info = company_snapshot.get('info', {})
    fast_info = company_snapshot.get('fast_info', {})

    daily_hist = base_hist.copy()
    daily_hist = daily_hist.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
    if daily_hist.empty:
        raise LookupError('Not enough market history is available for this symbol.')

    close = daily_hist['Close'].astype(float)
    latest_close = _safe_float(close.iloc[-1])
    previous_close = _safe_float(close.iloc[-2], latest_close) if len(close) > 1 else latest_close
    price_change = latest_close - previous_close
    price_change_pct = (price_change / previous_close * 100) if previous_close else 0.0

    ma_20 = _safe_float(close.rolling(window=20, min_periods=1).mean().iloc[-1], latest_close)
    ma_50 = _safe_float(close.rolling(window=50, min_periods=1).mean().iloc[-1], latest_close)
    ema_20 = _safe_float(close.ewm(span=20, adjust=False).mean().iloc[-1], latest_close)
    ema_50 = _safe_float(close.ewm(span=50, adjust=False).mean().iloc[-1], latest_close)
    rsi_value = _rsi(close)
    macd_values = _macd(close)
    support = _safe_float(daily_hist['Low'].tail(20).min(), latest_close)
    resistance = _safe_float(daily_hist['High'].tail(20).max(), latest_close)
    trend = _trend_label(latest_close, ema_20, ema_50, rsi_value, macd_values['histogram'])
    volatility = _volatility_pct(close)

    latest_row = daily_hist.iloc[-1]
    daily_return = _safe_float(close.pct_change().iloc[-1], 0.0) if len(close) > 1 else 0.0

    from ai.predictor import make_prediction

    prediction_result = make_prediction({
        'symbol': resolved_symbol,
        'open': _safe_float(latest_row.get('Open')),
        'high': _safe_float(latest_row.get('High')),
        'low': _safe_float(latest_row.get('Low')),
        'close': latest_close,
        'volume': _safe_int(latest_row.get('Volume')),
        'ma_5': _safe_float(close.rolling(window=5, min_periods=1).mean().iloc[-1], latest_close),
        'ma_10': _safe_float(close.rolling(window=10, min_periods=1).mean().iloc[-1], latest_close),
        'ma_20': ma_20,
        'daily_return': daily_return,
    })

    predicted_price = _safe_float(prediction_result.get('predicted_price'), latest_close)
    current_price = _safe_float(prediction_result.get('current_price'), latest_close)
    predicted_change_pct = _safe_float(prediction_result.get('change_percent'), 0.0)
    confidence_label = (prediction_result.get('confidence') or 'LOW').upper()
    is_reliable = prediction_result.get('is_reliable') is not False
    confidence_pct = _confidence_pct(confidence_label, predicted_change_pct, is_reliable)
    risk_score, risk_label = _risk_profile(volatility, predicted_change_pct, is_reliable)
    direction = _direction_from_prediction(predicted_price, current_price)

    news_items, sentiment_summary = _news_payload(raw_news)

    recommendation = _recommendation_payload(
        trend=trend,
        rsi_value=rsi_value,
        macd_hist=macd_values['histogram'],
        prediction={
            'direction': direction,
            'change_percent': predicted_change_pct,
        },
        sentiment_summary=sentiment_summary,
        risk_level=risk_label,
    )

    currency = (
        info.get('currency')
        or fast_info.get('currency')
        or ('INR' if resolved_symbol.endswith(('.NS', '.BO')) else 'USD')
    )
    market_cap = _safe_float(fast_info.get('marketCap') or info.get('marketCap'), None)
    volume = _safe_int(fast_info.get('lastVolume') or info.get('volume') or latest_row.get('Volume'))
    year_high = _safe_float(
        fast_info.get('yearHigh') or info.get('fiftyTwoWeekHigh') or daily_hist['High'].tail(252).max(),
        latest_close,
    )
    year_low = _safe_float(
        fast_info.get('yearLow') or info.get('fiftyTwoWeekLow') or daily_hist['Low'].tail(252).min(),
        latest_close,
    )
    company_name = (
        info.get('shortName')
        or info.get('longName')
        or info.get('displayName')
        or resolved_symbol
    )

    payload = {
        'symbol': resolved_symbol,
        'company_name': company_name,
        'selected_range': selected_range,
        'range_label': chart_config['display'],
        'overview': {
            'company_name': company_name,
            'symbol': resolved_symbol,
            'currency': currency,
            'current_price': current_price,
            'price_change': round(price_change, 2),
            'price_change_pct': round(price_change_pct, 2),
            'market_cap': market_cap,
            'volume': volume,
            'fifty_two_week_high': round(year_high, 2),
            'fifty_two_week_low': round(year_low, 2),
            'as_of': _chart_points(chart_hist.tail(1), selected_range)[0]['timestamp'],
        },
        'chart': {
            'range': selected_range,
            'points': _chart_points(chart_hist, selected_range),
        },
        'technical_analysis': {
            'moving_averages': {
                'ma_20': round(ma_20, 2),
                'ma_50': round(ma_50, 2),
                'ema_20': round(ema_20, 2),
                'ema_50': round(ema_50, 2),
            },
            'rsi': round(rsi_value, 2),
            'macd': {
                'macd': round(macd_values['macd'], 4),
                'signal': round(macd_values['signal'], 4),
                'histogram': round(macd_values['histogram'], 4),
            },
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'trend': trend,
            'volatility_pct': round(volatility, 2),
        },
        'ai_prediction': {
            'predicted_price': round(predicted_price, 2),
            'direction': direction,
            'confidence_pct': confidence_pct,
            'confidence_label': confidence_label.title(),
            'risk_score': risk_score,
            'risk_level': risk_label,
            'change_percent': round(predicted_change_pct, 2),
            'recommendation': prediction_result.get('recommendation', recommendation['action']),
            'warning': prediction_result.get('warning') or '',
        },
        'news_sentiment': {
            'items': news_items,
            'summary': sentiment_summary,
        },
        'recommendation': recommendation,
    }

    _cache_set(cleaned_symbol, selected_range, payload)
    return payload
