import time
from utils.exchange import Exchange
from utils.telegram_notifier import TelegramNotifier
from utils.log_trades import TradeLogger
from utils.performance_chart import plot_and_send_performance
from utils.ai_learning import AILearning
from strategies.advanced_strategy import AdvancedStrategy

print("🚀 NeriyaBot Ultra+ AI התחיל לפעול בהצלחה...")

MODE = "DEMO"  # מצב דמו (אפשר לשנות ל-REAL בהמשך)

exchange = Exchange(MODE)
notifier = TelegramNotifier()
logger = TradeLogger()

COINS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]

TRADE_PERCENT = 5
TAKE_PROFIT_PERCENT = 3
STOP_LOSS_PERCENT = 1.5

open_trades = {}

def trade_logic():
    try:
        ai = AILearning()
        current_strategy = ai.analyze_history()

        balance_data = exchange.get_balance()
        if not balance_data:
            notifier.send_message("⚠️ לא ניתן לבדוק יתרה כרגע.")
            return

        notifier.send_message("🤖 NeriyaBot AI התחיל סבב מסחר חכם...")

        for coin in COINS:
            strategy = AdvancedStrategy(coin)
            action = strategy.generate_signal(weights=current_strategy)
            ticker = exchange.exchange.fetch_ticker(coin)
            current_price = ticker['last']

            if coin in open_trades:
                entry_price = open_trades[coin]["entry_price"]
                side = open_trades[coin]["side"]

                change_percent = ((current_price - entry_price) / entry_price) * 100 if side == "Buy" else ((entry_price - current_price) / entry_price) * 100

                if change_percent >= TAKE_PROFIT_PERCENT:
                    notifier.send_message(f"💰 {coin}: רווח {change_percent:.2f}% – סגירת עסקה.")
                    exchange.create_market_order(symbol=coin, side="Sell" if side == "Buy" else "Buy", quote_amount_usdt=TRADE_PERCENT)
                    logger.log_trade(coin, "TAKE_PROFIT", TRADE_PERCENT, current_price, "Success")
                    del open_trades[coin]
                    continue

                if change_percent <= -STOP_LOSS_PERCENT:
                    notifier.send_message(f"❗ {coin}: הפסד {change_percent:.2f}% – סגירת עסקה.")
                    exchange.create_market_order(symbol=coin, side="Sell" if side == "Buy" else "Buy", quote_amount_usdt=TRADE_PERCENT)
                    logger.log_trade(coin, "STOP_LOSS", TRADE_PERCENT, current_price, "Stopped")
                    del open_trades[coin]
                    continue

            if action == "BUY" and coin not in open_trades:
                notifier.send_message(f"🟢 קניית BUY ב־{coin}")
                exchange.create_market_order(symbol=coin, side="Buy", quote_amount_usdt=TRADE_PERCENT)
                open_trades[coin] = {"side": "Buy", "entry_price": current_price}
                logger.log_trade(coin, "BUY", TRADE_PERCENT, current_price, "Opened")

            elif action == "SELL" and coin not in open_trades:
                notifier.send_message(f"🔴 מכירת SELL ב־{coin}")
                exchange.create_market_order(symbol=coin, side="Sell", quote_amount_usdt=TRADE_PERCENT)
                open_trades[coin] = {"side": "Sell", "entry_price": current_price}
                logger.log_trade(coin, "SELL", TRADE_PERCENT, current_price, "Opened")

            else:
                notifier.send_message(f"{coin}: אין שינוי כרגע.")

        # אחרי כל סבב – יצירת גרף ושליחה לטלגרם
        plot_and_send_performance()
        notifier.send_message("✅ סבב מסחר הסתיים.\n⏳ בוט ילמד ויחזור בעוד דקה.")

    except Exception as e:
        notifier.send_message(f"❌ שגיאת מערכת: {e}")

while True:
    trade_logic()
    time.sleep(60)
