import asyncio
import logging
from exchange import Exchange
from utils.telegram_notifier import send_trade_alert, start_command_listener

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🚀 NeriyaBot Ultra+ starting up...")

    # חיבור ל-Bybit במצב DEMO
    exchange = Exchange(mode="DEMO")

    # להפעיל מאזין לפקודות טלגרם (/status, /balance, /trades)
    asyncio.create_task(start_command_listener(exchange))

    # לולאת הבוט (כמו שהיה לך כבר)
    while True:
        try:
            logging.info("🤖 Bot running... waiting for next signal")
            await send_trade_alert("✅ NeriyaBot Ultra+ פעיל ומחובר ל-Testnet")
            await asyncio.sleep(600)  # 10 דקות
        except Exception as e:
            logging.error(f"❌ שגיאה בלולאה הראשית: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
