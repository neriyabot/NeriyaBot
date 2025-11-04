import os
import ccxt
import logging
from dotenv import load_dotenv

load_dotenv()

class Exchange:
    def __init__(self, mode="DEMO"):
        self.mode = mode
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ Missing API keys! Check .env or Render Environment Variables.")

        self.client = ccxt.bybit({
            "apiKey": self.api_key,
            "secret": self.api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"}
        })

        if mode == "DEMO":
            self.client.set_sandbox_mode(True)

        logging.info(f"✅ Connected to Bybit ({self.mode} mode)")

    def get_balance(self):
        try:
            balance = self.client.fetch_balance()
            return balance
        except Exception as e:
            logging.error(f"❌ Error fetching balance: {e}")
            return None
