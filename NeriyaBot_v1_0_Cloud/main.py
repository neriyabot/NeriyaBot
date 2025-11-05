import asyncio
from exchange import Exchange
from strategies.smart_trend_strategy import SmartTrendStrategy
from utils.telegram_notifier import send_trade_alert

async def main():
    print("🚀 Starting NeriyaBot Ultra+ (Bybit Testnet)...")

    # חיבור ל-Bybit במצב דמו
    exchange = Exchange(mode="DEMO")

    # יצירת אובייקט של האסטרטגיה (לא מעבירים כאן את הסימבול!)
    strategy = SmartTrendStrategy(exchange)

    while True:
        try:
            # כאן אנחנו מעבירים את הסימבול בפועל
            signal = await strategy.generate_signal("BTC/USDT")

            if signal == "BUY":
                await exchange.buy("BTC/USDT", 0.001)
                await send_trade_alert("📈 קנייה בוצעה! (BTC/USDT)")

            elif signal == "SELL":
                await exchange.sell("BTC/USDT", 0.001)
                await send_trade_alert("📉 מכירה בוצעה! (BTC/USDT)")

            else:
                print("⏳ אין אות ברור כרגע...")

            # מחכה 30 שניות לפני הבדיקה הבאה
            await asyncio.sleep(30)

        except Exception as e:
            print(f"❌ שגיאה: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
