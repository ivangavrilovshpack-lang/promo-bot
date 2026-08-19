import telebot
from telebot import types
import config
import database as db
import threading
import time
import random
import parser

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    db.init_db()
    db.add_user(message.from_user.id, message.from_user.username)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🔥 Получить промокод", callback_data="get_promo"))
    markup.add(types.InlineKeyboardButton("🎮 Бесплатные игры", callback_data="free_games"))
    markup.add(types.InlineKeyboardButton("💎 VIP-доступ", callback_data="vip"))
    markup.add(types.InlineKeyboardButton("📢 Заказать рекламу", callback_data="ad_request"))
    if message.from_user.id == config.ADMIN_ID:
        markup.add(types.InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin"))
    bot.send_message(message.chat.id, "🛒 Добро пожаловать в бота по промокодам!\n\nЯ собираю лучшие скидки со всего интернета.\nНажми кнопку ниже, чтобы получить промокод.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "get_promo")
def get_promo(call):
    promo = db.get_random_promo()
    if promo:
        bot.send_message(call.message.chat.id, f"🎉 Твой промокод:\n\n<b>{promo[1]}</b>\n\n📝 {promo[2]}\n🔗 Ссылка: {promo[3]}\n⏳ {promo[4]}", parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "🔍 Пока нет новых промокодов. Загляни позже!")

@bot.callback_query_handler(func=lambda call: call.data == "free_games")
def free_games(call):
    games = parser.parse_free_games()
    if games:
        text = "🎮 Бесплатные игры прямо сейчас:\n\n"
        for g in games[:5]:
            text += f"• <b>{g['title']}</b>\n{g['link']}\n\n"
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "😴 Пока нет бесплатных игр. Загляни завтра.")

@bot.callback_query_handler(func=lambda call: call.data == "admin" and call.from_user.id == config.ADMIN_ID)
def admin_panel(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="stats"))
    markup.add(types.InlineKeyboardButton("➕ Добавить промокод", callback_data="add_promo"))
    markup.add(types.InlineKeyboardButton("📨 Заявки на рекламу", callback_data="ads_requests"))
    markup.add(types.InlineKeyboardButton("🔁 Запустить парсер сейчас", callback_data="run_parser"))
    bot.send_message(call.message.chat.id, "⚙️ Админ-панель:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "run_parser" and call.from_user.id == config.ADMIN_ID)
def run_parser(call):
    bot.send_message(call.message.chat.id, "⏳ Парсинг запущен...")
    promos = parser.parse_promocodes()
    bot.send_message(call.message.chat.id, f"✅ Добавлено {len(promos)} новых промокодов.")

def auto_publish():
    while True:
        time.sleep(1800)
        promo = db.get_random_promo()
        if promo:
            text = f"🔥 НОВЫЙ ПРОМОКОД!\n\n<b>{promo[1]}</b>\n{promo[2]}\n🔗 {promo[3]}"
            try:
                bot.send_message(config.CHANNEL_ID, text, parse_mode='HTML')
            except:
                pass

if __name__ == "__main__":
    db.init_db()
    threading.Thread(target=auto_publish, daemon=True).start()
    print("🤖 Бот запущен!")
    bot.polling(none_stop=True)
