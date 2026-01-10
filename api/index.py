import os
import telebot
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
import random

app = FastAPI()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.velgram_ads
users_col = db.users
channels_col = db.channels
campaigns_col = db.campaigns

# Telegram Bot Setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Velgram Ads Exchange</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    <style>
        body { background-color: #020617; font-family: sans-serif; color: #f8fafc; padding-bottom: 100px; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px; }
        .tab-content { display: none; animation: fadeIn 0.3s ease; }
        .active-section { display: block; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .nav-active { color: #3b82f6; }
    </style>
</head>
<body>

    <!-- Top Points Header -->
    <div class="p-6 flex justify-between items-center sticky top-0 z-50 bg-[#020617]/90 backdrop-blur-md border-b border-white/5">
        <div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Your Points</p>
            <h2 class="text-3xl font-black text-blue-500 flex items-center gap-2">
                <i class='bx bxs-zap text-yellow-400'></i> <span id="balance">--</span>
            </h2>
        </div>
        <div class="w-10 h-10 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center">
            <i class='bx bxs-user text-xl text-slate-400'></i>
        </div>
    </div>

    <main class="p-5">
        <!-- EARN TAB: Add Channel -->
        <section id="earn" class="tab-content active-section space-y-5">
            <h3 class="font-bold text-lg italic">Host Ads & Earn</h3>
            <div class="glass p-5 space-y-4 border-emerald-500/20">
                <p class="text-xs text-slate-400">Add your channel and give bot admin permission. Earn 10 points for every ad hosted.</p>
                <input type="text" id="channel_id" placeholder="@ChannelUsername" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl outline-none text-sm text-white">
                <button onclick="addChannel()" class="w-full bg-emerald-600 py-3 rounded-xl font-bold text-sm">Add Channel & Start Earning</button>
            </div>
            <div id="my-channels" class="space-y-3">
                <!-- Channels list here -->
            </div>
        </section>

        <!-- PROMOTE TAB: Exchange Post -->
        <section id="promote" class="tab-content space-y-5">
            <h3 class="font-bold text-lg italic text-blue-400">Promote Your Post</h3>
            <div class="glass p-6 space-y-4 border-blue-500/20">
                <input type="text" id="post_link" placeholder="https://t.me/channel/123" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm">
                <div class="grid grid-cols-2 gap-3">
                    <input type="number" id="budget" placeholder="Budget (Pts)" class="bg-white/5 border border-white/10 p-3 rounded-xl text-sm text-white">
                    <input type="number" id="views" placeholder="Target Views" class="bg-white/5 border border-white/10 p-3 rounded-xl text-sm text-white">
                </div>
                <button onclick="promotePost()" class="w-full bg-blue-600 py-4 rounded-xl font-bold text-sm shadow-lg">Exchange Post Now</button>
            </div>
        </section>
    </main>

    <!-- Navigation -->
    <nav class="fixed bottom-0 left-0 right-0 bg-[#020617]/95 backdrop-blur-3xl border-t border-white/5 flex justify-around p-5 z-50">
        <button onclick="switchTab('earn')" id="nav-earn" class="flex flex-col items-center gap-1 nav-active">
            <i class='bx bxs-megaphone text-2xl'></i><span class="text-[9px] font-bold">Earn</span>
        </button>
        <button onclick="switchTab('promote')" id="nav-promote" class="flex flex-col items-center gap-1 text-slate-500">
            <i class='bx bxs-rocket text-2xl'></i><span class="text-[9px] font-bold">Promote</span>
        </button>
    </nav>

    <script>
        const tg = window.Telegram.WebApp;
        const userId = tg.initDataUnsafe?.user?.id || 'test_user';

        async function loadData() {
            const res = await fetch(`/api/user/${userId}`);
            const data = await res.json();
            document.getElementById('balance').innerText = data.points;
        }

        async function addChannel() {
            const channelId = document.getElementById('channel_id').value;
            const res = await fetch('/api/add-channel', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({userId, channelId})
            });
            const data = await res.json();
            alert(data.message);
        }

        async function promotePost() {
            const link = document.getElementById('post_link').value;
            const budget = document.getElementById('budget').value;
            const views = document.getElementById('views').value;
            const res = await fetch('/api/promote', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({userId, link, budget, views})
            });
            const data = await res.json();
            alert(data.message);
            loadData();
        }

        function switchTab(id) {
            document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active-section'));
            document.querySelectorAll('nav button').forEach(b => b.classList.replace('nav-active', 'text-slate-500'));
            document.getElementById(id).classList.add('active-section');
            document.getElementById('nav-'+id).classList.replace('text-slate-500', 'nav-active');
        }

        tg.ready();
        loadData();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    user = users_col.find_one({"user_id": user_id})
    if not user:
        user = {"user_id": user_id, "points": 100}
        users_col.insert_one(user)
    user["_id"] = str(user["_id"])
    return user

@app.post("/api/add-channel")
async def add_channel(request: Request):
    data = await request.json()
    try:
        # বট চেক করবে সে এডমিন কি না
        member = bot.get_chat_member(data['channelId'], bot.get_me().id)
        if member.status in ['administrator', 'creator']:
            channels_col.update_one(
                {"channel_id": data['channelId']},
                {"$set": {"owner": data['userId'], "status": "active"}},
                upsert=True
            )
            return {"message": "Channel Added! Now bot will post ads here to give you points."}
        else:
            return {"message": "Error: Make bot admin in your channel first!"}
    except:
        return {"message": "Invalid Channel or Bot is not Admin!"}

@app.post("/api/promote")
async def promote(request: Request):
    data = await request.json()
    user = users_col.find_one({"user_id": data['userId']})
    budget = int(data['budget'])
    
    if user['points'] < budget:
        return {"message": "Error: Insufficient Points!"}
    
    # বাজেট কাটা
    users_col.update_one({"user_id": data['userId']}, {"$inc": {"points": -budget}})
    
    # ক্যাম্পেইন সেভ
    campaigns_col.insert_one({
        "owner": data['userId'],
        "link": data['link'],
        "budget": budget,
        "views": int(data['views']),
        "done": 0
    })
    
    # অটো এক্সচেঞ্জ লজিক শুরু
    trigger_exchange()
    return {"message": "Success! Your post is now being shared in our network."}

def trigger_exchange():
    # এটি র্যান্ডম একটি পোস্ট নিয়ে অন্য ইউজারের চ্যানেলে দিবে (Forward ছাড়া)
    campaign = campaigns_col.find_one({"budget": {"$gt": 0}})
    target_channel = channels_col.find_one({"status": "active"})
    
    if campaign and target_channel:
        try:
            # লিঙ্ক থেকে পোস্ট আইডি নেওয়া
            parts = campaign['link'].split('/')
            chat_user = f"@{parts[-2]}"
            msg_id = int(parts[-1])
            
            # আসল ম্যাজিক: Copy Message (No Forward Tag)
            bot.copy_message(target_channel['channel_id'], chat_user, msg_id)
            
            # পয়েন্ট ডিস্ট্রিবিউশন
            campaigns_col.update_one({"_id": campaign["_id"]}, {"$inc": {"budget": -10, "done": 1}})
            users_col.update_one({"user_id": target_channel['owner']}, {"$inc": {"points": 10}})
        except:
            pass

@app.post("/api/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    update = telebot.types.Update.de_json(payload)
    bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url="https://velgramads.vercel.app/")
    markup.add(telebot.types.InlineKeyboardButton("Open Ad Exchange ✨", web_app=web_app))
    bot.send_message(message.chat.id, "Welcome to Velgram Ad Exchange! Add your channel to earn or promote your posts for free.", reply_markup=markup)
