import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment Variables မှ Tokens များကို ဖတ်ယူခြင်း
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API ကို Configure လုပ်ခြင်း (gemini-2.5-flash သို့မဟုတ် gemini-1.5-flash ကို သုံးနိုင်ပါတယ်)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # ဂျပန်စာ ဘာသာပြန်ဆိုရန် Prompt သတ်မှတ်ခြင်း
    prompt = f"Translate the following text into Japanese accurately, and provide its Myanmar meaning as well: {user_text}"
    
    try:
        # Gemini Model ဆီသို့ Request ပို့ခြင်း
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

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # စာသားမှန်သမျှကို လက်ခံပြီး handle_message သို့ ပို့ပေးရန်
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running with Gemini API...")
    application.run_polling()

if __name__ == '__main__':
    main()
