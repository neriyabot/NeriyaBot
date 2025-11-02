import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def signal(df: pd.DataFrame, cfg: dict):
    ema_f = EMAIndicator(close=df["close"], window=cfg["common"]["ema_fast"]).ema_indicator()
    ema_s = EMAIndicator(close=df["close"], window=cfg["common"]["ema_slow"]).ema_indicator()
    rsi = RSIIndicator(close=df["close"], window=cfg["common"]["rsi_len"]).rsi()
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=cfg["common"]["atr_len"]).average_true_range()

    last = df["close"].iloc[-1]
    stop_dist = atr.iloc[-1] * cfg["common"]["atr_mult"]

    if ema_f.iloc[-1] > ema_s.iloc[-1] and rsi.iloc[-1] > 55:
        return {"side": "BUY", "entry": float(last), "stop": float(last - stop_dist)}
    if ema_f.iloc[-1] < ema_s.iloc[-1] and rsi.iloc[-1] < 45:
        return {"side": "SELL", "entry": float(last), "stop": float(last + stop_dist)}
    return {"side": None, "entry": None, "stop": None}