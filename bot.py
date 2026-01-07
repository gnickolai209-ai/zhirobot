import os
import json
import random
import time
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ==================== FLASK СЕРВЕР ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Жиробот работает! /start в Telegram"

@app.route('/ping')
def ping():
    return "pong"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask, daemon=True).start()
print("✅ Flask запущен")
# ======================================================

# Токен
TOKEN = os.getenv("BOT_TOKEN", "8396283072:AAFkUveM3dx2EFXlAaeyrpvGHEfZM5RuGGk")
BOT_USERNAME = "Zhiiiiiiiiiirbot"

# База данных
DATA_FILE = 'users_data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, indent=2, ensure_ascii=False)

users_db = load_data()
print(f"👥 Загружено {len(users_db)} пользователей")

# Автосохранение
def auto_save():
    while True:
        time.sleep(120)
        save_data()
        print("💾 Автосохранение")

Thread(target=auto_save, daemon=True).start()

# ==================== КОМАНДЫ ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("➕ Добавить в группу", 
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]]
    await update.message.reply_text(
        "🤖 Привет! Я - Жиробот!\nРазвлекаю чаты!\nНачни с /zhiret!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def zhiret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    key = f"{user.id}_{chat.id}"
    
    now = int(time.time())
    
    if key in users_db:
        data = users_db[key]
        if now - data['last'] < 600:
            wait = 10 - (now - data['last']) // 60
            await update.message.reply_text(f"⏳ Жди {wait} минут!")
            return
        weight = data['weight']
        attempts = data['attempts'] + 1
        successful = data['successful']
        failed = data['failed']
    else:
        weight = 0
        attempts = 1
        successful = 0
        failed = 0
    
    if random.random() < 0.8:  # 80% успех
        kg = random.choices([1,2,3,4,5], weights=[40,30,15,10,5])[0]
        weight += kg
        successful += 1
        msg = random.choice([f"🍔 +{kg}кг!", f"🥤 +{kg}кг!", f"🍟 +{kg}кг!"])
        await update.message.reply_text(f"{msg}\nВес: {weight}кг")
    else:
        failed += 1
        await update.message.reply_text("😭 Не вышло")
    
    users_db[key] = {
        'name': user.first_name,
        'user_id': user.id,
        'chat_id': chat.id,
        'weight': weight,
        'attempts': attempts,
        'successful': successful,
        'failed': failed,
        'last': now
    }
    save_data()

async def myzhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    key = f"{user.id}_{chat.id}"
    
    if key in users_db:
        data = users_db[key]
        text = (f"👤 {user.first_name}\n"
                f"🔄 Попыток: {data['attempts']}\n"
                f"🏋️ Вес: {data['weight']}кг\n"
                f"✅ Успешно: {data['successful']}\n"
                f"❌ Неудач: {data['failed']}")
    else:
        text = "📭 Начни с /zhiret"
    
    await update.message.reply_text(text)

async def topzhirovchata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    top = []
    
    for data in users_db.values():
        if data['chat_id'] == chat.id:
            top.append((data['name'], data['weight']))
    
    top.sort(key=lambda x: x[1], reverse=True)
    
    if top:
        text = "🏆 Топ чата:\n"
        for i, (name, weight) in enumerate(top[:10], 1):
            text += f"{i}. {name}: {weight}кг\n"
    else:
        text = "📭 В чате пусто"
    
    await update.message.reply_text(text)

async def topzhirovglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    totals = {}
    for data in users_db.values():
        name = data['name']
        totals[name] = totals.get(name, 0) + data['weight']
    
    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if top:
        text = "🌍 Мировой топ:\n"
        for i, (name, total) in enumerate(top, 1):
            text += f"{i}. {name}: {total}кг\n"
    else:
        text = "🌍 В мире пусто"
    
    await update.message.reply_text(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("📋 Команды:\n"
            "/start - Инфо\n"
            "/zhiret - Набрать вес (раз в 10 мин)\n"
            "/myzhir - Статистика\n"
            "/topzhirovchata - Топ чата\n"
            "/topzhirovglobal - Мировой топ\n"
            "/help - Помощь")
    await update.message.reply_text(text)

# ==================== ЗАПУСК ====================
def main():
    print("="*50)
    print("🤖 ЖИРОБOT ЗАПУЩЕН НА REPLIT")
    print("="*50)
    
    bot_app = Application.builder().token(TOKEN).build()
    
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("zhiret", zhiret))
    bot_app.add_handler(CommandHandler("myzhir", myzhir))
    bot_app.add_handler(CommandHandler("topzhirovchata", topzhirovchata))
    bot_app.add_handler(CommandHandler("topzhirovglobal", topzhirovglobal))
    bot_app.add_handler(CommandHandler("help", help_cmd))
    
    print("✅ Бот готов!")
    print(f"🔗 URL для пингеров: https://{os.getenv('REPL_SLUG', 'ваш')}.{os.getenv('REPL_OWNER', 'user')}.repl.co")
    
    bot_app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
