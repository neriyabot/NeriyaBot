import os
import time
from datetime import datetime

from utils.exchange import Exchange
from strategies.pro_trend_strategy import ProTrendStrategy
from telegram_notifier import send_telegram_message


# === הגדרות כלליות ===

MODE = os.getenv("BOT_MODE", "DEMO").upper()

# רשימת מטבעות לסחר מקביל
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
]

POLL_INTERVAL = 15  # כמה שניות בין בדיקות

# === פונקציה עזר לעיצוב שם המטבע ===
def format_symbol(symbol: str) -> str:
    if symbol.endswith("USDT"):
        base = symbol[:-4]
        return f"{base}/USDT"
    return symbol


def main():
    print(f"[{datetime.utcnow()}] 🚀 NeriyaBot התחיל לעבוד במצב: {MODE}")

    exchange = Exchange(MODE)
    strategy = ProTrendStrategy(
        symbols=SYMBOLS,
        risk_per_trade=0.05,   # 5% מהיתרה
        take_profit_pct=0.06,  # טייק פרופיט 6%
        stop_loss_pct=0.03,    # סטופ לוס 3%
    )

    while True:
        try:
            # 1️⃣ מביא יתרת USDT
            balance_usdt = exchange.client.get_wallet_balance(accountType="UNIFIED")["result"]["list"][0]["totalEquity"]
            balance_usdt = float(balance_usdt)
        except Exception as e:
            print("❌ שגיאה בקריאת יתרה:", e)
            time.sleep(POLL_INTERVAL)
            continue

        for symbol in SYMBOLS:
            try:
                # 2️⃣ מביא מחיר עדכני
                price = exchange.get_last_price(symbol)
                nice_symbol = format_symbol(symbol)

                # 3️⃣ מעדכן היסטוריה
                strategy.update_price(symbol, price)

                # 4️⃣ בדיקה אם יש פוזיציה פתוחה וצריך לסגור אותה
                exit_reason = strategy.check_exit(symbol, price)
                if exit_reason:
                    pos = strategy.open_positions.get(symbol)
                    side = pos["side"]
                    size_usdt = pos["size_usdt"]
                    close_side = "SELL" if side == "BUY" else "BUY"

                    try:
                        exchange.create_market_order(symbol, close_side, size_usdt)
                        strategy.close_position(symbol)
                        msg = (
                            f"✅ סגירת עסקה ({exit_reason})\n"
                            f"צמד: {nice_symbol}\n"
                            f"סגירה: {close_side}\n"
                            f"מחיר: {price}\n"
                        )
                        print(msg)
                        send_telegram_message(msg)
                    except Exception as e:
                        print(f"⚠️ שגיאה בסגירה עבור {symbol}: {e}")
                    continue

                # 5️⃣ מקבל סיגנל חדש
                signal = strategy.get_trend_signal(symbol)

                if signal == "HOLD":
                    print(f"{datetime.utcnow()} - {nice_symbol}: HOLD (price={price})")
                    continue

                # 6️⃣ אם יש כבר פוזיציה באותו כיוון - מדלג
                if not strategy.should_open_position(symbol, signal):
                    continue

                # 7️⃣ חישוב גודל עסקה
                trade_size_usdt = strategy.get_position_size_usdt(balance_usdt)

                # 8️⃣ פתיחת פוזיציה חדשה
                exchange.create_market_order(symbol, signal, trade_size_usdt)
                strategy.register_open_position(symbol, signal, price, trade_size_usdt)

                msg = (
                    f"🟢 פתיחת עסקה חדשה!\n"
                    f"צמד: {nice_symbol}\n"
                    f"סוג: {signal}\n"
                    f"מחיר: {price}\n"
                    f"גודל עסקה: {trade_size_usdt:.2f} USDT\n"
                )
                print(msg)
                send_telegram_message(msg)

            except Exception as e:
                print(f"❌ שגיאה בעיבוד {symbol}: {e}")

        # 9️⃣ הפסקה בין סבבים
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
