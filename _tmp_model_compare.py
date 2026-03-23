import pandas as pd
import numpy as np
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def evaluate_random_forest(df):
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    x_train = train_df[["Open", "High", "Low", "Volume"]]
    y_train = train_df["Close"]
    x_test = test_df[["Open", "High", "Low", "Volume"]]
    y_test = test_df["Close"]

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    return {
        "rmse": float(np.sqrt(mean_squared_error(y_test, pred))),
        "mae": float(mean_absolute_error(y_test, pred)),
        "r2": float(r2_score(y_test, pred)),
        "mape_percent": float(np.mean(np.abs((y_test - pred) / np.clip(np.abs(y_test), 1e-8, None))) * 100),
    }


def evaluate_lstm(df):
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping

    split_idx = int(len(df) * 0.8)
    close_all = df[["Close"]].values

    scaler = MinMaxScaler((0, 1))
    scaled = scaler.fit_transform(close_all)

    window = 60
    x_all, y_all = [], []
    for i in range(window, len(scaled)):
        x_all.append(scaled[i - window:i, 0])
        y_all.append(scaled[i, 0])

    x_all = np.array(x_all).reshape(-1, window, 1)
    y_all = np.array(y_all)

    seq_split = max(split_idx - window, 1)
    x_train, y_train = x_all[:seq_split], y_all[:seq_split]
    x_test, y_test = x_all[seq_split:], y_all[seq_split:]

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(window, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")

    early = EarlyStopping(monitor="loss", patience=2, restore_best_weights=True)
    model.fit(x_train, y_train, epochs=5, batch_size=32, callbacks=[early], verbose=0)

    pred_scaled = model.predict(x_test, verbose=0)
    pred = scaler.inverse_transform(pred_scaled).ravel()
    true = scaler.inverse_transform(y_test.reshape(-1, 1)).ravel()

    return {
        "rmse": float(np.sqrt(mean_squared_error(true, pred))),
        "mae": float(mean_absolute_error(true, pred)),
        "r2": float(r2_score(true, pred)),
        "mape_percent": float(np.mean(np.abs((true - pred) / np.clip(np.abs(true), 1e-8, None))) * 100),
    }


def main():
    df = pd.read_csv("Datasets/TradeIQ_stock_data.csv")
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"]).reset_index(drop=True)

    out = {"rows": int(len(df))}
    out["random_forest"] = evaluate_random_forest(df)

    try:
        out["lstm"] = evaluate_lstm(df)
    except Exception as err:
        out["lstm_error"] = str(err)

    with open("_tmp_model_compare_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(out)


if __name__ == "__main__":
    main()
