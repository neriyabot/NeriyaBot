import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class AIPredictiveStrategy:
    """
    אסטרטגיה חכמה המשתמשת במודל AI פשוט כדי לנבא תנועות מחיר
    """

    def __init__(self, exchange, symbol="BTC/USDT"):
        self.exchange = exchange
        self.symbol = symbol
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.is_trained = False

    def get_data(self, timeframe="1h", limit=200):
        candles = self.exchange.client.fetch_ohlcv(self.symbol, timeframe, limit=limit)
        df = pd.DataFrame(candles, columns=["time","open","high","low","close","volume"])
        df["close"] = df["close"].astype(float)
        return df

    def prepare_features(self, df):
        """מכין תכונות עבור המודל (features)"""
        df["returns"] = df["close"].pct_change()
        df["ema_fast"] = df["close"].ewm(span=9).mean()
        df["ema_slow"] = df["close"].ewm(span=21).mean()
        df["rsi"] = self.compute_rsi(df)
        df.dropna(inplace=True)

        X = df[["returns", "ema_fast", "ema_slow", "rsi"]]
        y = (df["close"].shift(-1) > df["close"]).astype(int)  # 1 אם המחיר עלה
        X, y = X[:-1], y[:-1]
        return X, y

    def compute_rsi(self, df, period=14):
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def train_model(self, df):
        X, y = self.prepare_features(df)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        logging.info("🤖 מודל ה-AI אומן בהצלחה על נתוני המחירים האחרונים.")

    def predict_next_move(self, df):
        if not self.is_trained:
            self.train_model(df)

        X, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        prob = self.model.predict_proba(X_scaled)[-1][1]  # סיכוי לעלייה
        logging.info(f"📈 סבירות לעלייה לפי AI: {prob*100:.2f}%")
        return prob

    def get_signal(self):
        df = self.get_data("1h")
        prob_up = self.predict_next_move(df)

        # קביעת אותות לפי הסיכוי
        if prob_up > 0.7:
            logging.info("🟢 AI מנבא עליה – כניסה לקנייה")
            return "BUY"
        elif prob_up < 0.3:
            logging.info("🔴 AI מנבא ירידה – כניסה למכירה")
            return "SELL"
        else:
            logging.info("⚪ AI לא בטוח – אין עסקה כרגע")
            return None
