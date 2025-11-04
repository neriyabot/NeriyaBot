import os
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "trade_history.csv"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_daily_report():
    """שולח דוח יומי לטלגרם על בסיס trade_history.csv"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_TOKEN או TELEGRAM_CHAT_ID לא מוגדרים – לא ניתן לשלוח דוח.")
        return

    if not os.path.exists(LOG_FILE):
        text = "📊 דוח יומי:\nאין עדיין עסקאות רשומות היום."
        _send_telegram_message(text)
        return

    df = pd.read_csv(LOG_FILE)

    # נוודא שיש את העמודות שצריך
    required_cols = ["תאריך", "מטבע", "פעולה", "סכום (USDT)", "מחיר", "סטטוס"]
    for col in required_cols:
        if col not in df.columns:
            text = "📊 דוח יומי:\nקובץ היסטוריית העסקאות לא בפורמט תקין."
            _send_telegram_message(text)
            return

    # סינון ליום הנוכחי לפי תאריך
    today_str = datetime.now().strftime("%Y-%m-%d")
    df["תאריך_יום"] = df["תאריך"].astype(str).str.slice(0, 10)
    df_today = df[df["תאריך_יום"] == today_str]

    if df_today.empty:
        text = f"📊 דוח יומי {today_str}:\nאין עסקאות שבוצעו היום."
        _send_telegram_message(text)
        return

    total_trades = len(df_today)
    wins = df_today[df_today["סטטוס"].isin(["Success", "Completed", "בוצע"])]
    losses = df_today[df_today["סטטוס"].str.contains("Stopped", na=False)]

    win_count = len(wins)
    loss_count = len(losses)

    # נסכם רק את סכום ה-USDT שהשתתף בעסקאות (לא רווח נטו, אלא נפח)
    total_volume = df_today["סכום (USDT)"].sum()

    text_lines = [
        f"📊 דוח יומי – {today_str}",
        "",
        f"🔹 כמות עסקאות היום: {total_trades}",
        f"🟢 עסקאות מוצלחות (TP/בוצע): {win_count}",
        f"🔴 עסקאות שנסגרו בהפסד (SL/Stopped): {loss_count}",
        f"💵 סך נפח עסקאות (USDT): {total_volume:.2f}",
        "",
        "מטבעות פעילים היום:",
    ]

    pairs = df_today["מטבע"].value_counts().head(10)
    for pair, count in pairs.items():
        text_lines.append(f" • {pair} – {count} עסקאות")

    text = "\n".join(text_lines)
    _send_telegram_message(text)


def _send_telegram_message(text: str):
    """שליחת הודעה פשוטה לטלגרם"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("✅ דוח יומי נשלח לטלגרם בהצלחה.")
        else:
            print("⚠️ שגיאה בשליחת הדוח לטלגרם:", resp.text)
    except Exception as e:
        print("❌ שגיאה בחיבור לטלגרם בזמן דוח יומי:", e)
