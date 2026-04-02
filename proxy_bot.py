# -*- coding: utf-8 -*-
import logging
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8580720167:AAHEpDifcP8qcKFHOxbKXVAoS9psVgk0U5I"
PROXY = {"server": "188.132.184.166", "port": 443, "secret": "289e4b345eca25ad67c1026bee7c6915"}
STARS_PRICE = 1
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def proxy_link(p): return "https://t.me/proxy?server=" + p["server"] + "&port=" + str(p["port"]) + "&secret=" + p["secret"]

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Buy Proxy - 1 Star", callback_data="buy")],
        [InlineKeyboardButton("How to connect?", callback_data="howto")],
    ])

async def start(u, c):
    await u.message.reply_text(
        "Welcome to RuShield Proxy Bot!\n\n"
        "This bot provides MTProxy settings to bypass Telegram blocking in Russia.\n\n"
        "What would you like to do?",
        reply_markup=main_menu()
    )

async def buy(u, c):
    await c.bot.send_invoice(
        chat_id=u.effective_chat.id,
        title="MTProxy Access",
        description="Get instant access to MTProxy settings to bypass Roskomnadzor blocking. One tap connection included.",
        payload="proxy_purchase",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("MTProxy Access", STARS_PRICE)]
    )

async def howto(u, c):
    await u.effective_message.reply_text(
        "How to connect to MTProxy:\n\n"
        "1. Purchase the proxy using the Buy button\n"
        "2. After payment you will receive a link\n"
        "3. Tap the link - Telegram will ask you to apply settings\n"
        "4. Tap Enable - done!\n\n"
        "MTProxy is Telegrams official proxy protocol. "
        "It encrypts your traffic and looks like regular HTTPS.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Buy Proxy - 1 Star", callback_data="buy")]])
    )

async def precheckout(u, c):
    q = u.pre_checkout_query
    await q.answer(ok=q.invoice_payload=="proxy_purchase")

async def successful_payment(u, c):
    link = proxy_link(PROXY)
    await u.message.reply_text(
        "Payment successful! Thank you!\n\n"
        "Your proxy settings:\n"
        "Server: " + PROXY["server"] + "\n"
        "Port: " + str(PROXY["port"]) + "\n"
        "Secret: " + PROXY["secret"] + "\n\n"
        "Tap the button below to connect instantly!",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Connect Now", url=link)]])
    )

async def button_callback(u, c):
    q = u.callback_query
    await q.answer()
    if q.data == "buy":
        await buy(u, c)
    elif q.data == "howto":
        await howto(u, c)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.run_polling()

if __name__ == "__main__":
    main()
