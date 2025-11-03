def get_balance(self):
    try:
        # בקשה לנתוני היתרה של החשבון המאוחד (Unified)
        balance = self.client.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        
        # חילוץ הנתון של היתרה הכוללת ב־USDT
        total_balance = balance['result']['list'][0]['coin'][0]['walletBalance']
        
        print(f"💰 Balance detected: {total_balance} USDT")
        return float(total_balance)

    except Exception as e:
        print("❌ Failed to fetch balance:", e)
        return 0.0
