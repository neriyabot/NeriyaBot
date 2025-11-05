import numpy as np
import pandas as pd
import logging

class SmartTrendStrategy:
    def __init__(self, symbol="BTC/USDT", timeframe="15m", limit=200):
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit

    def calculate_rsi(self, closes, period=14):
        """ מחשב RSI לפי סגירות נרות """
        delta = np.diff(closes)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(period).mean()
        avg_loss = pd.Series(loss).rolling(period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.values

    def calculate_ema(self, closes, period=20):
        """ מחשב ממוצע נע אקספוננציאלי """
        return pd.Series(closes).ewm(span=period, adjust=False).mean().values

    def generate_signal(self, candles):
        """
        מחזיר אות קנייה/מכירה חכם בהתאם ל־RSI, EMA ונפח המסחר.
        """
        try:
            closes = np.array([c[4] for c in candles], dtype=float)
            volumes = np.array([c[5] for c in candles], dtype=float)

            # חישוב RSI ו־EMA
            rsi = self.calculate_rsi(closes)
            ema_fast = self.calculate_ema(closes, period=20)
            ema_slow = self.calculate_ema(closes, period=50)

            # פילטר מגמה חכם: מזהה עלייה/ירידה אמיתית
            trend_strength = ema_fast[-1] - ema_slow[-1]
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]

            logging.info(f"📊 {self.symbol} | RSI: {rsi[-1]:.2f} | Trend: {trend_strength:.3f} | Volume: {current_volume/avg_volume:.2f}x")

            # תנאים לקנייה
            if (
                rsi[-1] > 55
                and ema_fast[-1] > ema_slow[-1]
                and trend_strength > 0
                and current_volume > avg_volume * 1.1
            ):
                logging.info("✅ אות קנייה מזוהה (BUY)")
                return "BUY"

            # תנאים למכירה
            elif (
                rsi[-1] < 45
                and ema_fast[-1] < ema_slow[-1]
                and trend_strength < 0
                and current_volume > avg_volume * 1.1
            ):
                logging.info("❌ אות מכירה מזוהה (SELL)")
                return "SELL"

            # אין אות ברור
            return None

        except Exception as e:
            logging.error(f"שגיאה באסטרטגיה: {e}")
            return None
