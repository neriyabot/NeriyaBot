import logging
import pandas as pd
import asyncio
from utils.telegram_notifier import send_trade_alert

class RiskManager:
    def __init__(self, exchange, symbol="BTC/USDT", atr_period=14, atr_mult_sl=1.5, atr_mult_tp=3.0):
        """
        ניהול סיכונים חכם לפי תנודתיות (ATR)
        """
        self.exchange = exchange
        self.symbol = symbol
        self.atr_period = atr_period
        self.atr_mult_sl = atr_mult_sl
        self.atr_mult_tp = atr_mult_tp
        self.active_trade = None  # {"side": "BUY", "entry": float}

    def get_atr(self):
        """ מחשב ATR (Average True Range) מהנתונים האחרונים """
        candles = self.exchange.client.fetch_ohlcv(self.symbol, "1h", limit=self.atr_period + 1)
        df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume"])
        df["high_low"] = df["high"] - df["low"]
        df["high_close"] = abs(df["high"] - df["close"].shift())
        df["low_close"] = abs(df["low"] - df["close"].shift())
        df["true_range"] = df[["high_low", "high_close", "low_close"]].max(axis=1)
        df["ATR"] = df["true_range"].rolling(self.atr_period).mean()
        return df["ATR"].iloc[-1]

    def open_trade(self, side: str, entry_price: float):
        atr = self.get_atr()
        self.active_trade = {
            "side": side,
            "entry": entry_price,
            "atr": atr,
        }
        logging.info(f"🎯 נפתחה עסקה {side} במחיר {entry_price} (ATR={atr:.2f})")

    async def monitor_trade(self):
        """ מעקב אחרי עסקה פתוחה, כולל Stop-Loss / Take-Profit דינמיים """
        while True:
            try:
                if self.active_trade:
                    ticker = self.exchange.client.fetch_ticker(self.symbol)
                    price = ticker["last"]
                    entry = self.active_trade["entry"]
                    atr = self.active_trade["atr"]

                    sl_distance = atr * self.atr_mult_sl
                    tp_distance = atr * self.atr_mult_tp

                    if self.active_trade["side"] == "BUY":
                        sl_price = entry - sl_distance
                        tp_price = entry + tp_distance

                        if price <= sl_price:
                            self.exchange.sell(self.symbol, 0.001)
                            await send_trade_alert(f"🛑 Stop-Loss הופעל (ATR={atr:.2f}) במחיר {price}")
                            self.active_trade = None

                        elif price >= tp_price:
                            self.exchange.sell(self.symbol, 0.001)
                            await send_trade_alert(f"🏁 Take-Profit הופעל (ATR={atr:.2f}) במחיר {price}")
                            self.active_trade = None

                await asyncio.sleep(60)
            except Exception as e:
                logging.error(f"❌ שגיאה במעקב סיכון: {e}")
                await asyncio.sleep(30)
