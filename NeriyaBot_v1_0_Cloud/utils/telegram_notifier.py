import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ הבוט פעיל ומחובר ל-Bybit בהצלחה!\nמוכן לפעולה 💎")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 כרגע אין עסקאות פתוחות. הבוט עוקב אחרי השוק...")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📘 פקודות זמינות:\n/start - הפעלת הבוט\n/status - מצב נוכחי\n/help - רשימת פקודות")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Exception while handling update:", exc_info=context.error)
    if TELEGRAM_CHAT_ID:
        await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="❌ שגיאת מערכת. בדוק את הלוגים ב-Render.")

def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help))
    app.add_error_handler(error_handler)
    app.run_polling()v
