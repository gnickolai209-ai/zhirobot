import os
import json
import random
import time
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ==================== FLASK ДЛЯ ПИНГЕРОВ ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Жиробот работает! Используй /start в Telegram"

@app.route('/ping')
def ping():
    return "pong"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()
print("✅ Flask-сервер запущен на порту 8080")
# =============================================================

# Токен из Secrets Replit
TOKEN = os.getenv("BOT_TOKEN", "8396283072:AAFkUveM3dx2EFXlAaeyrpvGHEfZM5RuGGk")
BOT_USERNAME = "Zhiiiiiiiiiirbot"

# Файл для сохранения данных
DATA_FILE = 'users_data.json'
print(f"📁 Файл данных: {DATA_FILE}")

# Загружаем сохранённые данные
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# Сохраняем данные
def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, indent=2, ensure_ascii=False)
    print(f"💾 Сохранено {len(users_db)} пользователей")

users_db = load_data()
print(f"📊 Загружено {len(users_db)} пользователей")

# Автосохранение каждые 2 минуты
def auto_saver():
    while True:
        time.sleep(120)
        save_data()

saver_thread = Thread(target=auto_saver, daemon=True)
saver_thread.start()

# ==================== КОМАНДЫ БОТА ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("➕ Добавить в группу", 
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]]
    await update.message.reply_text(
        "🤖 Привет! Я - Жиробот!\nЯ развлекаю чаты!\nПросто начни, и ты станешь топом!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def zhiret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_key = f"{user.id}_{chat.id}"
    
    now = int(time.time())
    
    if user_key in users_db:
        data = users_db[user_key]
        if now - data['last_time'] < 600:
            wait = 10 - (now - data['last_time']) // 60
            await update.message.reply_text(f"⏳ Жди ещё {wait} минут!")
            return
        
        weight = data['weight']
        attempts = data['attempts']
        successful = data['successful']
        failed = data['failed']
    else:
        weight = attempts = successful = failed = 0
    
    attempts += 1
    success = random.random() >= 0.2
    
    if success:
        kg = random.choices([1,2,3,4,5], weights=[40,30,15,10,5])[0]
        weight += kg
        successful += 1
        messages = [f"🍔 +{kg}кг!", f"🥤 +{kg}кг!", f"🍟 +{kg}кг!"]
        await update.message.reply_text(f"{random.choice(messages)}\nВес: {weight}кг")
    else:
        failed += 1
        await update.message.reply_text("😭 Не получилось набрать вес")
    
    users_db[user_key] = {
        'name': user.first_name,
        'user_id': user.id,
        'chat_id': chat.id,
        'weight': weight,
        'attempts': attempts,
        'successful': successful,
        'failed': failed,
        'last_time': now
    }
    save_data()

async def myzhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_key = f"{user.id}_{chat.id}"
    
    if user_key in users_db:
        data = users_db[user_key]
        text = (f"👤 {user.first_name}\n"
                f"🔄 Попыток: {data['attempts']}\n"
                f"🏋️ Вес: {data['weight']}кг\n"
                f"✅ Успешных: {data['successful']}\n"
                f"❌ Неудач: {data['failed']}")
    else:
        text = "📭 Начни с /zhiret"
    
    await update.message.reply_text(text)

async def topzhirovchata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_users = []
    
    for key, data in users_db.items():
        if data['chat_id'] == chat.id:
            chat_users.append((data['name'], data['weight']))
    
    chat_users.sort(key=lambda x: x[1], reverse=True)
    
    if chat_users:
        text = "🏆 Топ чата:\n"
        for i, (name, weight) in enumerate(chat_users[:10], 1):
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
        for i, (name, weight) in enumerate(top, 1):
            text += f"{i}. {name}: {weight}кг\n"
    else:
        text = "🌍 В мире пусто"
    
    await update.message.reply_text(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("📋 Команды:\n\n"
            "/start - Информация\n"
            "/zhiret - Набрать вес (раз в 10 мин)\n"
            "/myzhir - Статистика\n"
            "/topzhirovchata - Топ чата\n"
            "/topzhirovglobal - Мировой топ\n"
            "/help - Помощь")
    await update.message.reply_text(text)

# ==================== ЗАПУСК БОТА ====================
def main():
    print("=" * 50)
    print("🤖 ЖИРОБОТ ЗАПУЩЕН")
    print("🌐 Web-сервер: http://0.0.0.0:8080")
    print("📁 Данные сохраняются в JSON")
    print("⏰ Автосохранение каждые 2 минуты")
    print("=" * 50)
    
    app_bot = Application.builder().token(TOKEN).build()
    
    # Команды
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("zhiret", zhiret))
    app_bot.add_handler(CommandHandler("myzhir", myzhir))
    app_bot.add_handler(CommandHandler("topzhirovchata", topzhirovchata))
    app_bot.add_handler(CommandHandler("topzhirovglobal", topzhirovglobal))
    app_bot.add_handler(CommandHandler("help", help_cmd))
    
    # Обработка текста
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.text:
            text = update.message.text.lower()
            if text.startswith('/'):
                await update.message.reply_text("ℹ️ Используй /help для списка команд")
    
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Бот запущен и готов к работе!")
    print("🔗 Добавь этот URL в UptimeRobot:")
    print(f"   https://{os.getenv('REPL_SLUG', 'ваш-repl')}.{os.getenv('REPL_OWNER', 'user')}.repl.co")
    
    app_bot.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
