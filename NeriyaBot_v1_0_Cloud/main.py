import asyncio
import logging
from exchange import Exchange
from utils.telegram_notifier import send_trade_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ starting up...")

    # יצירת חיבור ל-Bybit במצב DEMO
    exchange = Exchange(mode="DEMO")

    # לולאת הרצה אינסופית
    while True:
        try:
            # כאן תוכל לשלב לוגיקת מסחר (RSI, EMA וכו’)
            logging.info("🤖 Bot running... waiting for next signal")

            # שלח עדכון לטלגרם כל 10 דקות (לדוגמה)
            await send_trade_alert("✅ NeriyaBot Ultra+ פעיל ומחובר ל-Testnet")

            await asyncio.sleep(600)  # 10 דקות
        except Exception as e:
            logging.error(f"❌ שגיאה בלולאה הראשית: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
