import json
import os
from datetime import datetime

TRADES_FILE = "trades_log.json"

def log_trade(symbol, side, amount, price, profit_loss=None):
    trade = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "price": price,
        "profit_loss": profit_loss
    }

    trades = []
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "r") as f:
            trades = json.load(f)

    trades.append(trade)

    # שמירה מקומית
    with open(TRADES_FILE, "w") as f:
        json.dump(trades[-100:], f, indent=4)

def get_last_trades(limit=5):
    if not os.path.exists(TRADES_FILE):
        return []

    with open(TRADES_FILE, "r") as f:
        trades = json.load(f)

    return trades[-limit:]
