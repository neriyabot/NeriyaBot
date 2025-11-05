import asyncio
import logging
from exchange import Exchange
from strategies.rsi_ema_strategy import RSI_EMA_Strategy
from utils.telegram_notifier import send_trade_alert
from utils.risk import RiskManager
from utils.position_size import PositionSizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ v4 Adaptive Risk & Position Sizing Mode הופעל...")

    # חיבור ל-Bybit במצב DEMO
    exchange = Exchange(mode="DEMO")

    # הגדרת האסטרטגיה והניהול
    strategy = RSI_EMA_Strategy(exchange, symbol="BTC/USDT", timeframe="1h")
    risk = RiskManager(exchange, symbol="BTC/USDT", atr_period=14, atr_mult_sl=1.5, atr_mult_tp=3.0)
    sizer = PositionSizer(exchange, symbol="BTC/USDT", risk_percent=1.0)  # סיכון 1% מהיתרה לכל עסקה

    # הפעלת מנגנון ניהול סיכונים ברקע
    asyncio.create_task(risk.monitor_trade())

    await send_trade_alert("✅ NeriyaBot Ultra+ v4 הופעל ומוכן – כולל ATR ו-Position Size חכם")

    while True:
        try:
            signal = strategy.generate_signal()

            if signal == "BUY":
                # מקבל מחיר כניסה נוכחי
                current_price = exchange.client.fetch_ticker("BTC/USDT")["last"]

                # מחשב Stop-Loss לפי ATR נוכחי
                atr = risk.get_atr()
                stop_loss_price = current_price - (atr * 1.5)

                # מחשב גודל עסקה לפי אחוז סיכון
                qty = sizer.calculate_position_size(current_price, stop_loss_price)

                # ביצוע עסקה
                order = exchange.buy("BTC/USDT", qty)
                if order:
                    risk.open_trade("BUY", current_price)
                    await send_trade_alert(f"🟢 עסקת קנייה נפתחה ({qty} BTC) במחיר {current_price}")

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
