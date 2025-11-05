import asyncio
import logging
from exchange import Exchange
from strategies.smart_strategy import SmartStrategy
from utils.telegram_notifier import send_trade_alert
from utils.risk import RiskManager
from utils.position_size import PositionSizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ v5 Smart Edition הופעל...")

    exchange = Exchange(mode="DEMO")
    strategy = SmartStrategy(exchange, symbol="BTC/USDT")
    risk = RiskManager(exchange, symbol="BTC/USDT", atr_period=14, atr_mult_sl=1.5, atr_mult_tp=3.0)
    sizer = PositionSizer(exchange, symbol="BTC/USDT", risk_percent=1.0)

    asyncio.create_task(risk.monitor_trade())
    await send_trade_alert("✅ NeriyaBot Ultra+ v5 Smart Edition מחובר ל-Bybit Testnet ומוכן לפעולה")

    while True:
        try:
            signal = strategy.get_signal()

            if signal == "BUY":
                price = exchange.client.fetch_ticker("BTC/USDT")["last"]
                atr = risk.get_atr()
                stop_loss = price - (atr * 1.5)
                qty = sizer.calculate_position_size(price, stop_loss)

                order = exchange.buy("BTC/USDT", qty)
                if order:
                    risk.open_trade("BUY", price)
                    await send_trade_alert(f"🟢 קנייה חכמה נפתחה במחיר {price} עם גודל עסקה {qty} BTC")

            elif signal == "SELL":
                exchange.sell("BTC/USDT", 0.001)
                await send_trade_alert("🔴 מכירה חכמה בוצעה לפי אות רב-טווח")
                risk.active_trade = None

            await asyncio.sleep(300)
        except Exception as e:
            logging.error(f"❌ שגיאה בלולאה הראשית: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
