"""
LSTM model utilities for training and predicting stock prices.
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler


def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def prepare_data(df, window_size=60):
    """Prepare data for LSTM using closing prices"""
    scaler = MinMaxScaler(feature_range=(0, 1))
    close_prices = df[['Close']].values
    scaled = scaler.fit_transform(close_prices)

    X, y = [], []
    for i in range(window_size, len(scaled)):
        X.append(scaled[i-window_size:i, 0])
        y.append(scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler


def train_lstm(stock_df, window_size=60, epochs=10, batch_size=32):
    X, y, scaler = prepare_data(stock_df, window_size)
    model = create_lstm_model((X.shape[1], 1))
    early = EarlyStopping(monitor='loss', patience=5)
    model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=[early], verbose=0)
    return model, scaler


def predict_next_day(model, scaler, recent_window):
    """recent_window should be scaled values shape (window_size, 1)"""
    prediction = model.predict(np.reshape(recent_window, (1, recent_window.shape[0], 1)), verbose=0)
    return scaler.inverse_transform(prediction)[0][0]
