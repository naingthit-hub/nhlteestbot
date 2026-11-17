import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# Flask app ဖန်တັ້ງခြင်း (Render Free Plan တွင် Timeout ကာကွယ်ရန်)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live!"

# Environment Variables မှ Tokens များကို ယူခြင်း
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Google GenAI Client အသစ်ကို ချိတ်ဆက်ခြင်း
client = genai.Client(api_key=GEMINI_KEY)

# ဂျပန်စာ ဘာသာပြန်ဆိုပေးမည့် Function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        # Prompt တည်ဆောက်ခြင်း
        prompt = f"""
အောက်ပါ မြန်မာ သို့မဟုတ် အင်္ဂလိပ်စာသားကို ဂျပန်ဘာသာသို့ ဘာသာပြန်ဆိုပေးပါ။ 
ထို့နောက် မြန်မာလို အဓိပ္ပာယ် ရှင်းလင်းချက်နှင့် သဒ္ဒါဆိုင်ရာ ရှင်းလင်းချက်များကိုပါ အသေးစိတ် ဖော်ပြပေးပါ။

စာသား: {user_text}
"""
        # Google GenAI SDK အသစ်၏ Interactions API သို့မဟုတ် models.generate_content ကို အသုံးပြုခြင်း
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        
        reply_text = response.text
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        error_msg = f"API Error: {str(e)}"
        await update.message.reply_text(error_msg)

def main():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    # Telegram Bot Application တည်ဆောက်ခြင်း
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # စာသားများ လက်ခံရယူရန် MessageHandler ထည့်ခြင်း
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Bot ကို စတင် Run ခြင်း
    application.run_polling()

if __name__ == '__main__':
    import threading
    
    # Flask ကို Background တွင် အပြိုင် Run ပေးခြင်း (Render Web Service အတွက်)
    def run_flask():
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
        
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Bot ကို စတင်ခြင်း
    main()
