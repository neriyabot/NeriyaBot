from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

# קריאת מפתחות API מהסביבה
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

# התחברות ל-Bybit Testnet (אפשר לשנות ל-live בהמשך)
session = HTTP(
    testnet=True,
    api_key=api_key,
    api_secret=api_secret
)

print("🔄 Connecting to Bybit...")

try:
    balance = session.get_wallet_balance(accountType="UNIFIED")
    print("✅ Connected successfully!")
    print(balance)
except Exception as e:
    print("❌ Connection failed:", e)
