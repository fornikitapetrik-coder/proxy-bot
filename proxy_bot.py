# -*- coding: utf-8 -*-
import logging, json, os
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8580720167:AAHEpDifcP8qcKFHOxbKXVAoS9psVgk0U5I"
PROXY = {"server": "188.132.184.166", "port": 443, "secret": "289e4b345eca25ad67c1026bee7c6915"}
STARS_PRICE = 10
DB_FILE = "db.json"
ADMIN_ID = 6142844048
logging.basicConfig(level=logging.INFO)

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
        [InlineKeyboardButton("\U0001f6d2 \u041a\u0443\u043f\u0438\u0442\u044c \u043f\u0440\u043e\u043a\u0441\u0438 - 10 \u0437\u0432\u0451\u0437\u0434", callback_data="buy")],
        [InlineKeyboardButton("\U0001f517 \u041c\u043e\u044f \u0440\u0435\u0444\u0435\u0440\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430", callback_data="referral")],
        [InlineKeyboardButton("\U0001f4ca \u041c\u043e\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", callback_data="stats")],
        [InlineKeyboardButton("\U0001f4b0 \u0417\u0430\u0431\u0440\u0430\u0442\u044c \u0431\u043e\u043d\u0443\u0441\u044b", callback_data="claim")],
        [InlineKeyboardButton("\u2753 \u041a\u0430\u043a \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f?", callback_data="howto")],
        [InlineKeyboardButton("\U0001f381 \u041f\u043e\u0436\u0435\u0440\u0442\u0432\u043e\u0432\u0430\u0442\u044c", callback_data="donate")],
        [InlineKeyboardButton("\U0001f198 \u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430", callback_data="support")],
    ])

def donate_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 \u2b50", callback_data="donate_1"), InlineKeyboardButton("5 \u2b50", callback_data="donate_5")],
        [InlineKeyboardButton("10 \u2b50", callback_data="donate_10"), InlineKeyboardButton("50 \u2b50", callback_data="donate_50")],
        [InlineKeyboardButton("100 \u2b50", callback_data="donate_100")],
        [InlineKeyboardButton("\U0001f519 \u041c\u0435\u043d\u044e", callback_data="menu")],
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
        "\U0001f44b \u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c \u0432 RuShield Proxy Bot!\n\n"
        "\U0001f512 MTProxy \u0434\u043b\u044f \u043e\u0431\u0445\u043e\u0434\u0430 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0438 Telegram \u0432 \u0420\u043e\u0441\u0441\u0438\u0438.\n\n"
        "\u2b50 \u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c: 10 \u0437\u0432\u0451\u0437\u0434\n"
        "\U0001f381 \u041f\u0440\u0438\u0433\u043b\u0430\u0448\u0430\u0439 \u0434\u0440\u0443\u0437\u0435\u0439 \u0438 \u043f\u043e\u043b\u0443\u0447\u0430\u0439 1 \u0437\u0432\u0435\u0437\u0434\u0443 \u0437\u0430 \u043a\u0430\u0436\u0434\u0443\u044e \u0438\u0445 \u043f\u043e\u043a\u0443\u043f\u043a\u0443!\n\n"
        "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435:", reply_markup=main_menu())

async def buy(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    if user["has_proxy"]:
        link = proxy_link(PROXY)
        await u.effective_message.reply_text(
            "\u2705 \u0412\u044b \u0443\u0436\u0435 \u043a\u0443\u043f\u0438\u043b\u0438 \u043f\u0440\u043e\u043a\u0441\u0438!\n\n\u0412\u043e\u0442 \u0432\u0430\u0448\u0430 \u0441\u0441\u044b\u043b\u043a\u0430:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("\U0001f517 \u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f", url=link)],
                [InlineKeyboardButton("\U0001f519 \u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e", callback_data="menu")]]))
        return
    await c.bot.send_invoice(chat_id=u.effective_chat.id,
        title="MTProxy \u0434\u043e\u0441\u0442\u0443\u043f",
        description="\u041c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u0439 \u0434\u043e\u0441\u0442\u0443\u043f \u043a MTProxy \u0434\u043b\u044f \u043e\u0431\u0445\u043e\u0434\u0430 \u0420\u043e\u0441\u043a\u043e\u043c\u043d\u0430\u0434\u0437\u043e\u0440\u0430.",
        payload="proxy_purchase", provider_token="", currency="XTR",
        prices=[LabeledPrice("MTProxy", STARS_PRICE)])

async def donate(u, c, amount):
    await c.bot.send_invoice(chat_id=u.effective_chat.id,
        title="\U0001f381 \u041f\u043e\u0436\u0435\u0440\u0442\u0432\u043e\u0432\u0430\u043d\u0438\u0435",
        description="\u0421\u043f\u0430\u0441\u0438\u0431\u043e \u0437\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0443 \u043f\u0440\u043e\u0435\u043a\u0442\u0430! \u0412\u0430\u0448\u0430 \u043f\u043e\u043c\u043e\u0449\u044c \u043f\u043e\u043c\u043e\u0433\u0430\u0435\u0442 \u043d\u0430\u043c \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0442\u044c \u0441\u0435\u0440\u0432\u0435\u0440 \u0438 \u0440\u0430\u0437\u0432\u0438\u0432\u0430\u0442\u044c \u0431\u043e\u0442.",
        payload="donate_" + str(amount), provider_token="", currency="XTR",
        prices=[LabeledPrice("\u041f\u043e\u0436\u0435\u0440\u0442\u0432\u043e\u0432\u0430\u043d\u0438\u0435", amount)])

async def show_donate(u, c):
    await u.effective_message.reply_text(
        "\U0001f381 \u0421\u043f\u0430\u0441\u0438\u0431\u043e \u0437\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0443!\n\n"
        "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u0443\u043c\u043c\u0443 \u043f\u043e\u0436\u0435\u0440\u0442\u0432\u043e\u0432\u0430\u043d\u0438\u044f:",
        reply_markup=donate_menu())

async def howto(u, c):
    await u.effective_message.reply_text(
        "\u2753 \u041a\u0430\u043a \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f:\n\n"
        "1\ufe0f\u20e3 \u041a\u0443\u043f\u0438\u0442\u0435 \u043f\u0440\u043e\u043a\u0441\u0438\n"
        "2\ufe0f\u20e3 \u041f\u043e\u043b\u0443\u0447\u0438\u0442\u0435 \u0441\u0441\u044b\u043b\u043a\u0443\n"
        "3\ufe0f\u20e3 \u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043d\u0430 \u0441\u0441\u044b\u043b\u043a\u0443\n"
        "4\ufe0f\u20e3 \u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u0412\u043a\u043b\u044e\u0447\u0438\u0442\u044c - \u0433\u043e\u0442\u043e\u0432\u043e!\n\n"
        "\U0001f6e1 MTProxy \u0448\u0438\u0444\u0440\u0443\u0435\u0442 \u0442\u0440\u0430\u0444\u0438\u043a \u0438 \u0432\u044b\u0433\u043b\u044f\u0434\u0438\u0442 \u043a\u0430\u043a HTTPS.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("\U0001f6d2 \u041a\u0443\u043f\u0438\u0442\u044c \u043f\u0440\u043e\u043a\u0441\u0438", callback_data="buy")],
            [InlineKeyboardButton("\U0001f519 \u041c\u0435\u043d\u044e", callback_data="menu")]]))

async def support(u, c):
    await u.effective_message.reply_text(
        "\U0001f198 \u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u0432\u0430\u0448 \u0432\u043e\u043f\u0440\u043e\u0441!\n\n"
        "\U0001f447 \u041f\u0440\u043e\u0441\u0442\u043e \u043e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u043f\u0440\u044f\u043c\u043e \u0441\u0435\u0439\u0447\u0430\u0441:",
        reply_markup=ForceReply(selective=True))
    c.user_data["waiting_support"] = True

async def referral(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    bot_username = (await c.bot.get_me()).username
    ref_link = "https://t.me/" + bot_username + "?start=ref_" + str(u.effective_user.id)
    await u.effective_message.reply_text(
        "\U0001f517 \u0412\u0430\u0448\u0430 \u0440\u0435\u0444\u0435\u0440\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430:\n\n" + ref_link + "\n\n"
        "\U0001f4b0 \u0417\u0430 \u043a\u0430\u0436\u0434\u0443\u044e \u043f\u043e\u043a\u0443\u043f\u043a\u0443 - 1 \u0437\u0432\u0435\u0437\u0434\u0430 \u0432\u0430\u043c!\n\n"
        "\U0001f465 \u0420\u0435\u0444\u0435\u0440\u0430\u043b\u043e\u0432: " + str(user["referrals"]) + "\n"
        "\U0001f48e \u0411\u043e\u043d\u0443\u0441\u043e\u0432: " + str(user["balance"]) + " \u0437\u0432\u0435\u0437\u0434",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("\U0001f4b0 \u0417\u0430\u0431\u0440\u0430\u0442\u044c \u0431\u043e\u043d\u0443\u0441\u044b", callback_data="claim")],
            [InlineKeyboardButton("\U0001f519 \u041c\u0435\u043d\u044e", callback_data="menu")]]))

async def stats(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    bot_username = (await c.bot.get_me()).username
    ref_link = "https://t.me/" + bot_username + "?start=ref_" + str(u.effective_user.id)
    status = "\u2705 \u041a\u0443\u043f\u043b\u0435\u043d" if user["has_proxy"] else "\u274c \u041d\u0435 \u043a\u0443\u043f\u043b\u0435\u043d"
    await u.effective_message.reply_text(
        "\U0001f4ca \u0412\u0430\u0448\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430:\n\n"
        "\U0001f512 \u0421\u0442\u0430\u0442\u0443\u0441 \u043f\u0440\u043e\u043a\u0441\u0438: " + status + "\n"
        "\U0001f465 \u0420\u0435\u0444\u0435\u0440\u0430\u043b\u043e\u0432: " + str(user["referrals"]) + "\n"
        "\U0001f48e \u0411\u043e\u043d\u0443\u0441\u043d\u044b\u0439 \u0431\u0430\u043b\u0430\u043d\u0441: " + str(user["balance"]) + " \u0437\u0432\u0435\u0437\u0434\n\n"
        "\U0001f517 \u0412\u0430\u0448\u0430 \u0441\u0441\u044b\u043b\u043a\u0430:\n" + ref_link,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("\U0001f4b0 \u0417\u0430\u0431\u0440\u0430\u0442\u044c \u0431\u043e\u043d\u0443\u0441\u044b", callback_data="claim")],
            [InlineKeyboardButton("\U0001f519 \u041c\u0435\u043d\u044e", callback_data="menu")]]))

async def claim(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    if user["balance"] <= 0:
        await u.effective_message.reply_text(
            "\U0001f614 \u0423 \u0432\u0430\u0441 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442 \u0431\u043e\u043d\u0443\u0441\u043d\u044b\u0445 \u0437\u0432\u0451\u0437\u0434.\n\n\U0001f517 \u041f\u0440\u0438\u0433\u043b\u0430\u0448\u0430\u0439\u0442\u0435 \u0434\u0440\u0443\u0437\u0435\u0439!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("\U0001f517 \u0420\u0435\u0444\u0435\u0440\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430", callback_data="referral")],
                [InlineKeyboardButton("\U0001f519 \u041c\u0435\u043d\u044e", callback_data="menu")]]))
        return
    stars = user["balance"]
    user["balance"] = 0
    save_db(db)
    await u.effective_message.reply_text(
        "\u2705 \u0417\u0430\u043f\u0440\u043e\u0441 \u043d\u0430 \u0432\u044b\u043f\u043b\u0430\u0442\u0443 " + str(stars) + " \u0437\u0432\u0451\u0437\u0434 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d!\n\n\U0001f680 \u0421\u0440\u0435\u0434\u0441\u0442\u0432\u0430 \u0431\u0443\u0434\u0443\u0442 \u043f\u0435\u0440\u0435\u0432\u0435\u0434\u0435\u043d\u044b \u0432 \u0442\u0435\u0447\u0435\u043d\u0438\u0435 24 \u0447\u0430\u0441\u043e\u0432.",
        reply_markup=main_menu())

async def precheckout(u, c):
    q = u.pre_checkout_query
    if q.invoice_payload.startswith("donate_"):
        await q.answer(ok=True)
        return
    db = load_db()
    user = get_user(db, q.from_user.id)
    if user["has_proxy"]:
        await q.answer(ok=False, error_message="\u0412\u044b \u0443\u0436\u0435 \u043f\u0440\u0438\u043e\u0431\u0440\u0435\u043b\u0438 \u043f\u0440\u043e\u043a\u0441\u0438!")
        return
    await q.answer(ok=q.invoice_payload == "proxy_purchase")

async def successful_payment(u, c):
    payload = u.message.successful_payment.invoice_payload
    if payload.startswith("donate_"):
        amount = payload.split("_")[1]
        await u.message.reply_text(
            "\U0001f917 \u0421\u043f\u0430\u0441\u0438\u0431\u043e \u0437\u0430 \u043f\u043e\u0436\u0435\u0440\u0442\u0432\u043e\u0432\u0430\u043d\u0438\u0435 " + amount + " \u0437\u0432\u0451\u0437\u0434!\n\n"
            "\U0001f4aa \u0412\u044b \u043f\u043e\u043c\u043e\u0433\u0430\u0435\u0442\u0435 \u043d\u0430\u043c \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0442\u044c \u0441\u0435\u0440\u0432\u0435\u0440 \u0438 \u0440\u0430\u0437\u0432\u0438\u0432\u0430\u0442\u044c \u0431\u043e\u0442!",
            reply_markup=main_menu())
        return
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
                text="\U0001f389 \u0412\u0430\u0448 \u0440\u0435\u0444\u0435\u0440\u0430\u043b \u0441\u043e\u0432\u0435\u0440\u0448\u0438\u043b \u043f\u043e\u043a\u0443\u043f\u043a\u0443!\n\U0001f48e +1 \u0437\u0432\u0435\u0437\u0434\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u043d\u0430 \u0432\u0430\u0448 \u0431\u0430\u043b\u0430\u043d\u0441!")
        except: pass
    save_db(db)
    link = proxy_link(PROXY)
    await u.message.reply_text(
        "\u2705 \u041e\u043f\u043b\u0430\u0442\u0430 \u043f\u0440\u043e\u0448\u043b\u0430! \u0421\u043f\u0430\u0441\u0438\u0431\u043e! \U0001f389\n\n"
        "\U0001f512 \u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043f\u0440\u043e\u043a\u0441\u0438:\n"
        "\U0001f5a5 \u0421\u0435\u0440\u0432\u0435\u0440: " + PROXY["server"] + "\n"
        "\U0001f50c \u041f\u043e\u0440\u0442: " + str(PROXY["port"]) + "\n"
        "\U0001f511 \u0421\u0435\u043a\u0440\u0435\u0442: " + PROXY["secret"] + "\n\n"
        "\U0001f447 \u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443 \u0434\u043b\u044f \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f!",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("\U0001f517 \u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f", url=link)],
            [InlineKeyboardButton("\U0001f519 \u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e", callback_data="menu")]]))

async def handle_message(u, c):
    user = u.effective_user
    text = u.message.text
    if user.id == ADMIN_ID and u.message.reply_to_message:
        original = u.message.reply_to_message.text or ""
        if "ID:" in original:
            try:
                user_id = int(original.split("ID:")[1].split("\n")[0].strip())
                await c.bot.send_message(chat_id=user_id, text="\U0001f4ac \u041e\u0442\u0432\u0435\u0442 \u043e\u0442 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438:\n\n" + text)
                await u.message.reply_text("\u2705 \u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e!")
            except Exception as e:
                await u.message.reply_text("\u041e\u0448\u0438\u0431\u043a\u0430: " + str(e))
        return
    if c.user_data.get("waiting_support"):
        c.user_data["waiting_support"] = False
        username = "@" + user.username if user.username else "нет"
        await c.bot.send_message(chat_id=ADMIN_ID,
            text="\U0001f198 \u041d\u043e\u0432\u043e\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435!\n\n"
            "\U0001f464 " + (user.first_name or "") + "\n"
            "\U0001f517 " + username + "\n"
            "ID: " + str(user.id) + "\n\n"
            "\U0001f4ac " + text)
        await u.message.reply_text(
            "\u2705 \u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e! \u041c\u044b \u043e\u0442\u0432\u0435\u0442\u0438\u043c \u0432 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u0432\u0440\u0435\u043c\u044f. \U0001f64f",
            reply_markup=main_menu())

async def button_callback(u, c):
    q = u.callback_query
    await q.answer()
    if q.data == "buy": await buy(u, c)
    elif q.data == "howto": await howto(u, c)
    elif q.data == "referral": await referral(u, c)
    elif q.data == "stats": await stats(u, c)
    elif q.data == "claim": await claim(u, c)
    elif q.data == "support": await support(u, c)
    elif q.data == "donate": await show_donate(u, c)
    elif q.data.startswith("donate_"): await donate(u, c, int(q.data.split("_")[1]))
    elif q.data == "menu": await q.message.reply_text("\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e:", reply_markup=main_menu())

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
