def format_inr(value: float) -> str:
    """Format as Indian number system with ₹ prefix: ₹4,82,350.00"""
    if value is None: return "₹0.00"
    s, *d = str(round(value, 2)).partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return f"₹{r}{d[0]}{d[1].ljust(2, '0')}"

def format_change(value: float) -> str:
    if value is None: return "0.00%"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"

def color_value(value: float) -> str:
    if value is None: return ""
    return "metric-positive" if value > 0 else "metric-negative" if value < 0 else ""

def signal_badge_html(signal: str) -> str:
    if signal == "BUY":
        return f'<span class="badge-buy">{signal}</span>'
    return f'<span class="badge-sell">{signal}</span>'
