from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

session = HTTP(
    testnet=True,  # אם אתה רוצה לעבוד עם חשבון אמיתי שנה את זה ל-False
    api_key=api_key,
    api_secret=api_secret
)

try:
    balance = session.get_wallet_balance(accountType="UNIFIED")
    print("✅ Connected to Bybit successfully!")
    print(balance)
except Exception as e:
    print("❌ Error connecting to Bybit:", e)
