import os
import requests
import asyncio
import logging
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# לוג של העסקאות שנשלחות לטלגרם
TRADE_LOG = []
_last_update_id = 0


async def send_trade_alert(message: str):
    """
    שולח הודעה לטלגרם וגם שומר אותה בלוג העסקאות.
    את הפונקציה הזו אתה כבר משתמש בה בבוט – לא לשנות את הקריאות אליה.
    """
    if not TELEGRAM_TOKEN or not TELELEGRAM_CHAT_ID:
        logging.warning("⚠️ TELEGRAM_TOKEN או TELEGRAM_CHAT_ID לא מוגדרים, לא ניתן לשלוח הודעה.")
        return

    # לשמור בלוג העסקאות
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    TRADE_LOG.append(entry)
    # לא לשמור יותר מ-50 כדי שלא יתנפח
    if len(TRADE_LOG) > 50:
        del TRADE_LOG[:-50]

    try:
        requests.post(
            f"{API_URL}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=10,
        )
    except Exception as e:
        logging.error(f"❌ שגיאה בשליחת הודעה לטלגרם: {e}")


async def _handle_command(text: str, chat_id: int, exchange):
    """
    מטפל בפקודות שמגיעות מהטלגרם: /status, /balance, /trades
    """
    text = text.strip().lower()

    # /status
    if text.startswith("/status"):
        reply = "✅ NeriyaBot Ultra+ פעיל ומחובר ל-Testnet"

    # /balance
    elif text.startswith("/balance"):
        balance = exchange.get_balance()
        if balance and "total" in balance:
            usdt = balance["total"].get("USDT", 0)
            reply = f"💰 יתרת USDT נוכחית: {usdt}"
        else:
            reply = "❌ לא הצלחתי להביא את היתרה כרגע."

    # /trades
    elif text.startswith("/trades"):
        if not TRADE_LOG:
            reply = "אין עדיין עסקאות שמורות בלוג."
        else:
            last = TRADE_LOG[-5:]  # 5 האחרונות
            last = list(reversed(last))  # האחרונות למעלה
            reply = "🧾 5 העסקאות האחרונות:\n" + "\n".join(last)

    else:
        reply = "❓ פקודה לא מוכרת. נסה /status, /balance או /trades."

    try:
        requests.post(
            f"{API_URL}/sendMessage",
            data={"chat_id": chat_id, "text": reply},
            timeout=10,
        )
    except Exception as e:
        logging.error(f"❌ שגיאה בשליחת תשובה לפקודה: {e}")


async def start_command_listener(exchange):
    """
    מאזין לפקודות שמגיעות לבוט מהטלגרם באמצעות getUpdates.
    רץ כל הזמן בלולאה ברקע.
    """
    global _last_update_id

    if not TELEGRAM_TOKEN:
        logging.warning("⚠️ אין TELEGRAM_TOKEN, מאזין פקודות לא הופעל.")
        return

    logging.info("🤖 Telegram command listener started")

    while True:
        try:
            resp = requests.get(
                f"{API_URL}/getUpdates",
                params={"timeout": 20, "offset": _last_update_id + 1},
                timeout=25,
            )
            data = resp.json()

            if not data.get("ok"):
                await asyncio.sleep(3)
                continue

            for update in data.get("result", []):
                _last_update_id = update["update_id"]

                msg = update.get("message")
                if not msg:
                    continue

                text = msg.get("text")
                chat = msg.get("chat", {})
                chat_id = chat.get("id")

                if not text or not chat_id:
                    continue

                # רק פקודות שמתחילות ב-/
                if text.startswith("/"):
                    await _handle_command(text, chat_id, exchange)

        except Exception as e:
            logging.error(f"❌ שגיאה במאזין הפקודות: {e}")
            await asyncio.sleep(5)
