import random
import time
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv(8396283072:AAET9idaFvPuZy-D6XBTY1qCv34VIXVEIzM)
BOT_USERNAME = "Zhiiiiiiiiiirbot"

DB_PATH = "zhirobot.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()


def get_user(user_id, chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    SELECT attempts, successful, failed, weight, last_time
    FROM users WHERE user_id=? AND chat_id=?
    """, (user_id, chat_id))
    row = c.fetchone()
    conn.close()
    return row


def save_user(user_id, chat_id, name, attempts, successful, failed, weight, last_time):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    INSERT INTO users (user_id, chat_id, name, attempts, successful, failed, weight, last_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id, chat_id) DO UPDATE SET
        name=excluded.name,
        attempts=excluded.attempts,
        successful=excluded.successful,
        failed=excluded.failed,
        weight=excluded.weight,
        last_time=excluded.last_time
    """, (user_id, chat_id, name, attempts, successful, failed, weight, last_time))
    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        "➕ Добавить в группу",
        url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
    )]]

    await update.message.reply_text(
        "🤖 Привет! Я — Жиробот!\n"
        "Пиши /zhiret и становись самым жирным 💪",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def zhiret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    now = int(time.time())

    data = get_user(user.id, chat.id)

    if data:
        attempts, successful, failed, weight, last_time = data
        if now - last_time < 600:
            mins = 10 - (now - last_time) // 60
            await update.message.reply_text(f"⏳ Подожди {mins} минут")
            return
    else:
        attempts = successful = failed = weight = 0

    attempts += 1
    success = random.random() >= 0.2

    if success:
        kg = random.choices(
            [1,2,3,4,5,6,7,8,9,10],
            weights=[30,25,15,10,7,5,4,3,2,1]
        )[0]
        weight += kg
        successful += 1
        await update.message.reply_text(f"🍔 +{kg}кг\n⚖️ Вес: {weight}кг")
    else:
        failed += 1
        await update.message.reply_text("😭 Не получилось")

    save_user(
        user.id, chat.id, user.first_name,
        attempts, successful, failed, weight, now
    )


async def myzhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    data = get_user(user.id, chat.id)

    if not data:
        await update.message.reply_text("📭 Напиши /zhiret")
        return

    attempts, successful, failed, weight, _ = data
    await update.message.reply_text(
        f"👤 {user.first_name}\n"
        f"🔄 Попытки: {attempts}\n"
        f"⚖️ Вес: {weight}кг\n"
        f"✅ Успехи: {successful}\n"
        f"❌ Неудачи: {failed}"
    )


async def topzhirovchata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    SELECT name, weight FROM users
    WHERE chat_id=?
    ORDER BY weight DESC LIMIT 10
    """, (chat.id,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("📭 Пока пусто")
        return

    text = "🏆 Топ чата:\n"
    for i, (name, weight) in enumerate(rows, 1):
        text += f"{i}. {name} — {weight}кг\n"

    await update.message.reply_text(text)


async def topzhirovglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    SELECT name, SUM(weight) FROM users
    GROUP BY user_id
    ORDER BY SUM(weight) DESC LIMIT 10
    """)
    rows = c.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("🌍 Пока пусто")
        return

    text = "🌍 Мировой топ:\n"
    for i, (name, weight) in enumerate(rows, 1):
        text += f"{i}. {name} — {weight}кг\n"

    await update.message.reply_text(text)


def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("zhiret", zhiret))
    app.add_handler(CommandHandler("myzhir", myzhir))
    app.add_handler(CommandHandler("topzhirovchata", topzhirovchata))
    app.add_handler(CommandHandler("topzhirovglobal", topzhirovglobal))

    print("🤖 Жиробот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()

