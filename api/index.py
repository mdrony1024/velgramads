import os
import telebot
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from pathlib import Path

app = FastAPI()

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "1234") # Vercel Env থেকে সেট করবেন

# Database & Bot Setup
client = MongoClient(MONGO_URI)
db = client.velgram_ads
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 🛑 রুটস (ইউজার বনাম অ্যাডমিন)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def user_page():
    """ইউজারদের জন্য মেইন ইন্টারফেস"""
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin.html", response_class=HTMLResponse)
async def admin_page():
    """আপনার জন্য আলাদা অ্যাডমিন ইন্টারফেস"""
    with open(os.path.join(BASE_DIR, "admin.html"), "r", encoding="utf-8") as f:
        return f.read()

# ==========================================
# 👤 ইউজার এপিআই (User APIs)
# ==========================================

@app.get("/api/user/{uid}")
async def get_user(uid: str):
    user = db.users.find_one({"user_id": str(uid)})
    if not user:
        user = {"user_id": str(uid), "points": 100}
        db.users.insert_one(user)
    return {"points": user.get('points', 0)}

@app.post("/api/add-channel")
async def add_channel(request: Request):
    data = await request.json()
    try:
        chat = bot.get_chat(data['channelId'])
        member = bot.get_chat_member(chat.id, bot.get_me().id)
        if member.status in ['administrator', 'creator']:
            db.channels.update_one(
                {"channel_id": data['channelId']},
                {"$set": {"owner": str(data['userId']), "chat_id": chat.id, "status": "active"}},
                upsert=True
            )
            return {"message": "চ্যানেল সফলভাবে যুক্ত হয়েছে!"}
        return {"message": "বটকে আপনার চ্যানেলে অ্যাডমিন করুন!"}
    except:
        return {"message": "ভুল ইউজারনেম অথবা বট অ্যাডমিন নয়!"}

@app.post("/api/promote")
async def promote(request: Request):
    data = await request.json()
    uid = str(data['userId'])
    budget = int(data['budget'])
    user = db.users.find_one({"user_id": uid})
    
    if not user or user['points'] < budget:
        return {"message": "পর্যাপ্ত পয়েন্ট নেই!"}
    
    db.users.update_one({"user_id": uid}, {"$inc": {"points": -budget}})
    db.campaigns.insert_one({
        "owner": uid,
        "link": data['link'],
        "budget": budget,
        "done": 0
    })
    trigger_exchange() # অটো প্রমোশন শুরু
    return {"message": "আপনার পোস্ট প্রমোশন লাইভ হয়েছে!"}

# ==========================================
# 👑 অ্যাডমিন এপিআই (Admin APIs)
# ==========================================

@app.get("/api/admin/stats")
async def admin_stats(pw: str):
    if pw != ADMIN_PASS: raise HTTPException(status_code=401)
    return {
        "users": db.users.count_documents({}),
        "channels": db.channels.count_documents({"status": "active"}),
        "ads": db.campaigns.count_documents({"budget": {"$gt": 0}})
    }

@app.post("/api/admin/broadcast")
async def admin_broadcast(request: Request):
    data = await request.json()
    if data.get("pass") != ADMIN_PASS: return {"status": "error"}
    
    users = db.users.find()
    count = 0
    for u in users:
        try:
            bot.send_message(u['user_id'], data['msg'])
            count += 1
        except: pass
    return {"message": f"সফলভাবে {count} জন ইউজারকে পাঠানো হয়েছে।"}

# ==========================================
# ⚙️ সিস্টেম লজিক (Exchange Engine)
# ==========================================

def trigger_exchange():
    campaign = db.campaigns.find_one({"budget": {"$gte": 10}})
    target = db.channels.find_one({"status": "active", "owner": {"$ne": campaign['owner'] if campaign else ""}})
    
    if campaign and target:
        try:
            parts = campaign['link'].replace("https://t.me/", "").split('/')
            source_chat = f"@{parts[0]}"
            msg_id = int(parts[1])
            bot.copy_message(target['chat_id'], source_chat, msg_id)
            db.campaigns.update_one({"_id": campaign["_id"]}, {"$inc": {"budget": -10, "done": 1}})
            db.users.update_one({"user_id": target['owner']}, {"$inc": {"points": 8}})
        except: pass

@app.post("/api/webhook")
async def handle_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if not db.users.find_one({"user_id": uid}):
        db.users.insert_one({"user_id": uid, "points": 100})
    
    markup = telebot.types.InlineKeyboardMarkup()
    url = f"https://{os.getenv('VERCEL_URL')}/"
    markup.add(telebot.types.InlineKeyboardButton("অ্যাপ ওপেন করুন ✨", web_app=telebot.types.WebAppInfo(url=url)))
    bot.send_message(message.chat.id, "Velgram Ads-এ আপনাকে স্বাগতম!", reply_markup=markup)
