import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xin chào! Tôi là Gemini Bot. Hãy gửi tin nhắn cho tôi!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = ai_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=user_text,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        await update.message.reply_text("Có lỗi xảy ra khi kết nối với Gemini.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot dang chay...")
    app.run_polling()

if __name__ == '__main__':
    main()
