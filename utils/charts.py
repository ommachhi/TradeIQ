import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#161b22",
    font=dict(color="#f0f6fc"),
    margin=dict(l=20, r=20, t=40, b=20)
)

def apply_dark_theme(fig):
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#21262d")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#21262d")
    return fig

def candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC'), row=1, col=1)
    
    colors = ['#22c55e' if row['Close'] >= row['Open'] else '#ef4444' for i, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
    
    fig.update_layout(title=f"{symbol} Price & Volume", xaxis_rangeslider_visible=False)
    return apply_dark_theme(fig)

def line_chart_portfolio(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['value'], mode='lines', fill='tozeroy', line=dict(color='#4f46e5', width=3)))
    fig.update_layout(title="Portfolio Performance (30 Days)", showlegend=False)
    return apply_dark_theme(fig)

def prediction_bar_chart(signal_strengths: list) -> go.Figure:
    fig = go.Figure()
    colors = ["#22c55e" if s > 0 else "#ef4444" for s in signal_strengths]
    fig.add_trace(go.Bar(y=signal_strengths, marker_color=colors))
    fig.update_layout(title="Signal Strength Trend")
    return apply_dark_theme(fig)

def pie_chart_signals(buy_pct: float, sell_pct: float) -> go.Figure:
    fig = go.Figure(data=[go.Pie(labels=['BUY', 'SELL'], values=[buy_pct, sell_pct], hole=.5, marker_colors=['#22c55e', '#ef4444'])])
    fig.update_layout(title="Signal Distribution")
    return apply_dark_theme(fig)

def monthly_pnl_chart(months: list, values: list) -> go.Figure:
    colors = ["#22c55e" if v > 0 else "#ef4444" for v in values]
    fig = go.Figure(data=[go.Bar(x=months, y=values, marker_color=colors)])
    fig.update_layout(title="Monthly P&L (₹)")
    return apply_dark_theme(fig)

def indicator_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    from services.indicators import sma, ema, bollinger_bands
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC'))
    fig.add_trace(go.Scatter(x=df.index, y=sma(df, 20), mode='lines', name='SMA 20', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df.index, y=ema(df, 20), mode='lines', name='EMA 20', line=dict(color='orange')))
    bb = bollinger_bands(df)
    fig.add_trace(go.Scatter(x=df.index, y=bb['upper'], mode='lines', name='BB Upper', line=dict(color='gray', dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=bb['lower'], mode='lines', name='BB Lower', line=dict(color='gray', dash='dash')))
    fig.update_layout(title=f"{symbol} Technicals", xaxis_rangeslider_visible=False)
    return apply_dark_theme(fig)

def rsi_chart(rsi_series: pd.Series) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rsi_series.index, y=rsi_series, mode='lines', name='RSI', line=dict(color='#7c3aed')))
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444")
    fig.add_hline(y=30, line_dash="dash", line_color="#22c55e")
    fig.update_layout(title="Relative Strength Index (14)")
    return apply_dark_theme(fig)

def macd_chart(macd_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=macd_df.index, y=macd_df['macd'], mode='lines', name='MACD', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=macd_df.index, y=macd_df['signal'], mode='lines', name='Signal', line=dict(color='orange')))
    colors = ["#22c55e" if val > 0 else "#ef4444" for val in macd_df['histogram']]
    fig.add_trace(go.Bar(x=macd_df.index, y=macd_df['histogram'], marker_color=colors, name='Histogram'))
    fig.update_layout(title="MACD")
    return apply_dark_theme(fig)
