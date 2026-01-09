import os
import telebot
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pymongo import MongoClient

app = FastAPI()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.velgram_ads

# Telegram Bot Setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# আপনার মডার্ন ডিজাইনের HTML স্ট্রিং
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Velgram Ads Pro</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    <style>
        body { background-color: #0f172a; font-family: 'Poppins', sans-serif; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="text-white">
    <div class="p-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-b-[35px] shadow-lg text-center">
        <h1 class="text-2xl font-bold italic">VELGRAM ADS PRO</h1>
        <p class="text-[10px] opacity-80 uppercase tracking-widest mt-1">Point Based Ad Network</p>
    </div>

    <div class="p-5">
        <div class="glass p-8 rounded-[2.5rem] text-center mt-5 border-blue-500/20">
            <p class="text-xs text-slate-400 uppercase font-bold tracking-widest">My Balance</p>
            <h2 id="display-points" class="text-5xl font-black text-blue-500 mt-2">--</h2>
            <p class="text-[10px] text-slate-500 mt-2 italic">Start earning by adding channels</p>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-8">
            <div onclick="alert('Earn system is coming soon!')" class="glass p-6 rounded-3xl flex flex-col items-center gap-2 cursor-pointer active:scale-95 transition-all">
                <i class='bx bxs-megaphone text-3xl text-emerald-400'></i>
                <span class="text-[10px] font-bold uppercase">Earn Pts</span>
            </div>
            <div onclick="alert('Promote system is coming soon!')" class="glass p-6 rounded-3xl flex flex-col items-center gap-2 cursor-pointer active:scale-95 transition-all">
                <i class='bx bxs-rocket text-3xl text-blue-400'></i>
                <span class="text-[10px] font-bold uppercase">Promote</span>
            </div>
        </div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        const userId = tg.initDataUnsafe?.user?.id || 'test_user';

        async function fetchUserData() {
            try {
                // আমরা এই পাইথন ফাইলেরই এপিআই ব্যবহার করছি
                const res = await fetch(`/api/user/${userId}`);
                const data = await res.json();
                document.getElementById('display-points').innerText = data.points;
            } catch (e) {
                document.getElementById('display-points').innerText = "100";
            }
        }

        tg.ready();
        fetchUserData();
    </script>
</body>
</html>
"""

# ১. মেইন হোমপেজ রাউট (সরাসরি HTML রিটার্ন করবে)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

# ২. মিনি অ্যাপের জন্য ডাটা এপিআই
@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        user = {"user_id": user_id, "points": 100}
        db.users.insert_one(user)
    user["_id"] = str(user["_id"])
    return user

# ৩. টেলিগ্রাম বটের ওয়েবহুক রাউট
@app.post("/api/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    update = telebot.types.Update.de_json(payload)
    bot.process_new_updates([update])
    return {"status": "ok"}

# ৪. বটের লজিক
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url="https://velgramads.vercel.app/")
    markup.add(telebot.types.InlineKeyboardButton("Open Ads Manager 🚀", web_app=web_app))
    bot.send_message(message.chat.id, f"স্বাগতম {message.from_user.first_name}!\nআপনার এডস ও পয়েন্ট ম্যানেজ করতে নিচের বাটন ক্লিক করুন।", reply_markup=markup)
