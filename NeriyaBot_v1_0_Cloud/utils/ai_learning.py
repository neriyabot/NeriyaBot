import pandas as pd
import os
import numpy as np
from datetime import datetime

LOG_FILE = "trade_history.csv"

class AILearning:
    def __init__(self):
        self.best_strategy = {"rsi_weight": 1.0, "macd_weight": 1.0, "ema_weight": 1.0}
        self.learning_rate = 0.1  # כמה מהר להתאים את המשקלות

    def analyze_history(self):
        """לומד מהעסקאות הקודמות כדי לשפר החלטות עתידיות"""
        if not os.path.exists(LOG_FILE):
            print("⚠️ אין היסטוריית עסקאות ללמידה.")
            return self.best_strategy

        df = pd.read_csv(LOG_FILE)

        # רק עסקאות מוצלחות
        df_success = df[df["סטטוס"].isin(["Success", "Completed", "בוצע"])]

        if df_success.empty:
            print("⚠️ אין מספיק עסקאות מוצלחות ללמידה.")
            return self.best_strategy

        # מדמה למידה: אם היו יותר רווחים בקנייה, נותן משקל גבוה ל-RSI
        buy_trades = df_success[df_success["פעולה"].str.contains("BUY", case=False)]
        sell_trades = df_success[df_success["פעולה"].str.contains("SELL", case=False)]

        if len(buy_trades) > len(sell_trades):
            self.best_strategy["rsi_weight"] += self.learning_rate
        else:
            self.best_strategy["macd_weight"] += self.learning_rate

        # עדכון עדין של EMA לפי ממוצע רווחים
        if "מחיר" in df_success.columns:
            price_changes = df_success["מחיר"].diff().fillna(0)
            avg_change = np.mean(price_changes)
            if avg_change > 0:
                self.best_strategy["ema_weight"] += self.learning_rate / 2
            else:
                self.best_strategy["ema_weight"] -= self.learning_rate / 2

        print(f"🤖 משקלות חדשים: {self.best_strategy}")
        return self.best_strategy
