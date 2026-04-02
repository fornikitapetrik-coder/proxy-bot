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
        [InlineKeyboardButton("Kupit proksi - 10 zvezd", callback_data="buy")],
        [InlineKeyboardButton("Moya referalnaya ssylka", callback_data="referral")],
        [InlineKeyboardButton("Moya statistika", callback_data="stats")],
        [InlineKeyboardButton("Zabrat bonusy", callback_data="claim")],
        [InlineKeyboardButton("Kak podklyuchitsya?", callback_data="howto")],
        [InlineKeyboardButton("Podderzhka", callback_data="support")],
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
        "Dobro pozhalovat v RuShield Proxy Bot!\n\n"
        "Zashhita ot blokirovki Telegram v Rossii.\n\n"
        "Stoimost: 10 zvezd\n"
        "Priglashaj druzej i poluchai 1 zvezdu za kazhduyu ih pokupku!\n\n"
        "Vyberi dejstvie:", reply_markup=main_menu())

async def buy(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    if user["has_proxy"]:
        link = proxy_link(PROXY)
        await u.effective_message.reply_text(
            "Vy uzhe kupili proksi!\n\nVot vasha ssylka:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Podklyuchitsya", url=link)],
                [InlineKeyboardButton("Glavnoe menyu", callback_data="menu")]]))
        return
    await c.bot.send_invoice(chat_id=u.effective_chat.id, title="MTProxy dostup",
        description="Mgnovennyj dostup k MTProxy dlya obhoda Roskomnadzora.",
        payload="proxy_purchase", provider_token="", currency="XTR",
        prices=[LabeledPrice("MTProxy dostup", STARS_PRICE)])

async def howto(u, c):
    await u.effective_message.reply_text(
        "Kak podklyuchitsya:\n\n1. Kupite proksi\n2. Poluchite ssylku\n"
        "3. Nazhmite na ssylku\n4. Nazhmite Vklyuchit - gotovo!\n\n"
        "MTProxy shifruet trafik i vyglyadit kak HTTPS.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Kupit proksi", callback_data="buy")],
            [InlineKeyboardButton("Menyu", callback_data="menu")]]))

async def support(u, c):
    await u.effective_message.reply_text(
        "Napishite vash vopros i my otvetim vam v blizhajshee vremya!\n\nProsto otpravte soobshenie pryamo sejchas:",
        reply_markup=ForceReply(selective=True, input_field_placeholder="Vash vopros..."))
    c.user_data["waiting_support"] = True

async def referral(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    bot_username = (await c.bot.get_me()).username
    ref_link = "https://t.me/" + bot_username + "?start=ref_" + str(u.effective_user.id)
    await u.effective_message.reply_text(
        "Vasha referalnaya ssylka:\n\n" + ref_link + "\n\n"
        "Za kazhduyu pokupku po ssylke - 1 zvezda vam!\n\n"
        "Referalov: " + str(user["referrals"]) + "\n"
        "Bonusov nakopleno: " + str(user["balance"]) + " zvezd",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Zabrat bonusy", callback_data="claim")],
            [InlineKeyboardButton("Menyu", callback_data="menu")]]))

async def stats(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    bot_username = (await c.bot.get_me()).username
    ref_link = "https://t.me/" + bot_username + "?start=ref_" + str(u.effective_user.id)
    status = "Kuplen" if user["has_proxy"] else "Ne kuplen"
    await u.effective_message.reply_text(
        "Vasha statistika:\n\n"
        "Status proksi: " + status + "\n"
        "Referalov: " + str(user["referrals"]) + "\n"
        "Bonusnyj balans: " + str(user["balance"]) + " zvezd\n\n"
        "Vasha ssylka:\n" + ref_link,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Zabrat bonusy", callback_data="claim")],
            [InlineKeyboardButton("Menyu", callback_data="menu")]]))

async def claim(u, c):
    db = load_db()
    user = get_user(db, u.effective_user.id)
    if user["balance"] <= 0:
        await u.effective_message.reply_text(
            "U vas poka net bonusnyh zvezd.\n\nPriglashajte druzej i zarabatyvajte!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Referalnaya ssylka", callback_data="referral")],
                [InlineKeyboardButton("Menyu", callback_data="menu")]]))
        return
    stars = user["balance"]
    user["balance"] = 0
    save_db(db)
    await u.effective_message.reply_text(
        "Zapros na vyplatu " + str(stars) + " zvezd otpravlen!\n\nSredstva budut perevedeny v techenie 24 chasov.",
        reply_markup=main_menu())

async def precheckout(u, c):
    q = u.pre_checkout_query
    db = load_db()
    user = get_user(db, q.from_user.id)
    if user["has_proxy"]:
        await q.answer(ok=False, error_message="Vy uzhe priobrely proksi!")
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
            await c.bot.send_message(chat_id=int(ref_id), text="Vash referal sovershil pokupku! +1 zvezda dobavlena na vash balans!")
        except: pass
    save_db(db)
    link = proxy_link(PROXY)
    await u.message.reply_text(
        "Oplata proshla! Spasibo!\n\n"
        "Nastrojki proksi:\n"
        "Server: " + PROXY["server"] + "\n"
        "Port: " + str(PROXY["port"]) + "\n"
        "Sekret: " + PROXY["secret"] + "\n\n"
        "Nazhmite knopku dlya podklyucheniya!",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Podklyuchitsya", url=link)],
            [InlineKeyboardButton("Glavnoe menyu", callback_data="menu")]]))

async def handle_message(u, c):
    user = u.effective_user
    text = u.message.text
    if user.id == ADMIN_ID and u.message.reply_to_message:
        original = u.message.reply_to_message.text or ""
        if "ID polzovatelya:" in original:
            try:
                user_id = int(original.split("ID polzovatelya:")[1].split("\n")[0].strip())
                await c.bot.send_message(chat_id=user_id, text="Otvet ot podderzhki:\n\n" + text)
                await u.message.reply_text("Soobshenie otpravleno polzovatelyu!")
            except Exception as e:
                await u.message.reply_text("Oshibka: " + str(e))
        return
    if c.user_data.get("waiting_support"):
        c.user_data["waiting_support"] = False
        username = "@" + user.username if user.username else "net username"
        await c.bot.send_message(chat_id=ADMIN_ID,
            text="Novoe soobshenie v podderzhku!\n\n"
            "Imya: " + (user.first_name or "") + "\n"
            "Username: " + username + "\n"
            "ID polzovatelya: " + str(user.id) + "\n\n"
            "Soobshenie:\n" + text)
        await u.message.reply_text("Vashe soobshenie otpravleno v podderzhku! My otvetim vam v blizhajshee vremya.",
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
    elif q.data == "menu": await q.message.reply_text("Glavnoe menyu:", reply_markup=main_menu())

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
