
from signal_engine import is_market_open, generate_signal
import os

print(f"Market open: {is_market_open()}")
print(f"LIVE_MODE: {os.getenv('LIVE_MODE')}")
try:
    sig = generate_signal()
    print(f"Generated Signal: {sig}")
except Exception as e:
    print(f"Error generating signal: {e}")
