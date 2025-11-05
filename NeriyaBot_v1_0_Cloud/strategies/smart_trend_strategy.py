import pandas as pd
import numpy as np
import asyncio
import logging

class SmartTrendStrategy:
    def __init__(self, exchange):
        self.exchange = exchange
        self.last_signal = None

    async def get_klines(self, symbol, timeframe="15m", limit=200):
        try:
            data = await asyncio.to_thread(
                self.exchange.client.fetch_ohlcv,
                symbol,
                timeframe,
                limit=limit
            )
            df = pd.DataFrame(
                data,
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except Exception as e:
            logging.error(f"❌ שגיאה בטעינת נתוני Klines: {e}")
            return None

    def calculate_indicators(self, df):
        # חישוב ממוצעים נעים
        df["EMA_20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["EMA_50"] = df["close"].ewm(span=50, adjust=False).mean()

        # חישוב RSI
        delta = df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        return df

    async def generate_signal(self, symbol):
        df = await self.get_klines(symbol)
        if df is None or len(df) < 50:
            return None

        df = self.calculate_indicators(df)
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        ema_20, ema_50 = last_row["EMA_20"], last_row["EMA_50"]
        prev_ema_20, prev_ema_50 = prev_row["EMA_20"], prev_row["EMA_50"]
        rsi = last_row["RSI"]

        # תנאי קנייה: EMA20 חוצה כלפי מעלה את EMA50 + RSI עולה מ-50
        if prev_ema_20 < prev_ema_50 and ema_20 > ema_50 and rsi > 50:
            if self.last_signal != "BUY":
                self.last_signal = "BUY"
                logging.info("📈 אות קנייה מזוהה (מגמת עלייה)")
                return "BUY"

        # תנאי מכירה: EMA20 חוצה כלפי מטה את EMA50 + RSI יורד מ-50
        elif prev_ema_20 > prev_ema_50 and ema_20 < ema_50 and rsi < 50:
            if self.last_signal != "SELL":
                self.last_signal = "SELL"
                logging.info("📉 אות מכירה מזוהה (מגמת ירידה)")
                return "SELL"

        # אין שינוי ברור
        return None
