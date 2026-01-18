# rate_limit.py - TwelveData & API Quota Protection
# Strictly enforces ≤ 1 request / minute for market data

import time

_last_call = 0

def call_allowed():
    global _last_call
    now = time.time()
    if now - _last_call >= 60:
        _last_call = now
        return True
    return False

def check_quota():
    # Placeholder for more complex quota tracking if needed
    return True
