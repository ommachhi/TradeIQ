from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PLOTLY_TEMPLATE = "plotly_dark"


def candlestick_with_volume(df: pd.DataFrame, title: str = "") -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.72, 0.28],
        vertical_spacing=0.03,
    )
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color="#6C63FF"),
        row=2,
        col=1,
    )
    fig.update_layout(
        title=title,
        template=PLOTLY_TEMPLATE,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=560,
        legend=dict(orientation="h"),
    )
    return fig


def technical_indicator_chart(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=5,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.34, 0.14, 0.16, 0.18, 0.18],
        vertical_spacing=0.03,
        subplot_titles=("Price + Bands", "Volume", "RSI", "MACD", "Stochastic RSI"),
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close", line=dict(color="#6C63FF")), row=1, col=1)
    for column, name, color in [
        ("EMA_20", "EMA 20", "#00C2FF"),
        ("EMA_50", "EMA 50", "#20D68D"),
        ("EMA_200", "EMA 200", "#FFD166"),
        ("SMA_20", "SMA 20", "#FF9F1C"),
        ("SMA_50", "SMA 50", "#EF476F"),
        ("BB_upper", "BB Upper", "#A7B0C0"),
        ("BB_lower", "BB Lower", "#A7B0C0"),
        ("VWAP", "VWAP", "#FFFFFF"),
    ]:
        if column in df:
            fig.add_trace(go.Scatter(x=df.index, y=df[column], name=name, line=dict(width=1.2, color=color)), row=1, col=1)

    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color="#6C63FF"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="#20D68D")), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#EF476F", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#00C2FF", row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="#FFD166")), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal", line=dict(color="#A7B0C0")), row=4, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_hist"], name="Histogram", marker_color="#6C63FF"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Stochastic_RSI"], name="Stochastic RSI", line=dict(color="#FF9F1C")), row=5, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="#EF476F", row=5, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="#00C2FF", row=5, col=1)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=1050,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h"),
    )
    return fig


def prediction_chart(history_df: pd.DataFrame, forecast_df: pd.DataFrame, symbol: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=history_df.index,
            y=history_df["Close"],
            mode="lines",
            name=f"{symbol} actual",
            line=dict(color="#00C2FF", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df.index,
            y=forecast_df["Predicted"],
            mode="lines",
            name="Predicted",
            line=dict(color="#FF9F1C", width=2, dash="dash"),
        )
    )
    if {"Lower", "Upper"}.issubset(forecast_df.columns):
        fig.add_trace(
            go.Scatter(
                x=forecast_df.index,
                y=forecast_df["Upper"],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast_df.index,
                y=forecast_df["Lower"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(255, 159, 28, 0.18)",
                name="Confidence band",
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        title="Actual vs Predicted Price",
    )
    return fig


def portfolio_growth_chart(transactions: pd.DataFrame) -> go.Figure:
    if transactions.empty:
        return go.Figure()
    frame = transactions.copy()
    frame["trade_date"] = pd.to_datetime(frame["trade_date"])
    frame["cash_flow"] = frame["quantity"] * frame["buy_price"]
    frame = frame.groupby("trade_date", as_index=False)["cash_flow"].sum().sort_values("trade_date")
    frame["cumulative"] = frame["cash_flow"].cumsum()
    fig = px.area(frame, x="trade_date", y="cumulative", template=PLOTLY_TEMPLATE, title="Portfolio Growth")
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def accuracy_comparison_chart(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=frame["Model"], y=frame["Accuracy"], name="Accuracy", marker_color="#6C63FF"))
    fig.add_trace(go.Bar(x=frame["Model"], y=frame["R²"], name="R²", marker_color="#00C2FF"))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="group",
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        title="Model Accuracy Comparison",
    )
    return fig


def sector_heatmap(frame: pd.DataFrame) -> go.Figure:
    fig = px.treemap(
        frame,
        path=[px.Constant("Market"), "Sector", "Symbol"],
        values="MarketValue",
        color="ChangePct",
        color_continuous_scale=["#EF476F", "#1A1F2E", "#20D68D"],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20))
    return fig


def sparkline_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", line=dict(color="#6C63FF", width=2), name=symbol))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=120,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_visible=False,
        yaxis_visible=False,
        showlegend=False,
    )
    return fig
