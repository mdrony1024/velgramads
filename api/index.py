import os
import telebot
from fastapi import FastAPI, Request
from pymongo import MongoClient

app = FastAPI()

# MongoDB কানেকশন
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.velgram_ads

# টেলিগ্রাম বট টোকেন
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# মিনি অ্যাপের জন্য পয়েন্ট চেক করার এপিআই
@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        user = {"user_id": user_id, "points": 100}
        db.users.insert_one(user)
    user["_id"] = str(user["_id"])
    return user

# বটের ওয়েবহুক রাউট
@app.post("/api/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    update = telebot.types.Update.de_json(payload)
    bot.process_new_updates([update])
    return {"status": "ok"}

# বটের স্টার্ট মেসেজ
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url="https://velgramads.vercel.app/")
    markup.add(telebot.types.InlineKeyboardButton("Open Ads Manager 🚀", web_app=web_app))
    bot.send_message(message.chat.id, "স্বাগতম! আপনার এডস ম্যানেজ করতে নিচের বাটন ক্লিক করুন।", reply_markup=markup)
