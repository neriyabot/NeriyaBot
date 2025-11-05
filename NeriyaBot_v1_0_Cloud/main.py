import asyncio
import logging
from exchange import Exchange
from strategies.smart_trend_strategy import SmartTrendStrategy
from utils.telegram_notifier import send_trade_alert
from utils.risk import RiskManager
from utils.position_size import PositionSizer
from utils.sentiment import MarketSentiment

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ v7 Smart Trend & Dip Hunter Mode הופעל...")

    exchange = Exchange(mode="DEMO")
    strategy = SmartTrendStrategy(exchange, symbol="BTC/USDT")
    risk = RiskManager(exchange, symbol="BTC/USDT", atr_period=14, atr_mult_sl=1.5, atr_mult_tp=3.0)
    sentiment = MarketSentiment()

    base_risk = 1.0
    adj_risk, msg = sentiment.get_adjusted_risk(base_risk)
    sizer = PositionSizer(exchange, symbol="BTC/USDT", risk_percent=adj_risk)

    await send_trade_alert(f"📊 מצב שוק: {msg}")
    asyncio.create_task(risk.monitor_trade())

    await send_trade_alert("✅ NeriyaBot Ultra+ v7 פועל במצב חכם לזיהוי ירידות ומגמות")

    while True:
        try:
            signal = strategy.get_signal()

            price = exchange.client.fetch_ticker("BTC/USDT")["last"]
            atr = risk.get_atr()
            stop_loss = price - (atr * 1.5)
            qty = sizer.calculate_position_size(price, stop_loss)

            if signal == "BUY_DIP":
                order = exchange.buy("BTC/USDT", qty)
                if order:
                    risk.open_trade("BUY", price)
                    await send_trade_alert(f"💎 קנייה חכמה בירידה – מחיר: {price}, כמות: {qty} BTC")

            elif signal == "BUY_TREND":
                order = exchange.buy("BTC/USDT", qty)
                if order:
                    risk.open_trade("BUY", price)
                    await send_trade_alert(f"🟢 קנייה בהמשך מגמה – מחיר: {price}, כמות: {qty} BTC")

            elif signal == "SELL":
                exchange.sell("BTC/USDT", 0.001)
                await send_trade_alert("🔴 מכירה אוטומטית בוצעה לפי מגמה שלילית")
                risk.active_trade = None

            await asyncio.sleep(300)
        except Exception as e:
            logging.error(f"❌ שגיאה בלולאה הראשית: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
