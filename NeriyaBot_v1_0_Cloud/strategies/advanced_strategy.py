import ccxt
import pandas as pd
import numpy as np
from utils.telegram_notifier import TelegramNotifier

class AdvancedStrategy:
    def __init__(self, symbol, timeframe="1h"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = ccxt.bybit({"enableRateLimit": True})
        self.notifier = TelegramNotifier()

    def get_data(self, limit=100):
        """מקבל נתונים היסטוריים מהבורסה"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except Exception as e:
            self.notifier.send_message(f"⚠️ שגיאה בשליפת נתונים עבור {self.symbol}: {e}")
            return None

    def calculate_indicators(self, df):
        """מחשב מדדים טכניים RSI, EMA, MACD"""
        df["EMA20"] = df["close"].ewm(span=20).mean()
        df["EMA50"] = df["close"].ewm(span=50).mean()

        delta = df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        exp1 = df["close"].ewm(span=12, adjust=False).mean()
        exp2 = df["close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = exp1 - exp2
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        return df

    def generate_signal(self):
        """קובע אם לקנות, למכור או להמתין"""
        df = self.get_data()
        if df is None:
            return "HOLD"

        df = self.calculate_indicators(df)
        last = df.iloc[-1]

        if last["RSI"] < 30 and last["EMA20"] > last["EMA50"] and last["MACD"] > last["Signal"]:
            signal = "BUY"
        elif last["RSI"] > 70 and last["EMA20"] < last["EMA50"] and last["MACD"] < last["Signal"]:
            signal = "SELL"
        else:
            signal = "HOLD"

        self.notifier.send_message(f"📊 {self.symbol} אות זוהה: {signal} (RSI={last['RSI']:.2f})")
        return signal
