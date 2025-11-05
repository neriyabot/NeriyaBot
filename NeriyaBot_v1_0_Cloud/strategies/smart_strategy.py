import pandas as pd
import numpy as np
import logging

class SmartStrategy:
    def __init__(self, exchange, symbol="BTC/USDT"):
        self.exchange = exchange
        self.symbol = symbol
        self.position = None

    def get_data(self, timeframe="1h", limit=100):
        candles = self.exchange.client.fetch_ohlcv(self.symbol, timeframe, limit=limit)
        df = pd.DataFrame(candles, columns=["time","open","high","low","close","volume"])
        df["close"] = df["close"].astype(float)
        return df

    def ema(self, data, period):
        return data["close"].ewm(span=period, adjust=False).mean()

    def rsi(self, data, period=14):
        delta = data["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def get_signal(self):
        """ בודק מגמה רב־טווח ואותות משולבים """
        df_1h = self.get_data("1h")
        df_4h = self.get_data("4h")

        df_1h["EMA_9"] = self.ema(df_1h, 9)
        df_1h["EMA_21"] = self.ema(df_1h, 21)
        df_1h["RSI"] = self.rsi(df_1h)

        df_4h["EMA_9"] = self.ema(df_4h, 9)
        df_4h["EMA_21"] = self.ema(df_4h, 21)

        trend_up = df_4h["EMA_9"].iloc[-1] > df_4h["EMA_21"].iloc[-1]
        trend_down = df_4h["EMA_9"].iloc[-1] < df_4h["EMA_21"].iloc[-1]

        last = df_1h.iloc[-1]
        rsi = last["RSI"]
        ema9 = last["EMA_9"]
        ema21 = last["EMA_21"]

        # כניסה חכמה לפי מגמה כללית
        if trend_up and rsi < 40 and ema9 > ema21:
            logging.info("🟢 אישור רב־טווח לקנייה")
            return "BUY"

        elif trend_down and rsi > 60 and ema9 < ema21:
            logging.info("🔴 אישור רב־טווח למכירה")
            return "SELL"

        else:
            logging.info("⚪ אין איתות ברור – ממתין")
            return None
