import pandas as pd
import numpy as np
import logging

class SmartTrendStrategy:
    """
    אסטרטגיה חכמה שמזהה מתי לקנות ירידה (Buy the Dip)
    ומתי להצטרף למגמה (Trend Buy)
    """

    def __init__(self, exchange, symbol="BTC/USDT"):
        self.exchange = exchange
        self.symbol = symbol
        self.position = None

    def get_data(self, timeframe="1h", limit=200):
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
        df = self.get_data("1h")
        df["EMA_9"] = self.ema(df, 9)
        df["EMA_21"] = self.ema(df, 21)
        df["RSI"] = self.rsi(df)
        last = df.iloc[-1]

        rsi = last["RSI"]
        ema9 = last["EMA_9"]
        ema21 = last["EMA_21"]

        # זיהוי מגמה כללית
        trend_up = ema9 > ema21
        trend_down = ema9 < ema21

        # --- BUY THE DIP ---
        if trend_up and rsi < 30:
            logging.info("💎 Buy the Dip Signal – מגמה חיובית, מחיר בירידה חדה")
            return "BUY_DIP"

        # --- TREND BUY ---
        elif trend_up and 45 <= rsi <= 60:
            logging.info("🟢 Trend Buy Signal – כניסה עם כיוון המגמה")
            return "BUY_TREND"

        # --- SELL SIGNAL ---
        elif trend_down and rsi > 65:
            logging.info("🔴 Sell Signal – מגמה שלילית מתחזקת")
            return "SELL"

        else:
            logging.info("⚪ אין איתות ברור – ממתין")
            return None
