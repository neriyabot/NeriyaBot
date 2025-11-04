import os
import time
import ccxt
import requests
from datetime import datetime
import pandas as pd

# === Environment Variables ===
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
BOT_MODE = os.getenv("BOT_MODE", "TESTNET")  # TESTNET or LIVE
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Exchange Setup ===
if BOT_MODE.upper() == "TESTNET":
    exchange = ccxt.bybit({
        "apiKey": BYBIT_API_KEY,
        "secret": BYBIT_API_SECRET,
        "urls": {"api": {"public": "https://api-testnet.bybit.com",
                         "private": "https://api-testnet.bybit.com"}}
    })
else:
    exchange = ccxt.bybit({
        "apiKey": BYBIT_API_KEY,
        "secret": BYBIT_API_SECRET
    })

# === Settings ===
TRADE_PERCENT = 0.05   # 5% per trade
TIMEFRAME = "15m"      # 15 minutes candles
STOP_LOSS = 0.97       # -3%
TAKE_PROFIT = 1.06     # +6%
PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT"]

# === Telegram Notification ===
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

# === Trading Logic ===
def get_ema(df, n):
    return df["close"].ewm(span=n, adjust=False).mean()

def get_balance():
    balance = exchange.fetch_balance()
    return balance["USDT"]["free"]

def trade_signal(symbol):
    df = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=50)
    df = pd.DataFrame(df, columns=["time", "open", "high", "low", "close", "volume"])
    df["EMA9"] = get_ema(df, 9)
    df["EMA21"] = get_ema(df, 21)

    if df["EMA9"].iloc[-2] < df["EMA21"].iloc[-2] and df["EMA9"].iloc[-1] > df["EMA21"].iloc[-1]:
        return "BUY"
    elif df["EMA9"].iloc[-2] > df["EMA21"].iloc[-2] and df["EMA9"].iloc[-1] < df["EMA21"].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

def execute_trade(symbol, side):
    balance = get_balance()
    amount = (balance * TRADE_PERCENT) / exchange.fetch_ticker(symbol)["last"]

    order = exchange.create_market_order(symbol, side.lower(), amount)
    price = order["average"]
    msg = f"{'🟢 BUY' if side=='BUY' else '🔴 SELL'} {symbol} at {price:.2f}$"
    print(msg)
    send_telegram(msg)

    stop_price = price * STOP_LOSS if side == "BUY" else price * TAKE_PROFIT
    take_price = price * TAKE_PROFIT if side == "BUY" else price * STOP_LOSS

    exchange.create_order(symbol, "take_profit_market", side.lower(), amount, take_price)
    exchange.create_order(symbol, "stop_market", side.lower(), amount, stop_price)

# === Main Loop ===
print("🚀 NeriyaBot Pro AI is running...\n")
send_telegram("🤖 NeriyaBot Pro AI started trading!")

while True:
    for pair in PAIRS:
        try:
            signal = trade_signal(pair)
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pair, "→", signal)

            if signal in ["BUY", "SELL"]:
                execute_trade(pair, signal)

        except Exception as e:
            print(f"Error with {pair}: {e}")
    time.sleep(60)
