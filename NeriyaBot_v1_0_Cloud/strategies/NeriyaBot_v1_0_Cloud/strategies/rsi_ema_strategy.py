import pandas as pd
import numpy as np
import logging

class RSI_EMA_Strategy:
    def __init__(self, exchange, symbol="BTC/USDT", timeframe="1h"):
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.position = None  # None / "LONG" / "SHORT"

    def get_data(self, limit=100):
        candles = self.exchange.client.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
        df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume"])
        df["close"] = df["close"].astype(float)
        return df

    def rsi(self, data, period=14):
        delta = data["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def ema(self, data, period):
        return data["close"].ewm(span=period, adjust=False).mean()

    def generate_signal(self):
        data = self.get_data()
        data["RSI"] = self.rsi(data)
        data["EMA_9"] = self.ema(data, 9)
        data["EMA_21"] = self.ema(data, 21)

        latest = data.iloc[-1]
        rsi = latest["RSI"]
        ema9 = latest["EMA_9"]
        ema21 = latest["EMA_21"]

        if rsi < 30 and ema9 > ema21 and self.position != "LONG":
            self.position = "LONG"
            logging.info("🟢 BUY Signal detected")
            return "BUY"

        elif rsi > 70 and ema9 < ema21 and self.position == "LONG":
            self.position = None
            logging.info("🔴 SELL Signal detected")
            return "SELL"

        else:
            return None
