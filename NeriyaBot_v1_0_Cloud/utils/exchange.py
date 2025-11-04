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

    def connect(self):
        try:
            print("🌐 Connecting to Bybit...")
            balance = self.client.get_wallet_balance(accountType="UNIFIED")
            print("✅ Connection successful!")
            return balance
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return None

    def get_balance(self):
        try:
            print("🔄 Fetching Bybit account balance...")
            balance = self.client.get_wallet_balance(accountType="UNIFIED")
            coins = balance["result"]["list"][0]["coin"]
            usdt_balance = 0.0
            for coin in coins:
                if coin["coin"] == "USDT":
                    usdt_balance = float(coin["walletBalance"])
                    break

            print(f"💰 Balance detected: {usdt_balance} USDT")
            return usdt_balance
        except Exception as e:
            print(f"❌ Failed to fetch balance: {e}")
            return 0.0
def get_last_price(self, symbol: str) -> float:
        """
        מחזיר את המחיר האחרון של המטבע.
        symbol לדוגמה: 'BTCUSDT'
        """
        resp = self.client.get_tickers(
            category="spot",
            symbol=symbol
        )
        price_str = resp["result"]["list"][0]["lastPrice"]
        return float(price_str)

    def create_market_order(self, symbol: str, side: str, quote_amount_usdt: float):
        """
        יוצר פקודת שוק לפי סכום בדולרים (USDT).
        side: 'BUY' או 'SELL'
        quote_amount_usdt – כמה דולרים להשקיע/למכור.
        """
        price = self.get_last_price(symbol)
        qty = quote_amount_usdt / price
        qty = round(qty, 4)

        order = self.client.create_order(
            category="spot",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty)
        )
        return order
