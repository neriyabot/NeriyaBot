import os
import ccxt
import time
import logging
import requests
from datetime import datetime

# ==========================
# הגדרות ראשוניות
# ==========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# סביבת עבודה (דמו או אמיתי)
MODE = os.getenv("BOT_MODE", "DEMO")

# קבלת מפתחות
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # אפשר להוסיף אחר כך מזהה צ׳אט

# הגדרה של הבורסה
exchange = ccxt.bybit({
    'apiKey': BYBIT_API_KEY,
    'secret': BYBIT_API_SECRET,
})
exchange.set_sandbox_mode(MODE == "DEMO")

# ==========================
# פונקציות עזר
# ==========================

def send_telegram_message(message):
    """שליחת הודעה לטלגרם"""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            requests.post(url, data=data)
        except Exception as e:
            logging.error(f"שגיאה בשליחת הודעת טלגרם: {e}")

def get_balance():
    """בדיקת יתרה"""
    balance = exchange.fetch_balance()
    usdt = balance['total'].get('USDT', 0)
    return usdt

def get_signal(symbol):
    """אסטרטגיית כניסה חכמה לפי מגמת גרף"""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=100)
    closes = [c[4] for c in ohlcv]

    ma_short = sum(closes[-5:]) / 5
    ma_long = sum(closes[-20:]) / 20

    if ma_short > ma_long:
        return "BUY"
    elif ma_short < ma_long:
        return "SELL"
    else:
        return "HOLD"

def trade(symbol, signal, amount_percent=5):
    """ביצוע עסקה לפי האות"""
    balance = get_balance()
    amount = (balance * amount_percent) / 100 / exchange.fetch_ticker(symbol)['last']

    try:
        if signal == "BUY":
            order = exchange.create_market_buy_order(symbol, amount)
            send_telegram_message(f"💎 קנייה בוצעה: {symbol} ({amount_percent}% מהיתרה)")
        elif signal == "SELL":
            order = exchange.create_market_sell_order(symbol, amount)
            send_telegram_message(f"🔥 מכירה בוצעה: {symbol} ({amount_percent}% מהיתרה)")
        else:
            logging.info(f"{symbol} - אין פעולה כרגע")
    except Exception as e:
        logging.error(f"שגיאה בפעולה על {symbol}: {e}")

# ==========================
# לולאת הבוט הראשית
# ==========================

symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

send_telegram_message("🚀 Neriya Bot הופעל בהצלחה!")

while True:
    try:
        for symbol in symbols:
            signal = get_signal(symbol)
            logging.info(f"{symbol} - אות: {signal}")
            trade(symbol, signal)
            time.sleep(2)

        time.sleep(60)
    except Exception as e:
        logging.error(f"שגיאה בלולאה הראשית: {e}")
        time.sleep(30)
