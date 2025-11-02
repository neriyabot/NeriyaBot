import pandas as pd
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator

def signal(df: pd.DataFrame, cfg: dict):
    ema50 = EMAIndicator(close=df["close"], window=50).ema_indicator()
    ema200 = EMAIndicator(close=df["close"], window=200).ema_indicator()
    rsi = RSIIndicator(close=df["close"], window=cfg["common"]["rsi_len"]).rsi()
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=cfg["common"]["atr_len"]).average_true_range()

    last = df["close"].iloc[-1]
    stop_dist = atr.iloc[-1] * cfg["common"]["atr_mult"]

    if ema50.iloc[-1] > ema200.iloc[-1] and rsi.iloc[-1] > 50:
        return {"side": "BUY", "entry": float(last), "stop": float(last - stop_dist)}
    if ema50.iloc[-1] < ema200.iloc[-1] and rsi.iloc[-1] < 50:
        return {"side": "SELL", "entry": float(last), "stop": float(last + stop_dist)}
    return {"side": None, "entry": None, "stop": None}