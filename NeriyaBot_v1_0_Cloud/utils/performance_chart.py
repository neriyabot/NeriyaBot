import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "trade_history.csv"

def plot_and_send_performance():
    """יוצר גרף רווחים, שומר כ-PNG, ושולח לטלגרם"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ לא נמצא קובץ trade_history.csv – אין נתונים להצגה.")
        return

    df = pd.read_csv(LOG_FILE)

    if "מחיר" not in df.columns or "פעולה" not in df.columns:
        print("⚠️ הקובץ לא מכיל נתונים תקינים לציור גרף.")
        return

    df["מחיר"] = pd.to_numeric(df["מחיר"], errors="coerce")
    df = df.dropna(subset=["מחיר"])

    df["כיוון"] = df["פעולה"].apply(lambda x: 1 if "BUY" in x else -1 if "SELL" in x else 0)
    df["שינוי"] = df["מחיר"].diff() * df["כיוון"]
    df["רווח מצטבר"] = df["שינוי"].cumsum().fillna(0)

    plt.figure(figsize=(10, 5))
    plt.plot(df["תאריך"], df["רווח מצטבר"], marker="o", color="gold", linewidth=2)
    plt.title("💰 ביצועי NeriyaBot לאורך זמן", fontsize=16, color="black")
    plt.xlabel("תאריך")
    plt.ylabel("רווח מצטבר (USDT)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    chart_path = f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(chart_path)
    plt.close()
    print(f"📊 גרף נשמר: {chart_path}")

    send_chart_to_telegram(chart_path)

def send_chart_to_telegram(file_path):
    """שולח את הגרף לטלגרם"""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️ לא נמצאו פרטי טלגרם בקובץ .env")
        return

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(file_path, "rb") as photo:
        files = {"photo": photo}
        data = {"chat_id": chat_id, "caption": "📈 גרף ביצועי NeriyaBot מעודכן!"}
        response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        print("✅ הגרף נשלח בהצלחה לטלגרם.")
    else:
        print(f"❌ שגיאה בשליחת הגרף: {response.text}")
