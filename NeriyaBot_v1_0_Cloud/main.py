import os, time, threading, yaml, traceback, datetime as dt
import pandas as pd
from flask import Flask, jsonify
from dotenv import load_dotenv
from ta.volatility import AverageTrueRange

from utils.logger import log_print, append_csv
from utils.risk import position_size_from_risk, hit_daily_loss_limit
from utils.exchange import BinanceExchange

import strategies.scalping as strat_scalp
import strategies.trend as strat_trend
import strategies.swing as strat_swing

load_dotenv()
APP = Flask(__name__)

def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

CFG = load_config()
STATE = {
    "mode": CFG["mode"],
    "equity_usdt": CFG["initial_balance_usdt"] if CFG["mode"] == "DEMO" else 0.0,
    "equity_start_of_day": CFG["initial_balance_usdt"] if CFG["mode"] == "DEMO" else 0.0,
    "positions": {},
    "last_day": dt.datetime.utcnow().strftime("%Y-%m-%d"),
    "trades_csv": "trades.csv"
}

BIN = BinanceWrap()

def klines_to_df(kl):
    cols = ["open_time","open","high","low","close","volume",
            "close_time","qav","num_trades","taker_base","taker_quote","ignore"]
    df = pd.DataFrame(kl, columns=cols)
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    return df[["open_time","high","low","close","volume"]]

def get_df(symbol, interval="5m", limit=500):
    kl = BIN.get_klines(symbol, interval, limit)
    return klines_to_df(kl)

def pick_strategy(df_sig, df_trd, cfg):
    mode = cfg["strategy"]["mode"]
    if mode == "scalping":
        return strat_scalp.signal(df_sig, cfg["strategy"])
    if mode == "trend":
        return strat_trend.signal(df_sig, df_trd, cfg["strategy"])
    if mode == "swing":
        return strat_swing.signal(df_trd, cfg["strategy"])

    # Auto: choose by volatility level (ATR%)
    atr = AverageTrueRange(df_sig["high"], df_sig["low"], df_sig["close"], window=cfg["strategy"]["common"]["atr_len"]).average_true_range()
    vol_pct = float(100.0 * atr.iloc[-1] / max(df_sig["close"].iloc[-1], 1e-9))
    if vol_pct >= 0.7:
        return strat_scalp.signal(df_sig, cfg["strategy"])
    elif vol_pct >= 0.3:
        return strat_trend.signal(df_sig, df_trd, cfg["strategy"])
    else:
        return strat_swing.signal(df_trd, cfg["strategy"])

def manage_position(symbol, price, cfg, atr_now):
    pos = STATE["positions"].get(symbol)
    if not pos: return

    # partial TPs
    tiers = cfg["strategy"]["take_profit"]["tiers"]
    for i, t in enumerate(tiers):
        if pos["filled_tiers"][i]: continue
        rr = t["rr"]
        if pos["side"] == "BUY":
            target = pos["entry"] + rr * pos["risk_per_unit"]
            if price >= target:
                qty_to_close = pos["qty"] * (t["qty_pct"] / 100.0)
                pnl = qty_to_close * (price - pos["entry"])
                STATE["equity_usdt"] += pnl
                pos["qty"] -= qty_to_close
                pos["filled_tiers"][i] = True
                log_print(f"{symbol} TP{rr}R filled: +{pnl:.2f} USDT (DEMO)")
        else:
            target = pos["entry"] - rr * pos["risk_per_unit"]
            if price <= target:
                qty_to_close = pos["qty"] * (t["qty_pct"] / 100.0)
                pnl = qty_to_close * (pos["entry"] - price)
                STATE["equity_usdt"] += pnl
                pos["qty"] -= qty_to_close
                pos["filled_tiers"][i] = True
                log_print(f"{symbol} TP{rr}R filled: +{pnl:.2f} USDT (DEMO)")

    # trailing stop
    trl_cfg = cfg["strategy"]["take_profit"]["trailing"]
    if trl_cfg["enable"]:
        trigger = trl_cfg["trigger_rr"] * pos["risk_per_unit"]
        trail = trl_cfg["trail_atr_mult"] * atr_now
        if pos["side"] == "BUY" and price >= pos["entry"] + trigger:
            pos["stop"] = max(pos["stop"], price - trail)
        if pos["side"] == "SELL" and price <= pos["entry"] - trigger:
            pos["stop"] = min(pos["stop"], price + trail)

    # stop check
    if (pos["side"] == "BUY" and price <= pos["stop"]) or (pos["side"] == "SELL" and price >= pos["stop"]):
        if pos["side"] == "BUY":
            pnl = pos["qty"] * (pos["stop"] - pos["entry"])
        else:
            pnl = pos["qty"] * (pos["entry"] - pos["stop"])
        STATE["equity_usdt"] += pnl
        log_print(f"{symbol} STOP hit: PnL {pnl:.2f} USDT (DEMO).")
        STATE["positions"].pop(symbol, None)
        append_csv(STATE["trades_csv"], {
            "ts": dt.datetime.utcnow().isoformat(),
            "symbol": symbol, "side": "FLAT", "price": price, "pnl": pnl,
            "equity_usdt": STATE["equity_usdt"], "mode": STATE["mode"]
        })

def bot_loop():
    global CFG
    log_print("Starting Neriya Bot v1.0 Cloud Edition ...")
    while True:
        try:
            CFG = load_config()

            today = dt.datetime.utcnow().strftime("%Y-%m-%d")
            if today != STATE["last_day"]:
                STATE["last_day"] = today
                STATE["equity_start_of_day"] = STATE["equity_usdt"]

            # LIVE equity read
            if CFG["mode"] == "LIVE":
                try:
                    live_bal = BIN.get_balance("USDT")
                    STATE["equity_usdt"] = live_bal
                except Exception as e:
                    log_print(f"Could not fetch LIVE balance: {e}")

            if hit_daily_loss_limit(STATE["equity_start_of_day"], STATE["equity_usdt"], CFG["risk"]["max_daily_loss_pct"]):
                log_print("Daily loss limit reached. Pausing entries.")
                time.sleep(CFG["poll_interval_seconds"]); continue

            for symbol in CFG["symbols"]:
                df_sig = get_df(symbol, "5m", 500)
                df_trd = get_df(symbol, "1h", 500)
                if len(df_sig) < 210 or len(df_trd) < 210: continue

                price = float(df_sig["close"].iloc[-1])
                atr_now = AverageTrueRange(df_sig["high"], df_sig["low"], df_sig["close"], window=CFG["strategy"]["common"]["atr_len"]).average_true_range().iloc[-1]
                manage_position(symbol, price, CFG, atr_now)

                if symbol in STATE["positions"]:
                    continue

                sig = pick_strategy(df_sig, df_trd, CFG)
                if sig["side"] is None: continue

                entry = sig["entry"]; stop = sig["stop"]
                rpu = abs(entry - stop)
                if rpu <= 0: continue

                balance = STATE["equity_usdt"] if CFG["mode"] == "DEMO" else max(STATE["equity_usdt"], 0.0)
                qty = position_size_from_risk(balance, CFG["risk"]["risk_per_trade_pct"], entry, stop)
                notional = qty * entry
                if notional < 10: continue

                if CFG["mode"] == "DEMO":
                    STATE["positions"][symbol] = {
                        "side": sig["side"],
                        "entry": entry,
                        "stop": stop,
                        "qty": qty,
                        "risk_per_unit": rpu,
                        "filled_tiers": [False for _ in CFG["strategy"]["take_profit"]["tiers"]]
                    }
                    append_csv(STATE["trades_csv"], {
                        "ts": dt.datetime.utcnow().isoformat(),
                        "symbol": symbol, "side": sig["side"],
                        "entry": entry, "stop": stop, "qty": qty, "mode": "DEMO"
                    })
                    log_print(f"{symbol} {sig['side']} (DEMO) @ {entry:.2f} | stop {stop:.2f} | qty {qty:.6f} | notional ~{notional:.2f}")
                else:
                    try:
                        side = "BUY" if sig["side"] == "BUY" else "SELL"
                        if side == "SELL":
                            log_print(f"{symbol}: SELL ignored on LIVE spot (use futures for shorts).")
                            continue
                        order = BIN.market_order(symbol, "BUY", round(qty, 6))
                        append_csv(STATE["trades_csv"], {
                            "ts": dt.datetime.utcnow().isoformat(),
                            "symbol": symbol, "side": "BUY",
                            "entry": entry, "stop": stop, "qty": qty, "mode": "LIVE",
                            "orderId": order.get("orderId", "")
                        })
                        log_print(f"{symbol} BUY (LIVE) market sent. qty={qty:.6f}")
                        STATE["positions"][symbol] = {
                            "side": "BUY",
                            "entry": entry,
                            "stop": stop,
                            "qty": qty,
                            "risk_per_unit": rpu,
                            "filled_tiers": [False for _ in CFG["strategy"]["take_profit"]["tiers"]]
                        }
                    except Exception as e:
                        log_print(f"Order error (LIVE): {e}")

            time.sleep(CFG["poll_interval_seconds"])
        except Exception as e:
            log_print(f"Loop error: {e}")
            traceback.print_exc()
            time.sleep(5)

@APP.get("/")
def health():
    return jsonify({
        "name": "Neriya Bot v1.0 Cloud Edition",
        "mode": STATE["mode"],
        "equity_usdt": STATE["equity_usdt"],
        "positions": list(STATE["positions"].keys())
    })

def run_background():
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()

if __name__ == "__main__":
    run_background()
    APP.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
    from utils.exchange import BinanceExchange

if __name__ == "__main__":
    print("🚀 Starting NeriyaBot connection test...")

    try:
        exchange = BinanceExchange()
        balance = exchange.get_balance("USDT")
        print(f"✅ Connected to Binance Testnet successfully! USDT balance: {balance}")
    except Exception as e:
        print("❌ Connection failed!")
        print(e)
        @app.route('/')
def home():
    return "NeriyaBot is running on Render ✅"

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=10000)
