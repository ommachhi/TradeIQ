from __future__ import annotations

import numpy as np
import pandas as pd


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    working = df.copy()

    try:
        from ta.momentum import RSIIndicator, StochasticOscillator
        from ta.trend import EMAIndicator, MACD, SMAIndicator
        from ta.volatility import BollingerBands
        from ta.volume import VolumeWeightedAveragePrice

        working["RSI"] = RSIIndicator(close=working["Close"], window=14).rsi()
        macd = MACD(close=working["Close"], window_fast=12, window_slow=26, window_sign=9)
        working["MACD"] = macd.macd()
        working["MACD_signal"] = macd.macd_signal()
        working["MACD_hist"] = macd.macd_diff()
        working["EMA_20"] = EMAIndicator(close=working["Close"], window=20).ema_indicator()
        working["EMA_50"] = EMAIndicator(close=working["Close"], window=50).ema_indicator()
        working["EMA_200"] = EMAIndicator(close=working["Close"], window=200).ema_indicator()
        working["SMA_20"] = SMAIndicator(close=working["Close"], window=20).sma_indicator()
        working["SMA_50"] = SMAIndicator(close=working["Close"], window=50).sma_indicator()
        bb = BollingerBands(close=working["Close"], window=20, window_dev=2)
        working["BB_mid"] = bb.bollinger_mavg()
        working["BB_upper"] = bb.bollinger_hband()
        working["BB_lower"] = bb.bollinger_lband()
        working["VWAP"] = VolumeWeightedAveragePrice(
            high=working["High"],
            low=working["Low"],
            close=working["Close"],
            volume=working["Volume"],
            window=14,
        ).volume_weighted_average_price()
        stoch = StochasticOscillator(
            high=working["High"],
            low=working["Low"],
            close=working["Close"],
            window=14,
            smooth_window=3,
        )
        working["Stochastic_RSI"] = stoch.stoch()
    except Exception:
        delta = working["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        working["RSI"] = 100 - (100 / (1 + rs))
        working["EMA_20"] = working["Close"].ewm(span=20, adjust=False).mean()
        working["EMA_50"] = working["Close"].ewm(span=50, adjust=False).mean()
        working["EMA_200"] = working["Close"].ewm(span=200, adjust=False).mean()
        working["SMA_20"] = working["Close"].rolling(20).mean()
        working["SMA_50"] = working["Close"].rolling(50).mean()
        ema_12 = working["Close"].ewm(span=12, adjust=False).mean()
        ema_26 = working["Close"].ewm(span=26, adjust=False).mean()
        working["MACD"] = ema_12 - ema_26
        working["MACD_signal"] = working["MACD"].ewm(span=9, adjust=False).mean()
        working["MACD_hist"] = working["MACD"] - working["MACD_signal"]
        rolling_std = working["Close"].rolling(20).std()
        working["BB_mid"] = working["SMA_20"]
        working["BB_upper"] = working["BB_mid"] + 2 * rolling_std
        working["BB_lower"] = working["BB_mid"] - 2 * rolling_std
        typical_price = (working["High"] + working["Low"] + working["Close"]) / 3
        cumulative_volume = working["Volume"].replace(0, np.nan).cumsum()
        working["VWAP"] = (typical_price * working["Volume"]).cumsum() / cumulative_volume
        lowest_low = working["Low"].rolling(14).min()
        highest_high = working["High"].rolling(14).max()
        working["Stochastic_RSI"] = ((working["Close"] - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)) * 100

    working["Return_1"] = working["Close"].pct_change()
    working["Return_5"] = working["Close"].pct_change(5)
    working["BB_width"] = (working["BB_upper"] - working["BB_lower"]) / working["BB_mid"].replace(0, np.nan)
    return working.dropna()


def feature_frame(df: pd.DataFrame, horizon: int = 1, lookback: int = 10) -> tuple[pd.DataFrame, list[str]]:
    working = add_technical_indicators(df)
    if working.empty:
        return pd.DataFrame(), []

    for lag in range(1, lookback + 1):
        working[f"lag_{lag}"] = working["Close"].shift(lag)
    working["target_price"] = working["Close"].shift(-horizon)
    working["target_direction"] = (working["target_price"] > working["Close"]).astype(int)
    feature_columns = [
        "Volume",
        "RSI",
        "MACD",
        "MACD_signal",
        "MACD_hist",
        "EMA_20",
        "EMA_50",
        "EMA_200",
        "SMA_20",
        "SMA_50",
        "BB_upper",
        "BB_mid",
        "BB_lower",
        "BB_width",
        "VWAP",
        "Stochastic_RSI",
        "Return_1",
        "Return_5",
    ] + [f"lag_{lag}" for lag in range(1, lookback + 1)]
    working = working.dropna()
    return working, feature_columns
