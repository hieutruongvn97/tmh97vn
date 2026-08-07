import os
import logging
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("GEMINI_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xin chào! Tôi là Gemini Bot. Hãy gửi tin nhắn cho tôi!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [{"role": "user", "content": user_text}]
        }
        
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers, timeout=30)
        res_json = res.json()
        
        if "choices" in res_json:
            reply = res_json["choices"][0]["message"]["content"]
            await update.message.reply_text(reply)
        else:
            err_detail = res_json.get("error", {}).get("message", str(res_json))
            await update.message.reply_text(f"Lỗi OpenRouter: {err_detail[:200]}")
            
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        await update.message.reply_text("Có lỗi xảy ra khi xử lý phản hồi.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot dang chay...")
    app.run_polling()

if __name__ == '__main__':
    main()
