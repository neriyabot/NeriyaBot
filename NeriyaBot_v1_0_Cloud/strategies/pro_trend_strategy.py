# strategies/pro_trend_strategy.py

from collections import defaultdict, deque
from typing import Dict, Deque, Literal

Signal = Literal["BUY", "SELL", "HOLD"]


class ProTrendStrategy:
    """
    אסטרטגיית מגמה חכמה:
    - מחשבת ממוצעים נעים (EMA)
    - מזהה מגמה חיובית או שלילית
    - קובעת BUY / SELL / HOLD
    """

    def __init__(
        self,
        symbols,
        risk_per_trade: float = 0.05,
        take_profit_pct: float = 0.06,
        stop_loss_pct: float = 0.03,
        short_window: int = 20,
        long_window: int = 50,
    ):
        self.symbols = symbols
        self.risk_per_trade = risk_per_trade
        self.take_profit_pct = take_profit_pct
        self.stop_loss_pct = stop_loss_pct
        self.short_window = short_window
        self.long_window = long_window

        # היסטוריית מחירים לכל מטבע
        self.price_history: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=self.long_window)
        )

        # פוזיציות פתוחות
        self.open_positions: Dict[str, Dict] = {}

    # ---------- חישוב מגמות ----------

    def update_price(self, symbol: str, price: float):
        """מעדכן את מחיר המטבע"""
        self.price_history[symbol].append(price)

    def _moving_average(self, values, window) -> float:
        if len(values) < window:
            return 0.0
        return sum(list(values)[-window:]) / window

    def get_trend_signal(self, symbol: str) -> Signal:
        """בודק אם יש מגמה לונג (BUY) או שורט (SELL)"""
        prices = self.price_history[symbol]
        if len(prices) < self.long_window:
            return "HOLD"

        short_ma = self._moving_average(prices, self.short_window)
        long_ma = self._moving_average(prices, self.long_window)

        threshold = 0.001  # 0.1% הפרש כדי למנוע רעש

        if short_ma > long_ma * (1 + threshold):
            return "BUY"
        elif short_ma < long_ma * (1 - threshold):
            return "SELL"
        else:
            return "HOLD"

    # ---------- ניהול עסקאות ----------

    def should_open_position(self, symbol: str, signal: Signal) -> bool:
        pos = self.open_positions.get(symbol)
        if pos is None:
            return signal in ("BUY", "SELL")
        if pos["side"] == signal:
            return False
        return True

    def get_position_size_usdt(self, total_balance_usdt: float) -> float:
        """מחשב גודל עסקה לפי אחוז מהיתרה"""
        return total_balance_usdt * self.risk_per_trade

    def register_open_position(self, symbol: str, side: Signal, entry_price: float, size_usdt: float):
        if side not in ("BUY", "SELL"):
            return
        self.open_positions[symbol] = {
            "side": side,
            "entry_price": entry_price,
            "size_usdt": size_usdt,
        }

    def check_exit(self, symbol: str, current_price: float):
        """בודק אם צריך לצאת מהעסקה לפי טייק-פרופיט / סטופ-לוס"""
        pos = self.open_positions.get(symbol)
        if not pos:
            return None

        side = pos["side"]
        entry = pos["entry_price"]

        if side == "BUY":
            if current_price <= entry * (1 - self.stop_loss_pct):
                return "SL"
            if current_price >= entry * (1 + self.take_profit_pct):
                return "TP"

        elif side == "SELL":
            if current_price >= entry * (1 + self.stop_loss_pct):
                return "SL"
            if current_price <= entry * (1 - self.take_profit_pct):
                return "TP"

        return None

    def close_position(self, symbol: str):
        """סוגר פוזיציה מהזיכרון"""
        if symbol in self.open_positions:
            del self.open_positions[symbol]
