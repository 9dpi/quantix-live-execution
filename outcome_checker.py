# outcome_checker.py - Signal Result Validation
# Checks if signal hit TP or SL (Post-trade analysis)

def verify_signal_outcome(signal, current_price):
    """
    Basic logic to check if a signal's targets were met
    """
    entry = signal.get('entry', 0)
    tp = signal.get('tp', 0)
    sl = signal.get('sl', 0)
    direction = signal.get('direction', 'WAIT')

    if direction == 'BUY':
        if current_price >= tp: return "WIN"
        if current_price <= sl: return "LOSS"
    elif direction == 'SELL':
        if current_price <= tp: return "WIN"
        if current_price >= sl: return "LOSS"
    
    return "PENDING"
