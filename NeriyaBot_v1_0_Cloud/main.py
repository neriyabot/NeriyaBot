import os
import logging
import ccxt
from dotenv import load_dotenv

load_dotenv()

class Exchange:
    def __init__(self, mode):
        self.mode = mode
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API keys missing. Please set BYBIT_API_KEY and BYBIT_API_SECRET")

        # הגדרת חיבור ל-Bybit Testnet או ל-Bybit אמיתי בהתאם למצב
        if mode == "DEMO":
            logging.info("🧪 Connecting to Bybit Testnet...")
            self.client = ccxt.bybit({
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
                "urls": {"api": "https://api-testnet.bybit.com"},  # ✅ משתמש בשרת Testnet אמין
            })
            self.client.set_sandbox_mode(True)
        else:
            logging.info("💰 Connecting to Bybit LIVE environment...")
            self.client = ccxt.bybit({
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
                "urls": {"api": "https://api.bybit.com"},  # ✅ שרת ה-LIVE הרגיל
            })

        self.positions = {}
        self.trade_log = []
        logging.info("✅ NeriyaBot Ultra+ connected successfully!")
