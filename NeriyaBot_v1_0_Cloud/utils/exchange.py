import os
from binance.spot import Spot as Client
from dotenv import load_dotenv

load_dotenv()

class BinanceExchange:
    def __init__(self, recv_window=5000):
        self.api_key = os.getenv("BINANCE_API_KEY") or ""
        self.api_secret = os.getenv("BINANCE_API_SECRET") or ""
        mode = os.getenv("BOT_MODE", "DEMO").upper()

        if mode == "DEMO":
            print("[MODE] Running on Binance TESTNET (demo mode)")
            self.client = Client(api_key=self.api_key, api_secret=self.api_secret,
                                 base_url="https://testnet.binance.vision")
        else:
            print("[MODE] Running on Binance LIVE (real mode)")
            self.client = Client(api_key=self.api_key, api_secret=self.api_secret)

        self.recv_window = recv_window

    def get_klines(self, symbol: str, interval: str = "5m", limit: int = 500):
        return self.client.klines(symbol=symbol, interval=interval, limit=limit)

    def get_balance(self, asset="USDT"):
        balances = self.client.user_asset()
        for b in balances:
            if b["asset"] == asset:
                return float(b["free"])
        return 0.0
