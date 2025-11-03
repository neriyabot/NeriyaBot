def get_balance(self):
    try:
        print("🔄 Fetching Bybit account balance...")
        
        # בקשה לחשבון המאוחד ובדיקת יתרת USDT
        balance = self.client.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        
        # חילוץ היתרה הכוללת
        total_balance = balance['result']['list'][0]['coin'][0]['walletBalance']
        
        print(f"💰 Balance detected: {total_balance} USDT")
        return float(total_balance)
    
    except Exception as e:
        print(f"❌ Failed to fetch balance: {e}")
        return 0.0
