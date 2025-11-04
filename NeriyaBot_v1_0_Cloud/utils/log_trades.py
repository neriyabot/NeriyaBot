import csv
import os
from datetime import datetime

LOG_FILE = "trade_history.csv"

class TradeLogger:
    def __init__(self):
        # אם אין קובץ – ניצור חדש עם כותרות
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Symbol", "Action", "Amount(USDT)", "Price", "Status"])

    def log_trade(self, symbol, action, amount_usdt, price, status="Completed"):
        """שומר כל עסקה בקובץ"""
        with open(LOG_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                action,
                amount_usdt,
                price,
                status
            ])
        print(f"🧾 נרשמה עסקה: {action} ב־{symbol} ({amount_usdt}$ במחיר {price})")
