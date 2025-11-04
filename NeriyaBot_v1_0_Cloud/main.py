import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.token or not self.chat_id:
            raise ValueError("❌ Missing Telegram credentials (TOKEN or CHAT_ID).")

    def send_message(self, message: str):
        """שולח הודעה לטלגרם"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print(f"📩 הודעה נשלחה לטלגרם: {message}")
            else:
                print(f"⚠️ שגיאה בשליחת הודעה לטלגרם: {response.text}")
        except Exception as e:
            print(f"❌ שגיאה בחיבור לטלגרם: {e}")
