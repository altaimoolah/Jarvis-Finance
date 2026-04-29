import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
import threading

TOKEN = os.getenv("TELEGRAM_TOKEN")
app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

async def send_chart(update: Update, context):
    ticker = context.args[0].upper() if context.args else "SPY"
    # ... your chart generation code here (same as before)
    await update.message.reply_photo(...)

application.add_handler(CommandHandler("chart", send_chart))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    threading.Thread(target=lambda: application.process_update(update)).start()
    return 'OK', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
