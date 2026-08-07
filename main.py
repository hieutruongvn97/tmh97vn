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
    message = update.message
    if not message or not message.text:
        return

    chat_type = message.chat.type
    bot_user = context.bot
    bot_username = f"@{bot_user.username}"

    # QUY TẮC PHẢN HỒI
    should_reply = False
    
    if chat_type == 'private':
        should_reply = True  # Nhắn riêng thì luôn trả lời
    else:
        # Trong Group: Chỉ trả lời nếu có tag tên bot hoặc reply tin nhắn của bot
        if bot_username in message.text:
            should_reply = True
        elif message.reply_to_message and message.reply_to_message.from_user.id == bot_user.id:
            should_reply = True

    # Nếu không thỏa mãn điều kiện thì "làm thinh"
    if not should_reply:
        return

    # Loại bỏ @tag khỏi tin nhắn để AI đọc hiểu chuẩn xác hơn
    user_text = message.text.replace(bot_username, "").strip()
    if not user_text:
        user_text = "Xin chào"

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemini-3.5-flash-lite",
            "messages": [{"role": "user", "content": user_text}],
            "max_tokens": 500
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
