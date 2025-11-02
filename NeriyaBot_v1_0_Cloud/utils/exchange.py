import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

class BinanceWrap:
    def __init__(self, recv_window=5000):
        self.api_key = os.getenv("BINANCE_API_KEY") or ""
        self.api_secret = os.getenv("BINANCE_API_SECRET") or ""
        self.client = Client(self.api_key, self.api_secret)
        self.client.API_URL = 'https://api.binance.com'
        self.recv_window = recv_window

    def get_klines(self, symbol: str, interval: str="5m", limit: int=500):
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def get_balance(self, asset="USDT"):
        b = self.client.get_asset_balance(asset=asset)
        return float(b["free"])

    def market_order(self, symbol: str, side: str, qty: float):
        # LIVE orders. Be careful! Only used if mode == LIVE
        order = self.client.create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=qty,
            recvWindow=self.recv_window
        )
        return order