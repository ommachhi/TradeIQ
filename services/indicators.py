import pandas as pd
import numpy as np

def sma(df: pd.DataFrame, period=20) -> pd.Series:
    return df['Close'].rolling(window=period).mean()

def ema(df: pd.DataFrame, period=20) -> pd.Series:
    return df['Close'].ewm(span=period, adjust=False).mean()

def rsi(df: pd.DataFrame, period=14) -> pd.Series:
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def macd(df: pd.DataFrame) -> pd.DataFrame:
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({'macd': macd_line, 'signal': signal_line, 'histogram': histogram})

def bollinger_bands(df: pd.DataFrame, period=20) -> pd.DataFrame:
    sma20 = df['Close'].rolling(window=period).mean()
    std20 = df['Close'].rolling(window=period).std()
    upper = sma20 + (std20 * 2)
    lower = sma20 - (std20 * 2)
    return pd.DataFrame({'upper': upper, 'middle': sma20, 'lower': lower})

def atr(df: pd.DataFrame, period=14) -> pd.Series:
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()
