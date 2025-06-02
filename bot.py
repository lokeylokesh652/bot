import random
import string
import os
import threading
import time
import requests

from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask

# ─── Config ─────────────────────────────────────────────────────────────────
TOKEN = "8180863106:AAFQ4C0tM40F8r1HjV-0a6tITVaCmq7d-Ss"
DOMAIN = "king-viper-indo.shop"
EMAIL_COUNT = 5
FILE_PATH = "acc.txt"
RENDER_URL = "https://bot-3393.onrender.com"

# ─── Flask Keep-alive Server ────────────────────────────────────────────────
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Bot is alive!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# ─── Self Ping to Keep Alive ────────────────────────────────────────────────
def self_pinger():
    while True:
        try:
            requests.get(RENDER_URL)
        except:
            pass
        time.sleep(300)  # every 5 min

# ─── Email Generator ────────────────────────────────────────────────────────
def generate_dot_emails(base):
    return list(set([base[:i] + "." + base[i:] for i in range(1, len(base))] + [base]))

def generate_random_base():
    return ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 8)))

def generate_emails(count):
    seen = set()
    result = []
    while len(result) < count:
        base = generate_random_base()
        for local in generate_dot_emails(base):
            email = f"{local}@{DOMAIN}"
            if email not in seen:
                result.append(email)
                seen.add(email)
            if len(result) >= count:
                break
    return result

def save_emails(emails):
    with open(FILE_PATH, "a") as f:
        for e in emails:
            f.write(e + "\n")

# ─── Telegram Bot Commands ──────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to DotMail Bot*\n\n"
        f"I generate fake dot-variant emails using *{DOMAIN}*\n\n"
        "*Commands:*\n"
        "🔹 `/generate` – Generate emails\n"
        "🔹 `/clear` – Clear acc.txt\n"
        "🔹 `/download` – Download acc.txt",
        parse_mode="Markdown"
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emails = generate_emails(EMAIL_COUNT)
    save_emails(emails)
    await update.message.reply_text("✅ Emails:\n" + "\n".join(f"`{e}`" for e in emails), parse_mode="Markdown")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    open(FILE_PATH, "w").close()
    await update.message.reply_text("🧹 *acc.txt cleared.*", parse_mode="Markdown")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        await update.message.reply_document(InputFile(FILE_PATH))
    else:
        await update.message.reply_text("⚠️ *acc.txt is empty.*", parse_mode="Markdown")

# ─── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=self_pinger).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("download", download))
    app.run_polling()
