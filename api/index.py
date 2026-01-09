from fastapi import FastAPI
import telebot
import os
from pymongo import MongoClient

app = FastAPI()

# MongoDB setup
MONGO_URL = "আপনার_লিঙ্ক_এখানে"
client = MongoClient(MONGO_URL)
db = client.ads_bot

# Telegram Bot Setup
BOT_TOKEN = "আপনার_বট_টোকেন"
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "db": "connected"}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    # এখানে ভেরসেল হোস্ট করা লিঙ্ক দিতে হবে
    web_app = telebot.types.WebAppInfo(url="https://your-app.vercel.app")
    button = telebot.types.InlineKeyboardButton(text="Open Modern Dashboard", web_app=web_app)
    markup.add(button)
    
    bot.send_message(message.chat.id, "Welcome to the Modern Ads Manager! ✨", reply_markup=markup)

# Webhook handler
@app.post("/api/webhook")
async def handle_webhook(request: dict):
    if request:
        update = telebot.types.Update.de_json(request)
        bot.process_new_updates([update])
    return {"status": "ok"}
