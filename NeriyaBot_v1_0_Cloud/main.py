import time
from utils.exchange import Exchange
from utils.telegram_notifier import TelegramNotifier
from strategies.advanced_strategy import AdvancedStrategy

# ==============================
# NeriyaBot PRO – גרסה מלאה
# ==============================

print("🚀 NeriyaBot PRO התחיל לעבוד בהצלחה...")

# מצב עבודה: DEMO או REAL
MODE = "DEMO"

# אתחול המודולים
exchange = Exchange(MODE)
notifier = TelegramNotifier()

# רשימת המטבעות שהבוט יעקוב אחריהם
COINS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT"
]

TRADE_PERCENT = 5  # אחוז מהיתרה לשימוש בכל עסקה

# =========================================================
# פונקציית המסחר הראשית - ניתוח גרפים והחלטות קנייה/מכירה
# =========================================================
def trade_logic():
    try:
        balance_data = exchange.get_balance()
        if not balance_data:
            notifier.send_message("⚠️ לא ניתן לבדוק יתרה כרגע.")
            return

        notifier.send_message("🤖 הבוט התחיל סבב ניתוח שוק חכם...")

        for coin in COINS:
            strategy = AdvancedStrategy(coin)
            action = strategy.generate_signal()

            if action == "BUY":
                notifier.send_message(f"🟢 זוהתה הזדמנות קנייה ב־{coin}")
                exchange.create_market_order(symbol=coin, side="Buy", quote_amount_usdt=TRADE_PERCENT)

            elif action == "SELL":
                notifier.send_message(f"🔴 זוהתה הזדמנות מכירה ב־{coin}")
                exchange.create_market_order(symbol=coin, side="Sell", quote_amount_usdt=TRADE_PERCENT)

            else:
                notifier.send_message(f"{coin} – אין שינוי מגמה כרגע.")

        notifier.send_message("✅ סבב מסחר הסתיים בהצלחה.\n⏳ הבוט יבדוק שוב בעוד דקה.")

    except Exception as e:
        print(f"שגיאה כללית: {e}")
        notifier.send_message(f"❌ שגיאת מערכת: {e}")

# =========================================================
# לולאת עבודה אינסופית – הבוט פועל ברקע
# =========================================================
while True:
    trade_logic()
    time.sleep(60)  # כל דקה בודק מחדש את כל המטבעות
