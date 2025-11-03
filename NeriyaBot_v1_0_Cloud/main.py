# main.py
import os
import time
import threading
import yaml
from datetime import datetime as dt

# צד של ה־API/ווב
from flask import Flask, jsonify

# תלויות עזר (נטען בעדינות כדי שלא יפיל את האפליקציה אם לא קיימות)
try:
    import pandas as pd  # לא חובה לרוץ, אבל שימושי אם תרצה בהמשך
except Exception:
    pd = None

# קובץ .env (ברנדר אפשר גם ENV VARS דרך ה־dashboard)
from dotenv import load_dotenv
load_dotenv()

# אינדיקטורים/טכני (לא חובה שהחבילה תהיה בשימוש בשלב זה)
try:
    from ta.volatility import AverageTrueRange  # noqa: F401
except Exception:
    pass

# כלים פנימיים (אם לא קיימים, לא נעצור את השרת)
try:
    from utils.logger import log_print, append_csv   # noqa: F401
except Exception:
    def log_print(*args, **kwargs):
        print(*args)

    def append_csv(*args, **kwargs):
        pass

try:
    from utils.risk import (
        position_size_from_risk,       # noqa: F401
        hit_daily_loss_limit           # noqa: F401
    )
except Exception:
    pass

#
from utils.exchange import BybitExchange as Exchange

# אסטרטגיות (אם לא קיימות כרגע, נמשיך לרוץ ללא עצירה)
try:
    import strategies.scalping as strat_scalp  # noqa: F401
    import strategies.trend as strat_trend     # noqa: F401
    import strategies.swing as strat_swing     # noqa: F401
except Exception:
    strat_scalp = strat_trend = strat_swing = None

APP = Flask(__name__)


# ---------- הגדרות/קונפיג ----------
def load_config(path: str = "config.yaml") -> dict:
    """
    טוען config.yaml מהשורש של הפרויקט.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        log_print("⚠️  config.yaml לא נמצא, נשתמש בברירות מחדל.")
        return {}
    except Exception as e:
        log_print("⚠️  שגיאה בקריאת config.yaml:", e)
        return {}


CFG = load_config()

POLL_SECONDS = int(CFG.get("poll_interval_seconds", 15))
MODE = str(CFG.get("mode", os.getenv("BOT_MODE", "DEMO"))).upper()

STATE = {
    "mode": MODE,
    "equity_usdt": float(CFG.get("initial_balance_usdt", 0.0)) if MODE == "DEMO" else 0.0,
    "equity_start_of_day": float(CFG.get("initial_balance_usdt", 0.0)) if MODE == "DEMO" else 0.0,
    "positions": {},
    "last_day": dt.utcnow().strftime("%Y-%m-%d"),
    "trades_csv": "trades.csv",
}


# ---------- לוגיקת רקע (אפשר להשאיר פשוט בשלב זה) ----------
def bot_loop():
    """
    לולאת רקע קלה — רק heartbeat כדי לשמור את השירות חי.
    אפשר להרחיב כאן אסטרטגיות בהמשך.
    """
    log_print(f"🫀 Bot loop started. Mode={STATE['mode']}, poll={POLL_SECONDS}s")
    while True:
        # כאן אפשר לשתול קריאות לאסטרטגיות בעתיד
        time.sleep(POLL_SECONDS)


def run_background():
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()


# ---------- ראוטים ----------
@APP.route("/")
def home():
    return "NeriyaBot is running on Render ✅"


@APP.route("/healthz")
def healthz():
    return "ok", 200


@APP.route("/status")
def status():
    return jsonify({
        "mode": STATE["mode"],
        "equity_usdt": STATE["equity_usdt"],
        "positions": list(STATE["positions"].keys()),
        "last_day": STATE["last_day"],
        "poll_seconds": POLL_SECONDS,
    })


# ---------- הרצה ----------
if __name__ == "__main__":
    print("🚀 Starting NeriyaBot connection test...")

    # בדיקת חיבור לבורסה (Testnet/LIVE לפי MODE או ENV)
    try:
        exchange = BinanceExchange()
        balance = exchange.get_balance("USDT")
        print(f"✅ Connected to Binance {'Testnet' if MODE == 'DEMO' else 'LIVE'} successfully! "
              f"USDT balance: {balance}")
    except Exception as e:
        print("❌ Connection failed!")
        print(e)

    # מרימים רקע + Flask
    run_background()
    APP.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")), debug=False)
