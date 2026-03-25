#!/usr/bin/env python
"""
Quick test to demonstrate the Indian stock prediction fix.
Copy this to terminal and run to verify predictions work correctly.
"""

import sys
sys.path.insert(0, 'tradeiq_backend')

from prediction.symbols import resolve_symbol_with_history

# Test symbols
test_symbols = ['RELIANCE', 'TCS', 'INFY', 'INFY.NS']

print("=" * 60)
print("Testing Indian Stock Symbol Resolution")
print("=" * 60)

for symbol in test_symbols:
    print(f"\nAttempting to resolve: {symbol}")
    try:
        resolved_symbol, hist = resolve_symbol_with_history(symbol, period='5d')
        if hist is not None and not hist.empty:
            latest = hist.iloc[-1]
            print(f"  ✓ Resolved to: {resolved_symbol}")
            print(f"    Latest Close: ₹{latest['Close']:.2f}")
            print(f"    Open: ₹{latest['Open']:.2f}, High: ₹{latest['High']:.2f}, Low: ₹{latest['Low']:.2f}")
            print(f"    Volume: {int(latest['Volume']):,}")
        else:
            print(f"  ✗ No data found")
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("\nNext Steps:")
print("1. Run: python retrain_model.py  (to train with proper scaler)")
print("2. Restart backend: python manage.py runserver")
print("3. Test prediction endpoint with RELIANCE, TCS, etc.")
print("=" * 60)
