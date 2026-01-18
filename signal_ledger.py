# signal_ledger.py - MPV Ledger Management
# Tracks signal history and persistence (internal memory for MPV)

class SignalLedger:
    def __init__(self, limit=50):
        self.history = []
        self.limit = limit

    def record(self, signal):
        if not self.history or signal.get('timestamp') != self.history[0].get('timestamp'):
            self.history.insert(0, signal)
            if len(self.history) > self.limit:
                self.history.pop()
        return self.history

    def get_history(self):
        return self.history
