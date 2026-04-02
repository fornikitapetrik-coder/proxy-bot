# -*- coding: utf-8 -*-
import logging, json, os
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8580720167:AAHEpDifcP8qcKFHOxbKXVAoS9psVgk0U5I"
PROXY = {"server": "188.132.184.166", "port": 443, "secret": "289e4b345eca25ad67c1026bee7c6915"}
STARS_PRICE = 5
DB_FILE = "db.json"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f)

def get_user(db, user_id):
    uid = str(user_id)
    if uid not in db: db[uid] = {"balance": 0, "purchases": 0, "referrals": 0, "referred_by": None}
    return db[uid]

def proxy_link(p): return "https://t.me/proxy?server=" + p["server"] + "&port=" + str(p["port"]) + "&secret=" + p["secret"]

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Купить прокси - 5 звезд", callback_data="buy")],
        [InlineKeyboardButton("🔗 Моя реферальная ссылка", callback_data="referral")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton("💰 Забрать бонусы", callback_data="claim")],
        [InlineKeyboardButton("❓ Как подключиться?", callback_data="howto")],
    ])

async def start(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    if c.args and c.args[0].startswith("ref_"):
        ref_id = c.args[0][4:]
        if ref_id != str(u.effective_user.id) and user["referred_by"] is None:
            user["referred_by"] = ref_id
    save_db(db)
    await u.message.reply_text(
        "👋 Добро пожаловать в RuShield Proxy Bot!\n\n"
        "🔒 MTProxy для обхода блокировки Telegram в России.\n\n"
        "⭐ Стоимость: 5 звёзд\n"
        "🎁 Приглашай друзей и получай 1 звезду за каждую их покупку!\n\n"
        "Выберите действие:", reply_markup=main_menu())

async def buy(u, c):
    await c.bot.send_invoice(chat_id=u.effective_chat.id, title="🔒 MTProxy доступ",
        description="Мгновенный доступ к MTProxy для обхода Роскомнадзора. Подключение в один клик!",
        payload="proxy_purchase", provider_token="", currency="XTR",
        prices=[LabeledPrice("MTProxy доступ", STARS_PRICE)])

async def howto(u, c):
    await u.effective_message.reply_text(
        "❓ Как подключиться:\n\n1️⃣ Купите прокси\n2️⃣ Получите ссылку\n"
        "3️⃣ Нажмите на ссылку\n4️⃣ Нажмите Включить — готово! 🎉\n\n"
        "🛡 MTProxy шифрует трафик и выглядит как HTTPS.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Купить прокси", callback_data="buy")],
            [InlineKeyboardButton("🔙 Меню", callback_data="menu")]]))

async def referral(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    bot_username = (await c.bot.get_me()).username
    ref_link = "https://t.me/" + bot_username + "?start=ref_" + str(u.effective_user.id)
    await u.effective_message.reply_text(
        "🔗 Ваша реферальная ссылка:\n\n" + ref_link + "\n\n"
        "💰 За каждую покупку по ссылке — 1 звезда вам!\n\n"
        "👥 Рефералов: " + str(user["referrals"]) + "\n"
        "💎 Бонусов накоплено: " + str(user["balance"]) + " звезд",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Забрать бонусы", callback_data="claim")],
            [InlineKeyboardButton("🔙 Меню", callback_data="menu")]]))

async def stats(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    bot_username = (await c.bot.get_me()).username
    ref_link = "https://t.me/" + bot_username + "?start=ref_" + str(u.effective_user.id)
    await u.effective_message.reply_text(
        "📊 Ваша статистика:\n\n"
        "🛒 Покупок: " + str(user["purchases"]) + "\n"
        "👥 Рефералов: " + str(user["referrals"]) + "\n"
        "💎 Бонусный баланс: " + str(user["balance"]) + " звезд\n\n"
        "🔗 Ваша ссылка:\n" + ref_link,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Забрать бонусы", callback_data="claim")],
            [InlineKeyboardButton("🔙 Меню", callback_data="menu")]]))

async def claim(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    if user["balance"] <= 0:
        await u.effective_message.reply_text(
            "😔 У вас пока нет бонусных звёзд.\n\n"
            "🔗 Приглашайте друзей и зарабатывайте!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Реферальная ссылка", callback_data="referral")],
                [InlineKeyboardButton("🔙 Меню", callback_data="menu")]]))
        return
    stars = user["balance"]
    user["balance"] = 0
    save_db(db)
    await u.effective_message.reply_text(
        "✅ Запрос на выплату " + str(stars) + " звезд отправлен!\n\n"
        "Средства будут переведены в течение 24 часов. 🚀",
        reply_markup=main_menu())

async def precheckout(u, c):
    q = u.pre_checkout_query
    await q.answer(ok=q.invoice_payload == "proxy_purchase")

async def successful_payment(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    user["purchases"] += 1
    ref_id = user.get("referred_by")
    if ref_id and ref_id in db:
        db[ref_id]["balance"] += 1
        db[ref_id]["referrals"] += 1
        try:
            await c.bot.send_message(chat_id=int(ref_id),
                text="🎉 Ваш реферал совершил покупку!\n💎 +1 звезда добавлена на ваш баланс!")
        except: pass
    save_db(db)
    link = proxy_link(PROXY)
    await u.message.reply_text(
        "✅ Оплата прошла! Спасибо! 🎉\n\n"
        "🔒 Настройки прокси:\n"
        "🖥 Сервер: " + PROXY["server"] + "\n"
        "🔌 Порт: " + str(PROXY["port"]) + "\n"
        "🔑 Секрет: " + PROXY["secret"] + "\n\n"
        "👇 Нажмите кнопку для подключения!",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Подключиться", url=link)],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="menu")]]))

async def button_callback(u, c):
    q = u.callback_query
    await q.answer()
    if q.data == "buy": await buy(u, c)
    elif q.data == "howto": await howto(u, c)
    elif q.data == "referral": await referral(u, c)
    elif q.data == "stats": await stats(u, c)
    elif q.data == "claim": await claim(u, c)
    elif q.data == "menu": await q.message.reply_text("Главное меню:", reply_markup=main_menu())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.run_polling()

if __name__ == "__main__":
    main()
