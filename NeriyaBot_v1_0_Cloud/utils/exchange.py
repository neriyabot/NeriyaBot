from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()


class Exchange:
    def __init__(self, mode):
        self.mode = mode
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API keys not found. Make sure BYBIT_API_KEY and BYBIT_API_SECRET are set.")

        self.client = HTTP(
            testnet=True if mode == "DEMO" else False,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

        print("✅ Bybit client initialized successfully!")

    def get_balance(self):
        """בדיקת יתרה"""
        try:
            balance = self.client.get_wallet_balance(accountType="UNIFIED")
            return balance
        except Exception as e:
            print(f"⚠️ שגיאה בקריאת יתרה: {e}")
            return None

    def create_market_order(self, symbol: str, side: str, quote_amount_usdt: float):
        """מבצע פקודת קנייה או מכירה בשוק"""
        try:
            order = self.client.place_order(
                category="spot",
                symbol=symbol,
                side=side,
                orderType="Market",
                qty=quote_amount_usdt,
            )
            print(f"✅ פקודת {side} נשלחה בהצלחה ({symbol})")
            return order
        except Exception as e:
            print(f"⚠️ שגיאה בביצוע פקודת {side} עבור {symbol}: {e}")
            return None
