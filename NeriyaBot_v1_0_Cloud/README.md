# Neriya Bot v1.0 — Cloud Edition (Render, Mac M2)

בוט מסחר חכם ל-Binance, רץ בענן 24/7. כולל מצב DEMO ו-LIVE.

## איך מעלים ל-Render (שלב-שלב)
1) היכנס ל-https://render.com והירשם/התחבר.
2) לחץ New → Web Service.
3) בחר Upload והעלה את קובץ ה-ZIP של התיקייה הזו.
4) Name: `neriya-bot` | Runtime: Python | Start Command: `python main.py`
5) פריסה תתחיל ותראה לוגים (Logs).

## מצב דמו / אמיתי
- `config.yaml`:
  ```yaml
  mode: "DEMO"   # שנה ל "LIVE" למסחר אמיתי
  ```
- לקובץ `.env` (שכפול מ-`.env.example`) הכנס:
  ```
  BINANCE_API_KEY=...
  BINANCE_API_SECRET=...
  ```

## הערות
- ב-LIVE הדוגמה שולחת קנית MARKET ב-Spot בלבד (לשורט/יציאות אוטומטיות דרוש פיתוח Futures/OOCO).
- `trades.csv` ירכז עסקאות/מצב (בענן נשמר בדיסק השירות).
- זה אינו ייעוץ פיננסי. השתמש באחריותך בלבד.