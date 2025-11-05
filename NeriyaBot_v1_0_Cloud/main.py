import asyncio
import logging
from exchange import Exchange
from strategies.rsi_ema_strategy import RSI_EMA_Strategy
from utils.telegram_notifier import send_trade_alert
from utils.risk import RiskManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ v3 Adaptive Risk Mode הופעל...")
    exchange = Exchange(mode="DEMO")
    strategy = RSI_EMA_Strategy(exchange, symbol="BTC/USDT", timeframe="1h")
    risk = RiskManager(exchange, symbol="BTC/USDT", atr_period=14, atr_mult_sl=1.5, atr_mult_tp=3.0)

    # הפעלת מנגנון ניהול סיכונים ברקע
    asyncio.create_task(risk.monitor_trade())

    await send_trade_alert("✅ NeriyaBot Ultra+ v3 פעיל ומחובר ל-Testnet עם ניהול סיכונים חכם (ATR)")

    while True:
        try:
            signal = strategy.generate_signal()

            if signal == "BUY":
                order = exchange.buy("BTC/USDT", 0.001)
                if order:
                    entry = order["price"] if order.get("price") else exchange.client.fetch_ticker("BTC/USDT")["last"]
                    risk.open_trade("BUY", entry)
                    await send_trade_alert(f"🟢 עסקת קנייה נפתחה על {entry}")

            elif signal == "SELL":
                exchange.sell("BTC/USDT", 0.001)
                await send_trade_alert("🔴 עסקת מכירה בוצעה על BTC/USDT")
                risk.active_trade = None

            await asyncio.sleep(300)  # 5 דקות בין סריקות
        except Exception as e:
            logging.error(f"❌ שגיאה בלולאה הראשית: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
