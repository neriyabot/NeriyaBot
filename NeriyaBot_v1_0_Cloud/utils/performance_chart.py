import pandas as pd
import matplotlib.pyplot as plt
import os

LOG_FILE = "trade_history.csv"

def plot_performance():
    """מציג גרף רווחים לפי היסטוריית המסחר"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ לא נמצא קובץ trade_history.csv – אין נתונים להצגה.")
        return

    df = pd.read_csv(LOG_FILE)

    if "מחיר" not in df.columns or "פעולה" not in df.columns:
        print("⚠️ הקובץ לא מכיל נתונים תקינים לציור גרף.")
        return

    # המרת טקסטים למספרים
    df["מחיר"] = pd.to_numeric(df["מחיר"], errors="coerce")

    # סימון עסקאות BUY ו-SELL
    df["כיוון"] = df["פעולה"].apply(lambda x: 1 if "BUY" in x else -1 if "SELL" in x else 0)
    df["שינוי"] = df["מחיר"].diff() * df["כיוון"]

    # חישוב רווח מצטבר
    df["רווח מצטבר"] = df["שינוי"].cumsum().fillna(0)

    # ציור גרף
    plt.figure(figsize=(10, 5))
    plt.plot(df["תאריך"], df["רווח מצטבר"], marker="o", linewidth=2)
    plt.title("📈 ביצועי NeriyaBot לאורך זמן", fontsize=16)
    plt.xlabel("תאריך")
    plt.ylabel("רווח מצטבר (USDT)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
