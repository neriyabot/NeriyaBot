import logging
from utils.telegram_notifier import send_trade_alert

class RiskManager:
    def __init__(self, exchange, symbol="BTC/USDT", stop_loss_pct=2.0, take_profit_pct=4.0):
        self.exchange = exchange
        self.symbol = symbol
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.active_trade = None  # {"side": "BUY", "entry": float}

    def open_trade(self, side: str, entry_price: float):
        self.active_trade = {"side": side, "entry": entry_price}
        logging.info(f"🎯 נפתחה עסקה {side} במחיר {entry_price}")

    async def monitor_trade(self):
        """
        רץ בלולאה ברקע ובודק כל 30 שניות אם המחיר חצה את גבולות הסיכון.
        """
        import asyncio
        while True:
            try:
                if self.active_trade:
                    ticker = self.exchange.client.fetch_ticker(self.symbol)
                    price = ticker["last"]
                    entry = self.active_trade["entry"]

                    if self.active_trade["side"] == "BUY":
                        sl_price = entry * (1 - self.stop_loss_pct / 100)
                        tp_price = entry * (1 + self.take_profit_pct / 100)
                        if price <= sl_price:
                            self.exchange.sell(self.symbol, 0.001)
                            await send_trade_alert(f"🛑 Stop-Loss הופעל במחיר {price}")
                            self.active_trade = None
                        elif price >= tp_price:
                            self.exchange.sell(self.symbol, 0.001)
                            await send_trade_alert(f"🏁 Take-Profit הופעל במחיר {price}")
                            self.active_trade = None
                await asyncio.sleep(30)
            except Exception as e:
                logging.error(f"❌ שגיאה במעקב סיכון: {e}")
                await asyncio.sleep(30)
