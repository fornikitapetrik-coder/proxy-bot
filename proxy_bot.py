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

async def start(u, c):
    await u.message.reply_text("Hello! Pay 1 star to get proxy settings. Use /buy to purchase.", parse_mode="Markdown")

async def buy(u, c):
    await c.bot.send_invoice(chat_id=u.effective_chat.id, title="MTProxy", description="Bypass Telegram blocking", payload="proxy_purchase", currency="XTR", prices=[LabeledPrice("MTProxy", 1)])

async def precheckout(u, c):
    q = u.pre_checkout_query
    await q.answer(ok=q.invoice_payload=="proxy_purchase")

async def successful_payment(u, c):
    link = proxy_link(PROXY)
    await u.message.reply_text("Payment successful! Connect here: " + link, disable_web_page_preview=True)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.run_polling()

if __name__ == "__main__":
    main()
