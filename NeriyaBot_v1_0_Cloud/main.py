import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from utils.exchange import Exchange
from utils.daily_report import send_daily_report
from utils.telegram_notifier import run_telegram_bot

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

MODE = "DEMO"  # אפשר לשנות ל-REAL בהמשך


async def main_loop():
    """לולאת המסחר הראשית – מפעילה את NeriyaBot Ultra+ ואת הדוח היומי"""
    logging.info("🚀 NeriyaBot Ultra+ התחיל לעבוד...")

    # אתחול האקסצ'יינג'
    exchange = Exchange(mode=MODE)

    # מתזמן לדוח יומי ב-23:00 לפי שעון ישראל
    scheduler = BackgroundScheduler(timezone="Asia/Jerusalem")
    scheduler.add_job(send_daily_report, "cron", hour=23, minute=0)
    scheduler.start()
    logging.info("📅 דוח יומי מתוזמן אוטומטית כל יום ב-23:00 (Asia/Jerusalem).")

    # הרצת לולאת המסחר (async)
    await exchange.run()


if __name__ == "__main__":
    import threading

    # מפעילים את הבוט טלגרם בת'רד נפרד
    tg_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    tg_thread.start()
    logging.info("📲 בוט הטלגרם הופעל.")

    # מפעילים את לולאת המסחר הראשית
    asyncio.run(main_loop())
