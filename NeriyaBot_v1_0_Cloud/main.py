import asyncio
import logging
from exchange import Exchange
from strategies.ai_predictive_strategy import AIPredictiveStrategy
from utils.telegram_notifier import send_trade_alert
from utils.risk import RiskManager
from utils.position_size import PositionSizer
from utils.sentiment import MarketSentiment

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ v8 AI Predictive Mode הופעל...")

    exchange = Exchange(mode="DEMO")
    strategy = AIPredictiveStrategy(exchange, symbol="BTC/USDT")
    risk = RiskManager(exchange, symbol="BTC/USDT", atr_period=14, atr_mult_sl=1.5, atr_mult_tp=3.0)
    sentiment = MarketSentiment()

    base_risk = 1.0
    adj_risk, msg = sentiment.get_adjusted_risk(base_risk)
    sizer = PositionSizer(exchange, symbol="BTC/USDT", risk_percent=adj_risk)

    await send_trade_alert(f"🤖 NeriyaBot Ultra+ v8 הופעל\n{msg}")

    asyncio.create_task(risk.monitor_trade())

    while True:
        try:
            signal = strategy.get_signal()
            price = exchange.client.fetch_ticker("BTC/USDT")["last"]
            atr = risk.get_atr()
            stop_loss = price - (atr * 1.5)
            qty = sizer.calculate_position_size(price, stop_loss)

            if signal == "BUY":
                order = exchange.buy("BTC/USDT", qty)
                if order:
                    risk.open_trade("BUY", price)
                    await send_trade_alert(f"🟢 קנייה לפי תחזית AI – מחיר: {price} | כמות: {qty} BTC")

            elif signal == "SELL":
                exchange.sell("BTC/USDT", 0.001)
                await send_trade_alert(f"🔴 מכירה לפי תחזית AI – מחיר נוכחי: {price}")
                risk.active_trade = None

            await asyncio.sleep(600)  # בדיקה כל 10 דקות
        except Exception as e:
            logging.error(f"❌ שגיאה בלולאה הראשית: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
