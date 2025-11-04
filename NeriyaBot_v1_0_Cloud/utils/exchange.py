import os
import logging
import asyncio
import random
from dotenv import load_dotenv
from pybit.unified_trading import HTTP
from utils.telegram_notifier import send_trade_alert

load_dotenv()

class Exchange:
    def __init__(self, mode):
        self.mode = mode
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API keys not found. Make sure BYBIT_API_KEY and BYBIT_API_SECRET are set.")

        # חיבור ל-Bybit
        self.client = HTTP(
            testnet=True if mode == "DEMO" else False,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

        logging.info("✅ Bybit initialized successfully!")

    async def analyze_market(self, symbol):
        """
        ניתוח שוק פשוט – מדמה ניתוח של מגמה
        בהמשך אפשר לשלב כאן אלגוריתם אמיתי או בינה מלאכותית
        """
        trend = random.choice(["UP", "DOWN", "SIDEWAYS"])
        return trend

    async def trade_decision(self, symbol, balance):
        """
        מחליט אם לקנות, למכור או להחזיק על פי ניתוח מגמה
        """
        trend = await self.analyze_market(symbol)

        if trend == "UP":
            decision = "BUY"
        elif trend == "DOWN":
            decision = "SELL"
        else:
            decision = "HOLD"

        amount = balance * 0.05  # 5% מסך החשבון
        await self.execute_trade(symbol, decision, amount)

    async def execute_trade(self, symbol, decision, amount):
        """
        מבצע את הפעולה בשוק (מדמה פעולה אמיתית)
        """
        if decision == "BUY":
            logging.info(f"📈 ביצוע קנייה של {amount}$ ב-{symbol}")
            await send_trade_alert(f"📈 בוצעה קנייה של {symbol} בסכום {amount}$ 💎")

        elif decision == "SELL":
            logging.info(f"📉 ביצוע מכירה של {amount}$ ב-{symbol}")
            await send_trade_alert(f"📉 בוצעה מכירה של {symbol} בסכום {amount}$ ⚡")

        else:
            logging.info(f"⏸ החזקת פוזיציה ב-{symbol}")
            await send_trade_alert(f"⏸ אין פעולה חדשה ב-{symbol}. הבוט במעקב...")

    async def run(self):
        """
        לולאת מסחר שרצה על כמה מטבעות במקביל
        """
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
        balance = 10000  # סכום וירטואלי לתחזית (אפשר לשנות)

        while True:
            for symbol in symbols:
                await self.trade_decision(symbol, balance)
                await asyncio.sleep(5)  # זמן קצר בין עסקאות
