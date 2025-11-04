import os
import logging
import asyncio
import ccxt
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from utils.telegram_notifier import send_trade_alert

load_dotenv()

class Exchange:
    def __init__(self, mode):
        self.mode = mode
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API keys missing. Please set BYBIT_API_KEY and BYBIT_API_SECRET")

        # התחברות ל-Bybit
        self.client = ccxt.bybit({
            "apiKey": self.api_key,
            "secret": self.api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        })

        if mode == "DEMO":
            self.client.set_sandbox_mode(True)

        self.positions = {}  # פוזיציות פתוחות
        logging.info("✅ NeriyaBot Ultra+ connected successfully to Bybit!")

    async def fetch_ohlcv(self, symbol, timeframe="15m", limit=100):
        """משיכת נתוני גרף"""
        try:
            data = self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["close"] = df["close"].astype(float)
            return df
        except Exception as e:
            logging.error(f"❌ Failed to fetch data for {symbol}: {e}")
            return None

    def calculate_indicators(self, df):
        """חישוב אינדיקטורים (RSI + EMA קצר וארוך)"""
        df["EMA_short"] = df["close"].ewm(span=9, adjust=False).mean()
        df["EMA_long"] = df["close"].ewm(span=21, adjust=False).mean()

        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        return df

    async def trade_signal(self, symbol):
        """יצירת אות מסחר לפי RSI + EMA"""
        df_15m = await self.fetch_ohlcv(symbol, "15m")
        df_1h = await self.fetch_ohlcv(symbol, "1h")

        if df_15m is None or df_1h is None:
            return "HOLD"

        df_15m = self.calculate_indicators(df_15m)
        df_1h = self.calculate_indicators(df_1h)

        rsi_15 = df_15m["RSI"].iloc[-1]
        rsi_1h = df_1h["RSI"].iloc[-1]
        ema_cross_15 = df_15m["EMA_short"].iloc[-1] > df_15m["EMA_long"].iloc[-1]
        ema_cross_1h = df_1h["EMA_short"].iloc[-1] > df_1h["EMA_long"].iloc[-1]

        if rsi_15 < 30 and ema_cross_15 and ema_cross_1h:
            return "BUY"
        elif rsi_15 > 70 and not ema_cross_15:
            return "SELL"
        else:
            return "HOLD"

    async def execute_trade(self, symbol, action, amount, entry_price):
        """ביצוע פעולת מסחר"""
        tp = entry_price * 1.05  # Take Profit 5%
        sl = entry_price * 0.98  # Stop Loss 2%

        self.positions[symbol] = {
            "side": action,
            "entry": entry_price,
            "tp": tp,
            "sl": sl
        }

        msg = f"📈 נפתחה עסקה: {action} על {symbol}\n🎯 TP: {tp:.2f} | ⛔ SL: {sl:.2f}"
        await send_trade_alert(msg)
        logging.info(msg)

    async def monitor_positions(self):
        """בדיקה מתמדת של העסקאות הפתוחות"""
        while True:
            to_close = []
            for symbol, pos in self.positions.items():
                ticker = self.client.fetch_ticker(symbol)
                current_price = ticker["last"]

                if pos["side"] == "BUY":
                    if current_price >= pos["tp"]:
                        msg = f"💰 עסקה סגורה ברווח על {symbol} (+5%)"
                        await send_trade_alert(msg)
                        to_close.append(symbol)
                    elif current_price <= pos["sl"]:
                        msg = f"❌ עסקה נסגרה בהפסד על {symbol} (-2%)"
                        await send_trade_alert(msg)
                        to_close.append(symbol)

                elif pos["side"] == "SELL":
                    if current_price <= pos["tp"]:
                        msg = f"💰 עסקת SELL נסגרה ברווח על {symbol} (+5%)"
                        await send_trade_alert(msg)
                        to_close.append(symbol)
                    elif current_price >= pos["sl"]:
                        msg = f"❌ עסקת SELL נסגרה בהפסד על {symbol} (-2%)"
                        await send_trade_alert(msg)
                        to_close.append(symbol)

            for s in to_close:
                del self.positions[s]

            await asyncio.sleep(10)

    async def run(self):
        """לולאת מסחר כוללת"""
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
        balance = 10000
        active_trades = 0
        max_trades = 6

        asyncio.create_task(self.monitor_positions())

        while True:
            for symbol in symbols:
                if active_trades >= max_trades:
                    continue

                signal = await self.trade_signal(symbol)
                ticker = self.client.fetch_ticker(symbol)
                price = ticker["last"]

                if signal == "BUY" or signal == "SELL":
                    await self.execute_trade(symbol, signal, balance * 0.05, price)
                    active_trades += 1
                else:
                    logging.info(f"⏸ {symbol} - אין פעולה כרגע")

                await asyncio.sleep(15)
