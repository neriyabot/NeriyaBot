import asyncio
from utils.exchange import Exchange
from utils.telegram_notifier import run_telegram_bot
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    try:
        logging.info("🚀 NeriyaBot starting...")
        exchange = Exchange(mode="DEMO")
        logging.info("✅ Connected to Bybit successfully!")
        # אפשר להוסיף כאן בהמשך לולאת מסחר או אסטרטגיה
        while True:
            await asyncio.sleep(10)
    except Exception as e:
        logging.error(f"❌ Error in main loop: {e}")

if __name__ == "__main__":
    import threading
    telegram_thread = threading.Thread(target=run_telegram_bot)
    telegram_thread.start()
    asyncio.run(main())
