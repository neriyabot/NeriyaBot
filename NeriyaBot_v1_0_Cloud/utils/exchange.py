import os
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

load_dotenv()

class BybitExchange:
    """
    עטיפה קטנה ל-Bybit (Spot) עם ממשק דומה לבייננס:
      - get_klines(symbol, interval, limit)
      - get_balance(asset='USDT')
      - market_order(symbol, side, qty)
    """

    def __init__(self, recv_window=5000):
        self.api_key = os.getenv("BYBIT_API_KEY", "") or ""
        self.api_secret = os.getenv("BYBIT_API_SECRET", "") or ""
        mode = (os.getenv("BOT_MODE", "DEMO") or "DEMO").upper()

        # DEMO => testnet=True
        self.testnet = True if mode == "DEMO" else False

        # חשבון מסחר Spot ב-Bybit (Unified Trading HTTP)
        self.client = HTTP(
            testnet=self.testnet,
            api_key=self.api_key,
            api_secret=self.api_secret,
            recv_window=recv_window,
        )
        # קטגוריה למסחר SPOT ב-Bybit v5
        self.category = "spot"

    # interval נכנס בסגנון "5m" / "15m" וכו'. Bybit צריך מספר בדקות (ללא 'm')
    @staticmethod
    def _interval_to_bybit(interval_str: str) -> str:
        s = interval_str.strip().lower()
        if s.endswith("m"):
            return s[:-1]               # "5m" -> "5"
        if s.endswith("h"):
            return str(int(s[:-1]) * 60) # "1h" -> "60"
        if s.endswith("d"):
            return str(int(s[:-1]) * 60 * 24) # "1d" -> "1440"
        return s

    def get_klines(self, symbol: str, interval: str = "5m", limit: int = 500):
        """
        מחזיר רשימה בסגנון של Binance kline:
        [ open_time_ms, open, high, low, close, volume ]
        """
        bybit_interval = self._interval_to_bybit(interval)
        res = self.client.get_kline(
            category=self.category,
            symbol=symbol,
            interval=bybit_interval,
            limit=limit
        )
        # מבנה תשובה: res["result"]["list"] = [["start","open","high","low","close","volume",...], ...]
        rows = []
        data = (res or {}).get("result", {}).get("list", []) or []
        # Bybit מחזיר בסדר מהחדש לישן – נהפוך לישן->חדש כמו בבייננס
        data = list(reversed(data))
        for r in data:
            # r: [startTime, open, high, low, close, volume, ...]
            start_ms = int(r[0])
            o = float(r[1]); h = float(r[2]); l = float(r[3]); c = float(r[4]); v = float(r[5])
            rows.append([start_ms, o, h, l, c, v])
        return rows

    def get_balance(self, asset: str = "USDT") -> float:
        """
        יתרת SPOT ל-asset. אם אין רשומה – מחזיר 0.0
        """
        res = self.client.get_wallet_balance(accountType="SPOT")
        # res["result"]["list"] => [{ "coin":[{"coin":"USDT","walletBalance":"...","availableToWithdraw":"..."}], ... }]
        coins = []
        try:
            lst = (res or {}).get("result", {}).get("list", []) or []
            if lst:
                coins = lst[0].get("coin", []) or []
        except Exception:
            coins = []
        for c in coins:
            if c.get("coin", "").upper() == asset.upper():
                # ניקח את ה-balance הזמין
                val = c.get("availableToWithdraw") or c.get("walletBalance") or "0"
                try:
                    return float(val)
                except Exception:
                    return 0.0
        return 0.0

    def market_order(self, symbol: str, side: str, qty: float):
        """
        הזמנת Market ב-SPOT.
        side: 'BUY' או 'SELL'
        qty: כמות ביחידות המטבע הנקנה/נמכר (למשל BTC)
        """
        side_clean = side.strip().upper()
        if side_clean not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")
        return self.client.place_order(
            category=self.category,
            symbol=symbol,
            side="Buy" if side_clean == "BUY" else "Sell",
            orderType="Market",
            qty=str(qty)  # Bybit מצפה למחרוזת
        )
