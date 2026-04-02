# -*- coding: utf-8 -*-
import logging, json, os
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8580720167:AAHEpDifcP8qcKFHOxbKXVAoS9psVgk0U5I"
PROXY = {"server": "188.132.184.166", "port": 443, "secret": "289e4b345eca25ad67c1026bee7c6915"}
STARS_PRICE = 5
DB_FILE = "db.json"
ADMIN_ID = 6142844048
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
    if uid not in db: db[uid] = {"balance": 0, "purchases": 0, "referrals": 0, "referred_by": None, "has_proxy": False}
    if "has_proxy" not in db[uid]: db[uid]["has_proxy"] = db[uid]["purchases"] > 0
    return db[uid]

def proxy_link(p): return "https://t.me/proxy?server=" + p["server"] + "&port=" + str(p["port"]) + "&secret=" + p["secret"]

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Купить прокси - 5 звезд", callback_data="buy")],
        [InlineKeyboardButton("🔗 Моя реферальная ссылка", callback_data="referral")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton("💰 Забрать бонусы", callback_data="claim")],
        [InlineKeyboardButton("❓ Как подключиться?", callback_data="howto")],
        [InlineKeyboardButton("🆘 Поддержка", callback_data="support")],
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
    db = load_db()
    user = get_user(db, u.effective_user.id)
    if user["has_proxy"]:
        link = proxy_link(PROXY)
        await u.effective_message.reply_text(
            "✅ Вы уже купили прокси!\n\n👇 Вот ваша ссылка для подключения:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Подключиться", url=link)],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="menu")]]))
        return
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

async def support(u, c):
    user = u.effective_user
    await u.effective_message.reply_text(
        "🆘 Напишите ваш вопрос и мы ответим вам в ближайшее время!\n\n"
        "👇 Просто отправьте сообщение прямо сейчас:",
        reply_markup=ForceReply(selective=True, input_field_placeholder="Ваш вопрос...")
    )
    c.user_data["waiting_support"] = True

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
    status = "✅ Куплен" if user["has_proxy"] else "❌ Не куплен"
    await u.effective_message.reply_text(
        "📊 Ваша статистика:\n\n"
        "🔒 Статус прокси: " + status + "\n"
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
            "😔 У вас пока нет бонусных звёзд.\n\n🔗 Приглашайте друзей и зарабатывайте!",
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
    db = load_db()
    user = get_user(db, q.from_user.id)
    if user["has_proxy"]:
        await q.answer(ok=False, error_message="Вы уже приобрели прокси!")
        return
    await q.answer(ok=q.invoice_payload == "proxy_purchase")

async def successful_payment(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    user["purchases"] += 1
    user["has_proxy"] = True
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

async def handle_message(u, c):
    user = u.effective_user
    text = u.message.text

    # Admin replying to a user
    if user.id == ADMIN_ID and u.message.reply_to_message:
        original = u.message.reply_to_message.text or ""
        if "ID пользователя:" in original:
            try:
                user_id = int(original.split("ID пользователя:")[1].split("\n")[0].strip())
                await c.bot.send_message(chat_id=user_id,
                    text="💬 Ответ от поддержки:\n\n" + text)
                await u.message.reply_text("✅ Сообщение отправлено пользователю!")
            except Exception as e:
                await u.message.reply_text("❌ Ошибка: " + str(e))
        return

    # User sending support message
    if c.user_data.get("waiting_support"):
        c.user_data["waiting_support"] = False
        username = "@" + user.username if user.username else "нет username"
        await c.bot.send_message(
            chat_id=ADMIN_ID,
            text="🆘 Новое сообщение в поддержку!\n\n"
                "👤 Имя: " + (user.first_name or "") + "\n"
                "🔗 Username: " + username + "\n"
                "🆔 ID пользователя: " + str(user.id) + "\n\n"
                "💬 Сообщение:\n" + text
        )
        await u.message.reply_text(
            "✅ Ваше сообщение отправлено в поддержку!\n\n"
            "Мы ответим вам в ближайшее время. 🙏",
            reply_markup=main_menu()
        )

async def button_callback(u, c):
    q = u.callback_query
    await q.answer()
    if q.data == "buy": await buy(u, c)
    elif q.data == "howto": await howto(u, c)
    elif q.data == "referral": await referral(u, c)
    elif q.data == "stats": await stats(u, c)
    elif q.data == "claim": await claim(u, c)
    elif q.data == "support": await support(u, c)
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
