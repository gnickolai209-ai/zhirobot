import os
import random
import time
import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# ===== НАСТРОЙКИ =====
BOT_USERNAME = "Zhiiiiiiiiiirbot"
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment variables")

# ===== БАЗА ДАННЫХ =====
conn = sqlite3.connect("zhirobot.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    chat_id INTEGER,
    name TEXT,
    attempts INTEGER,
    successful INTEGER,
    failed INTEGER,
    weight INTEGER,
    last_time INTEGER,
    PRIMARY KEY (user_id, chat_id)
)
""")
conn.commit()

# ===== КОМАНДЫ =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "➕ Добавить в группу",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    ]]
    await update.message.reply_text(
        "🤖 Я Жиробот!\nЖирей и повышай вес 💪",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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
            await update.message.reply_text("⏳ Подожди 10 минут")
            return
    else:
        weight = attempts = successful = failed = 0

    attempts += 1

    if random.random() >= 0.2:
        kg = random.randint(1, 10)
        weight += kg
        successful += 1
        await update.message.reply_text(f"🍔 +{kg} кг\n🏋️ Вес: {weight} кг")
    else:
        failed += 1
        await update.message.reply_text("😭 Не получилось пожиреть")

    c.execute(
        "REPLACE INTO users VALUES (?,?,?,?,?,?,?,?)",
        (user.id, chat.id, user.first_name, attempts, successful, failed, weight, now)
    )
    conn.commit()

async def myzhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    c.execute(
        "SELECT attempts, successful, failed, weight FROM users WHERE user_id=? AND chat_id=?",
        (user.id, chat.id)
    )
    row = c.fetchone()

    if not row:
        await update.message.reply_text("📭 Напиши /zhiret")
        return

    attempts, successful, failed, weight = row
    await update.message.reply_text(
        f"👤 {user.first_name}\n"
        f"🔄 Попыток: {attempts}\n"
        f"🏋️ Вес: {weight} кг\n"
        f"✅ Успехов: {successful}\n"
        f"❌ Неудач: {failed}"
    )

async def topzhirovchata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    c.execute(
        "SELECT name, weight FROM users WHERE chat_id=? ORDER BY weight DESC LIMIT 10",
        (chat.id,)
    )
    rows = c.fetchall()

    if not rows:
        await update.message.reply_text("В чате пусто")
        return

    text = "🏆 Топ чата:\n"
    for i, (name, weight) in enumerate(rows, 1):
        text += f"{i}. {name} — {weight} кг\n"

    await update.message.reply_text(text)

async def topzhirovglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute(
        "SELECT name, SUM(weight) FROM users GROUP BY user_id ORDER BY SUM(weight) DESC LIMIT 10"
    )
    rows = c.fetch
