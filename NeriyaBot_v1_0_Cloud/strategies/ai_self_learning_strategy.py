import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

class AISelfLearningStrategy:
    """
    בוט חיזוי שמתעדכן לבד אחרי כל עסקה (Online Learning)
    """

    def __init__(self, exchange, symbol="BTC/USDT"):
        self.exchange = exchange
        self.symbol = symbol
        self.model = SGDClassifier(loss="log_loss", learning_rate="optimal")
        self.scaler = StandardScaler()
        self.trained = False
        self.success_history = []
        self.max_history = 20  # כמות עסקאות אחרונות למעקב ביצועים

    def get_data(self, timeframe="1h", limit=200):
        candles = self.exchange.client.fetch_ohlcv(self.symbol, timeframe, limit=limit)
        df = pd.DataFrame(candles, columns=["time","open","high","low","close","volume"])
        df["close"] = df["close"].astype(float)
        return df

    def prepare_features(self, df):
        df["returns"] = df["close"].pct_change()
        df["ema_fast"] = df["close"].ewm(span=9).mean()
        df["ema_slow"] = df["close"].ewm(span=21).mean()
        df["rsi"] = self.compute_rsi(df)
        df.dropna(inplace=True)
        X = df[["returns", "ema_fast", "ema_slow", "rsi"]]
        y = (df["close"].shift(-1) > df["close"]).astype(int)
        return X[:-1], y[:-1]

    def compute_rsi(self, df, period=14):
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def initial_train(self, df):
        X, y = self.prepare_features(df)
        X_scaled = self.scaler.fit_transform(X)
        self.model.partial_fit(X_scaled, y, classes=[0,1])
        self.trained = True
        logging.info("🤖 מודל Self-Learning אומן לראשונה על נתוני עבר")

    def predict_signal(self):
        df = self.get_data()
        if not self.trained:
            self.initial_train(df)

        X, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        prob_up = self.model.predict_proba(X_scaled)[-1][1]
        logging.info(f"📈 סיכוי לעלייה: {prob_up*100:.2f}%")

        # גישה חכמה לפי דיוק אחרון
        confidence_threshold = 0.6
        accuracy = self.get_accuracy()
        if accuracy > 0.75:
            confidence_threshold = 0.55
        elif accuracy < 0.5:
            confidence_threshold = 0.7

        if prob_up > confidence_threshold:
            return "BUY", prob_up
        elif prob_up < (1 - confidence_threshold):
            return "SELL", prob_up
        else:
            return None, prob_up

    def update_after_trade(self, was_profitable):
        """עדכון המודל לפי הצלחה או כישלון"""
        self.success_history.append(int(was_profitable))
        if len(self.success_history) > self.max_history:
            self.success_history.pop(0)
        acc = self.get_accuracy()
        logging.info(f"📊 דיוק נוכחי: {acc*100:.1f}%")

    def get_accuracy(self):
        if not self.success_history:
            return 0.5
        return sum(self.success_history) / len(self.success_history)
