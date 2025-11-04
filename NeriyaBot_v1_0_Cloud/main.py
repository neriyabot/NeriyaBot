import time
from utils.exchange import Exchange
from utils.telegram_notifier import TelegramNotifier
from utils.log_trades import TradeLogger
from utils.performance_chart import plot_and_send_performance
from strategies.advanced_strategy import AdvancedStrategy

# ===============================================
# NeriyaBot Ultra+ – עם Take Profit, Stop Loss וגרף אוטומטי לטלגרם
# ===============================================

print("🚀 NeriyaBot Ultra+ התחיל לפעול בהצלחה...")

# מצב עבודה: DEMO או REAL
MODE = "DEMO"

# אתחול המודולים
exchange = Exchange(MODE)
notifier = TelegramNotifier()
logger = TradeLogger()

# רשימת המטבעות שהבוט מנתח
COINS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT"
]

TRADE_PERCENT = 5          # אחוז מהיתרה לכל עסקה
TAKE_PROFIT_PERCENT = 3    # רווח יעד (Take Profit)
STOP_LOSS_PERCENT = 1.5    # הפסד מקסימלי (Stop Loss)

open_trades = {}  # מעקב אחרי עסקאות פתוחות

# =====================================================
# פונקציית המסחר הראשית
# =====================================================
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
            ticker = exchange.exchange.fetch_ticker(coin)
            current_price = ticker['last']

            # ============================
            # ניהול עסקאות פתוחות
            # ============================
            if coin in open_trades:
                entry_price = open_trades[coin]["entry_price"]
                side = open_trades[coin]["side"]

                change_percent = ((current_price - entry_price) / entry_price) * 100 if side == "Buy" else ((entry_price - current_price) / entry_price) * 100

                # Take Profit
                if change_percent >= TAKE_PROFIT_PERCENT:
                    notifier.send_message(f"💰 {coin}: רווח של {change_percent:.2f}% – סגירת עסקה ברווח.")
                    exchange.create_market_order(symbol=coin, side="Sell" if side == "Buy" else "Buy", quote_amount_usdt=TRADE_PERCENT)
                    logger.log_trade(coin, "TAKE_PROFIT", TRADE_PERCENT, current_price, "Success")
                    del open_trades[coin]
                    continue

                # Stop Loss
                if change_percent <= -STOP_LOSS_PERCENT:
                    notifier.send_message(f"❗ {coin}: הפסד של {change_percent:.2f}% – סגירת עסקה בהפסד.")
                    exchange.create_market_order(symbol=coin, side="Sell" if side == "Buy" else "Buy", quote_amount_usdt=TRADE_PERCENT)
                    logger.log_trade(coin, "STOP_LOSS", TRADE_PERCENT, current_price, "Stopped")
                    del open_trades[coin]
                    continue

            # ============================
            # פתיחת עסקאות חדשות
            # ============================
            if action == "BUY" and coin not in open_trades:
                notifier.send_message(f"🟢 פתיחת עסקת BUY ב־{coin}")
                exchange.create_market_order(symbol=coin, side="Buy", quote_amount_usdt=TRADE_PERCENT)
                open_trades[coin] = {"side": "Buy", "entry_price": current_price}
                logger.log_trade(coin, "BUY", TRADE_PERCENT, current_price, "Opened")

            elif action == "SELL" and coin not in open_trades:
                notifier.send_message(f"🔴 פתיחת עסקת SELL ב־{coin}")
                exchange.create_market_order(symbol=coin, side="Sell", quote_amount_usdt=TRADE_PERCENT)
                open_trades[coin] = {"side": "Sell", "entry_price": current_price}
                logger.log_trade(coin, "SELL", TRADE_PERCENT, current_price, "Opened")

            else:
                notifier.send_message(f"{coin}: אין שינוי מגמה כרגע.")

        # ============================
        # שליחת גרף ביצועים לטלגרם
        # ============================
        plot_and_send_performance()

        notifier.send_message("✅ סבב מסחר הסתיים בהצלחה.\n⏳ הבוט יבדוק שוב בעוד דקה.")

    except Exception as e:
        print(f"שגיאה כללית: {e}")
        notifier.send_message(f"❌ שגיאת מערכת: {e}")

# =====================================================
# לולאת עבודה מתמשכת
# =====================================================
while True:
    trade_logic()
    time.sleep(60)
