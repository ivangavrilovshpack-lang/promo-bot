import telebot
from telebot import types
import config
import database as db
import threading
import time
import random
import parser
from flask import Flask
import os

app = Flask(__name__)
bot = telebot.TeleBot(config.TOKEN)

VIP_PRICE = 99
PAYMENT_LINK = "https://www.donationalerts.com/r/ваш_ник"

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

@bot.callback_query_handler(func=lambda call: call.data == "vip")
def vip(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Оплатить 99₽", url=PAYMENT_LINK))
    markup.add(types.InlineKeyboardButton("✅ Я оплатил", callback_data="vip_paid"))
    bot.send_message(call.message.chat.id,
        f"💎 VIP-доступ — {VIP_PRICE}₽/мес\n\nЧто даёт VIP:\n• Эксклюзивные промокоды\n• Первым узнаёшь о раздачах\n• Безлимитные запросы\n\nПосле оплаты нажми «Я оплатил».",
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "vip_paid")
def vip_paid(call):
    bot.send_message(call.message.chat.id, "✅ Заявка отправлена админу.")
    bot.send_message(config.ADMIN_ID, f"🔔 Пользователь @{call.from_user.username or 'без ника'} хочет VIP.")

@bot.callback_query_handler(func=lambda call: call.data == "ad_request")
def ad_request(call):
    msg = bot.send_message(call.message.chat.id, "📝 Напиши текст рекламы (до 500 символов):")
    bot.register_next_step_handler(msg, process_ad_text)

def process_ad_text(message):
    if len(message.text) > 500:
        bot.send_message(message.chat.id, "❌ Слишком длинный текст.")
        return
    bot.send_message(config.ADMIN_ID,
        f"📢 НОВАЯ ЗАЯВКА НА РЕКЛАМУ\nОт: @{message.from_user.username or 'без ника'}\nТекст:\n{message.text}")
    bot.send_message(message.chat.id, "✅ Заявка отправлена админу.")

@bot.callback_query_handler(func=lambda call: call.data == "get_promo")
def get_promo(call):
    promo = db.get_random_promo()
    if promo:
        bot.send_message(call.message.chat.id, f"🎉 Промокод:\n<b>{promo[1]}</b>\n{promo[2]}\n🔗 {promo[3]}", parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "🔍 Пока нет промокодов.")

@bot.callback_query_handler(func=lambda call: call.data == "free_games")
def free_games(call):
    games = parser.parse_free_games()
    if games:
        text = "🎮 Бесплатные игры:\n\n"
        for g in games[:5]:
            text += f"• <b>{g['title']}</b>\n{g['link']}\n\n"
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "😴 Пока нет игр.")

@bot.callback_query_handler(func=lambda call: call.data == "admin" and call.from_user.id == config.ADMIN_ID)
def admin_panel(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🔁 Запустить парсер", callback_data="run_parser"))
    bot.send_message(call.message.chat.id, "⚙️ Админ-панель:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "run_parser" and call.from_user.id == config.ADMIN_ID)
def run_parser(call):
    bot.send_message(call.message.chat.id, "⏳ Парсинг...")
    promos = parser.parse_promocodes()
    bot.send_message(call.message.chat.id, f"✅ Добавлено {len(promos)} промокодов.")

def auto_publish():
    while True:
        time.sleep(1800)
        promo = db.get_random_promo()
        if promo:
            text = f"🔥 НОВЫЙ ПРОМОКОД!\n<b>{promo[1]}</b>\n{promo[2]}"
            try:
                bot.send_message(config.CHANNEL_ID, text, parse_mode='HTML')
            except:
                pass

@app.route('/')
def home():
    return "✅ Бот работает!"

if __name__ == "__main__":
    db.init_db()
    threading.Thread(target=auto_publish, daemon=True).start()
    # Запускаем бота в отдельном потоке
    threading.Thread(target=bot.polling, daemon=True).start()
    # Запускаем веб-сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
