import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai
from flask import Flask
from threading import Thread

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment Variables မှ Tokens များကို ဖတ်ယူခြင်း
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API ကို Configure လုပ်ခြင်း
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Render Timeout မဖြစ်စေရန် Flask Web Server ငယ်တစ်ခု တည်ဆောက်ခြင်း
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is running with Gemini API!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # ဂျပန်စာ ဘာသာပြန်ဆိုရန် Prompt သတ်မှတ်ခြင်း
    prompt = f"Translate the following text into Japanese accurately, and provide its Myanmar meaning as well: {user_text}"
    
    try:
        response = model.generate_content(prompt)
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        reply_text = f"API Error: {e}"
        
    await update.message.reply_text(reply_text)

def main():
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        print("Error: TELEGRAM_BOT_TOKEN or GEMINI_API_KEY is missing!")
        return

    # Flask Server ကို Background Thread ဖြင့် စတင် Run ခြင်း (Render Timeout ကာကွယ်ရန်)
    t = Thread(target=run_web)
    t.start()

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running with Gemini API...")
    application.run_polling()

if __name__ == '__main__':
    main()
