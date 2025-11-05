import asyncio
import logging
from exchange import Exchange
from utils.telegram_notifier import send_trade_alert
from strategies.rsi_ema_strategy import RSI_EMA_Strategy

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ v2 starting...")
    exchange = Exchange(mode="DEMO")
    strategy = RSI_EMA_Strategy(exchange, symbol="BTC/USDT", timeframe="1h")

    await send_trade_alert("✅ NeriyaBot Ultra+ v2 הופעל בהצלחה ומחובר ל-Testnet")

    while True:
        try:
            signal = strategy.generate_signal()

            if signal == "BUY":
                exchange.buy("BTC/USDT", 0.001)
                await send_trade_alert("🟢 עסקת קנייה נפתחה על BTC/USDT")

            elif signal == "SELL":
                exchange.sell("BTC/USDT", 0.001)
                await send_trade_alert("🔴 עסקת מכירה בוצעה על BTC/USDT")

            await asyncio.sleep(60 * 5)  # 5 דקות בין בדיקות

        except Exception as e:
            logging.error(f"❌ שגיאה בלולאה הראשית: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
