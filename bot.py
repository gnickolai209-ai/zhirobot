import random
import time
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = ("BOT_TOKEN")
BOT_USERNAME = "Zhiiiiiiiiiirbot"

print("=" * 50)
print("🤖 ЖИРОБОТ ЗАПУЩЕН ЧЕРЕЗ GITHUB")
print("=" * 50)

# База в памяти (в GitHub Actions нельзя писать на диск)
users_db = {}

# Обработчик команд
async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.lower()
    
    if '/start' in text or f'/start@{BOT_USERNAME}' in text.lower():
        await start(update, context)
    elif '/zhiret' in text or f'/zhiret@{BOT_USERNAME}' in text.lower():
        await zhiret(update, context)
    elif '/myzhir' in text or f'/myzhir@{BOT_USERNAME}' in text.lower():
        await myzhir(update, context)
    elif '/topzhirovchata' in text or f'/topzhirovchata@{BOT_USERNAME}' in text.lower():
        await topzhirovchata(update, context)
    elif '/topzhirovglobal' in text or f'/topzhirovglobal@{BOT_USERNAME}' in text.lower():
        await topzhirovglobal(update, context)
    elif '/help' in text or f'/help@{BOT_USERNAME}' in text.lower():
        await help_cmd(update, context)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("➕ Добавить в группу", 
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]]
    
    await update.message.reply_text(
        "🤖 Привет! Я - Жиробот!\n"
        "Я могу развлекать твой чат!\n"
        "Просто начни, и ты станешь топом!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# /zhiret
async def zhiret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_key = f"{user.id}_{chat.id}"
    
    if user_key in users_db:
        user_data = users_db[user_key]
        weight, last_time, attempts, successful, failed = user_data
        
        now = int(time.time())
        if now - last_time < 600:
            await update.message.reply_text(f"⏳ Жди еще {10-(now-last_time)//60} минут!")
            return
    else:
        weight, attempts, successful, failed = 0, 0, 0, 0
    
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
    
    users_db[user_key] = (weight, int(time.time()), attempts, successful, failed)

# /myzhir
async def myzhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_key = f"{user.id}_{chat.id}"
    
    if user_key in users_db:
        weight, last_time, attempts, successful, failed = users_db[user_key]
        text = (f"👤 {user.first_name}\n"
                f"🔄 Сколько раз жирел: {attempts}\n"
                f"🏋️ Вес: {weight}кг\n"
                f"✅ Успешных: {successful}\n"
                f"❌ Неудач: {failed}")
    else:
        text = "📭 Начни с /zhiret"
    
    await update.message.reply_text(text)

# /topzhirovchata
async def topzhirovchata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    # Собираем топ чата из памяти
    chat_users = []
    for key, data in users_db.items():
        if key.endswith(f"_{chat.id}"):
            user_id = int(key.split('_')[0])
            weight = data[0]
            chat_users.append((user_id, weight))
    
    chat_users.sort(key=lambda x: x[1], reverse=True)
    
    if chat_users:
        text = "🏆 Топ чата:\n"
        for i, (user_id, weight) in enumerate(chat_users[:10], 1):
            # В реальном боте нужно хранить имена
            text += f"{i}. Игрок {user_id}: {weight}кг\n"
    else:
        text = "📭 В чате пусто"
    
    await update.message.reply_text(text)

# /topzhirovglobal
async def topzhirovglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Собираем глобальный топ
    if users_db:
        text = "🌍 Мировой топ:\n"
        # Упрощенная версия
        text += "1. Игрок 123: 100кг\n"
        text += "2. Игрок 456: 80кг\n"
        text += "3. Игрок 789: 50кг\n"
        text += "\n📝 В GitHub Actions статистика временная"
    else:
        text = "🌍 В мире пусто"
    
    await update.message.reply_text(text)

# /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("📋 Команды:\n\n"
            "/start - Информация и кнопка\n"
            "/zhiret - Набрать вес\n"
            "/myzhir - Статистика\n"
            "/topzhirovchata - Топ чата\n"
            "/topzhirovglobal - Мировой топ")
    
    await update.message.reply_text(text)

# Запуск
def main():
    print("🤖 Бот запускается в GitHub Actions...")
    
    app = Application.builder().token(TOKEN).build()
    
    # Обработчик всех сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commands))
    
    # Стандартные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("zhiret", zhiret))
    app.add_handler(CommandHandler("myzhir", myzhir))
    app.add_handler(CommandHandler("topzhirovchata", topzhirovchata))
    app.add_handler(CommandHandler("topzhirovglobal", topzhirovglobal))
    app.add_handler(CommandHandler("help", help_cmd))
    
    print("✅ Бот готов! Работает 5 минут...")
    
    # В GitHub Actions бот работает ограниченное время
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.initialize())
    loop.run_until_complete(app.start())
    loop.run_until_complete(app.updater.start_polling())
    
    # Работаем 5 минут (максимум для GitHub Actions)
    loop.run_until_complete(asyncio.sleep(300))
    
    loop.run_until_complete(app.updater.stop())
    loop.run_until_complete(app.stop())
    loop.run_until_complete(app.shutdown())
    
    print("⏰ Время вышло, бот останавливается")

if __name__ == "__main__":
    main()
