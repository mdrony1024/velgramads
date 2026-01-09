import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import telebot
from pymongo import MongoClient

app = FastAPI()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.velgram_ads

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# ১. এই অংশটি নতুন যোগ করা হয়েছে (যাতে index.html দেখা যায়)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("public/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Index file not found in public folder</h1>"

# ২. ইউজার ডাটা পাওয়ার এপিআই (রাউট থেকে /api বাদ দেওয়া হয়েছে)
@app.get("/user/{user_id}")
async def get_user(user_id: str):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        user = {"user_id": user_id, "points": 100}
        db.users.insert_one(user)
    user["_id"] = str(user["_id"])
    return user

# ৩. টেলিগ্রাম বটের ওয়েবহুক রাউট
@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    update = telebot.types.Update.de_json(payload)
    bot.process_new_updates([update])
    return {"status": "ok"}
