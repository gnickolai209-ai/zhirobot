import os
import random
import time
import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

logging.basicConfig(level=logging.INFO)

# === ТОКЕН ТОЛЬКО ИЗ ENV (Render) ===
TOKEN = os.getenv(8396283072:AAET9idaFvPuZy-D6XBTY1qCv34VIXVEIzM)
BOT_USERNAME = "Zhiiiiiiiiiirbot"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment variables")

# === БАЗА ДАННЫХ (SQLite, сохраняется пока сервис живёт) ===
conn = sqlite3.connect("zhirobot.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    chat_id INTEGER,
    name TEXT,
    attempts INTEGER DEFAULT 0,
    successful INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    weight INTEGER DEFAULT 0,
    last_time INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, chat_id)
)
""")
conn.commit()

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "➕ Добавить в группу",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    ]]
    await update.message.reply_text(
        "🤖 Привет! Я — Жиробот!\n"
        "Жирей, соревнуйся и попадай в топ 🏆",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# === /zhiret ===
async def zhiret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    now = int(time.time())

    c.execute(
        "SELECT weight, last_time, attempts, successful, failed FROM users WHERE user_id=? AND chat_id=?",
        (user.id, chat.id)
    )
    row = c.fetchone()

    if row:
        weight, last_time, attempts, successful, failed = row
        if now - last_time < 600:
            minutes = 10 - (now - last_time) // 60
            await update.message.reply_text(f"⏳ Подожди {minutes} минут")
            return
    else:
        weight = attempts = successful = failed = 0

    attempts += 1
    success = random.random() >= 0.2

    if success:
        kg = random.choices(
            [1,2,3,4,5,6,7,8,9,10],
            weights=[30,25,15,10,7,5,4,3,2,1]
        )[0]
        weight += kg
        successful += 1
        await update.message.reply_text(
            f"🍔 Ты нажрал +{kg}кг!\n"
            f"🏋️ Текущий вес: {weight}кг"
        )
    else:
        failed += 1
        await update.message.reply_text("😭 Сегодня не получилось пожиреть")

    c.execute("""
        REPLACE INTO users VALUES (?,?,?,?,?,?,?,?)
    """, (user.id, chat.id, user.first_name, attempts, successful, failed, weight, now))
    conn.commit()

# === /myzhir ===
async def myzhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    c.execute(
        "SELECT attempts, successful, failed, weight FROM users WHERE user_id=? AND chat_id=?",
        (user.id, chat.id)
    )
    row = c.fetchone()

    if not row:
        await update.message.reply_text("📭 Сначала напиши /zhiret")
        return

    attempts, successful, failed, weight = row
    await update.message.reply_text(
        f"👤 {user.first_name}\n"
        f"🔄 Попыток: {attempts}\n"
        f"🏋️ Вес: {weight}кг\n"
        f"✅ Успехов: {successful}\n"
        f"❌ Неудач: {failed}"
    )

# === /topzhirovchata ===
async def topzhirovchata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    c.execute(
        "SELECT name, weight FROM users WHERE chat_id=? ORDER BY weight DESC LIMIT 10",
        (chat.id,)
    )
    rows = c.fetchall()

    if not rows:
        await update.message.reply_text("📭 В чате ещё никто не жирел")
        return

    text = "🏆 Топ жиробасов чата:\n"
    for i, (name, weight) in enumerate(rows, 1):
        text += f"{i}. {name} — {weight}кг\n"

    await update.message.reply_text(text)

# === /topzhirovglobal ===
async def topzhirovglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute("""
        SELECT name, SUM(weight) FROM users
        GROUP BY user_id
        ORDER BY SUM(weight) DESC
        LIMIT 10
    """)
    rows = c.fetchall()

    if not rows:
        await update.message.reply_text("🌍 В мире ещё никто не жирел")
        return

    text = "🌍 Мировой топ жиробасов:\n"
    for i, (name, weight) in enumerate(rows, 1):
        text += f"{i}. {name} — {weight}кг\n"

    await update.message.reply_text(text)

# === /help ===
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/zhiret — пожиреть\n"
        "/myzhir — твоя статистика\n"
        "/topzhirovchata — топ чата\n"
        "/topzhirovglobal — мировой топ"
    )

# === ЗАПУСК ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("zhiret", zhiret))
    app.add_handler(CommandHandler("myzhir", myzhir))
    app.add_handler(CommandHandler("topzhirovchata", topzhirovchata))
    app.add_handler(CommandHandler("topzhirovglobal", topzhirovglobal))
    app.add_handler(CommandHandler("help", help_cmd))

    app.run_polling()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()

