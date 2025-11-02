import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def signal(df_sig: pd.DataFrame, df_trend: pd.DataFrame, cfg: dict):
    ema200 = EMAIndicator(close=df_trend["close"], window=200).ema_indicator()
    uptrend = df_trend["close"].iloc[-1] > ema200.iloc[-1]

    ema_f = EMAIndicator(close=df_sig["close"], window=cfg["common"]["ema_fast"]).ema_indicator()
    ema_s = EMAIndicator(close=df_sig["close"], window=cfg["common"]["ema_slow"]).ema_indicator()
    rsi = RSIIndicator(close=df_sig["close"], window=cfg["common"]["rsi_len"]).rsi()
    atr = AverageTrueRange(df_sig["high"], df_sig["low"], df_sig["close"], window=cfg["common"]["atr_len"]).average_true_range()

    last = df_sig["close"].iloc[-1]
    stop_dist = atr.iloc[-1] * cfg["common"]["atr_mult"]

    long_ok = (ema_f.iloc[-1] > ema_s.iloc[-1]) and (rsi.iloc[-1] > 50) and uptrend
    short_ok = (ema_f.iloc[-1] < ema_s.iloc[-1]) and (rsi.iloc[-1] < 50) and (not uptrend)

    if long_ok:
        return {"side": "BUY", "entry": float(last), "stop": float(last - stop_dist)}
    if short_ok:
        return {"side": "SELL", "entry": float(last), "stop": float(last + stop_dist)}
    return {"side": None, "entry": None, "stop": None}