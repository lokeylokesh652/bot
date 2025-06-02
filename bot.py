import random
import string
import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import threading

TOKEN = "8180863106:AAEez-aHjZ6Q9ugAyjR3E2X9RKuP6GgofMg"
DOMAIN = "king-viper-indo.shop"
EMAIL_COUNT = 5
FILE_PATH = "acc.txt"

# ─── Flask Keep-alive Server ────────────────────────────────────────────────
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ─── Email Generator ────────────────────────────────────────────────────────
def generate_dot_emails(base):
    parts = []
    for i in range(1, len(base)):
        parts.append(base[:i] + "." + base[i:])
    parts.append(base)
    return list(set(parts))

def generate_random_base():
    return ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 8)))

def generate_emails(count):
    emails = []
    seen = set()
    while len(emails) < count:
        base = generate_random_base()
        for local in generate_dot_emails(base):
            email = f"{local}@{DOMAIN}"
            if email not in seen:
                emails.append(email)
                seen.add(email)
            if len(emails) >= count:
                break
    return emails

def save_emails(emails):
    with open(FILE_PATH, "a") as f:
        for email in emails:
            f.write(email + "\n")

# ─── Telegram Handlers ──────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *Welcome to DotMail Bot*\n\n"
        f"I generate fake dot-variant emails using *{DOMAIN}*\n\n"
        "*Commands:*\n"
        "🔹 `/generate` – Generate emails\n"
        "🔹 `/clear` – Clear acc.txt\n"
        "🔹 `/download` – Download acc.txt"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emails = generate_emails(EMAIL_COUNT)
    save_emails(emails)
    reply = "✅ *Emails Generated:*\n" + "\n".join(f"`{e}`" for e in emails)
    await update.message.reply_text(reply, parse_mode="Markdown")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    open(FILE_PATH, "w").close()
    await update.message.reply_text("🧹 *acc.txt cleared.*", parse_mode="Markdown")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        await update.message.reply_document(document=InputFile(FILE_PATH))
    else:
        await update.message.reply_text("⚠️ *acc.txt is empty or missing.*", parse_mode="Markdown")

# ─── Main Entrypoint ────────────────────────────────────────────────────────
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("download", download))

    app.run_polling()
