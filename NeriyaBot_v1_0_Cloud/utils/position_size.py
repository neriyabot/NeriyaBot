import logging

class PositionSizer:
    """
    מחלקה לחישוב גודל עסקה חכם לפי אחוז סיכון מהיתרה הכוללת.
    לדוגמה: אם אתה רוצה לסכן רק 1% מההון הכולל שלך בכל עסקה.
    """

    def __init__(self, exchange, symbol="BTC/USDT", risk_percent=1.0):
        self.exchange = exchange
        self.symbol = symbol
        self.risk_percent = risk_percent

    def get_account_balance(self):
        """ מביא יתרת USDT מהחשבון """
        try:
            balance = self.exchange.get_balance()
            usdt = balance["total"].get("USDT", 0)
            return float(usdt)
        except Exception as e:
            logging.error(f"❌ שגיאה בקבלת יתרת החשבון: {e}")
            return 0.0

    def calculate_position_size(self, entry_price: float, stop_loss_price: float):
        """
        מחשב את כמות המטבעות לקנייה לפי אחוז הסיכון.
        risk_amount = balance * (risk_percent / 100)
        position_size = risk_amount / (entry - stop_loss)
        """
        balance = self.get_account_balance()
        if balance <= 0:
            logging.warning("⚠️ יתרה לא זמינה, לא ניתן לחשב גודל עסקה.")
            return 0.001  # ברירת מחדל קטנה

        risk_amount = balance * (self.risk_percent / 100)
        stop_distance = abs(entry_price - stop_loss_price)
        if stop_distance == 0:
            return 0.001

        position_size = risk_amount / stop_distance
        logging.info(f"📐 גודל עסקה מחושב: {position_size:.6f} BTC לסיכון של {self.risk_percent}%")
        return round(position_size, 6)
