import os
import telebot
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
import datetime

app = FastAPI()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.velgram_ads
users_col = db.users
campaigns_col = db.campaigns # প্রমোশন জমা রাখার জন্য
channels_col = db.channels   # অনুমোদিত চ্যানেলগুলোর জন্য

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Velgram Ads Pro</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    <style>
        body { background-color: #020617; font-family: sans-serif; color: #f8fafc; margin: 0; padding-bottom: 100px; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .tab-content { display: none; }
        .active-section { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        input { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 12px; width: 100%; color: white; outline: none; font-size: 14px; }
    </style>
</head>
<body>

    <!-- Header -->
    <div class="p-6 flex justify-between items-center sticky top-0 z-50 bg-[#020617]/90 backdrop-blur-xl">
        <div>
            <p class="text-[10px] text-slate-500 font-bold uppercase">Balance</p>
            <h2 class="text-3xl font-black text-blue-500 flex items-center gap-2">
                <i class='bx bxs-zap text-yellow-400'></i> <span id="balance">--</span>
            </h2>
        </div>
        <div class="w-10 h-10 rounded-full bg-blue-600/10 border border-blue-500/20 flex items-center justify-center">
            <i class='bx bxs-user-circle text-2xl text-blue-500'></i>
        </div>
    </div>

    <main class="px-5 pt-4">

        <!-- EARN TAB (Channel Management) -->
        <section id="earn" class="tab-content active-section space-y-4">
            <h3 class="font-bold text-xl italic">My Channels</h3>
            <div class="glass p-5 rounded-[2rem] space-y-3">
                <input type="text" id="new_channel_id" placeholder="@your_channel_id">
                <button onclick="addChannel()" class="w-full bg-emerald-600 py-3 rounded-xl font-bold text-sm">Add & Give Post Permission</button>
            </div>
            <div id="channel-list" class="space-y-3">
                <!-- Channels will load here -->
            </div>
        </section>

        <!-- PROMOTE TAB -->
        <section id="promote" class="tab-content space-y-4">
            <h3 class="font-bold text-xl italic">Promote Content</h3>
            <div class="glass p-6 rounded-[2.5rem] space-y-4 border-blue-500/20">
                <div>
                    <label class="text-[10px] font-bold text-slate-500 ml-2">TELEGRAM POST LINK</label>
                    <input type="text" id="post_link" placeholder="https://t.me/channel/123">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-[10px] font-bold text-slate-500 ml-2">BUDGET (PTS)</label>
                        <input type="number" id="budget" placeholder="Pts">
                    </div>
                    <div>
                        <label class="text-[10px] font-bold text-slate-500 ml-2">VIEWS TARGET</label>
                        <input type="number" id="views" placeholder="Target">
                    </div>
                </div>
                <button onclick="publishCampaign()" class="w-full bg-blue-600 py-4 rounded-2xl font-bold text-sm shadow-xl">Publish Promotion</button>
            </div>
        </section>

        <!-- STATS TAB -->
        <section id="stats" class="tab-content">
             <h3 class="font-bold text-xl italic mb-4">Live Campaigns</h3>
             <div id="campaign-list" class="space-y-3 font-bold text-xs text-slate-400">
                Loading campaigns...
             </div>
        </section>

    </main>

    <!-- Bottom Nav -->
    <nav class="fixed bottom-0 left-0 right-0 bg-[#020617]/95 backdrop-blur-3xl border-t border-white/5 flex justify-around p-5 z-50">
        <button onclick="switchTab('earn')" id="nav-earn" class="flex flex-col items-center gap-1 text-blue-500"><i class='bx bxs-megaphone text-xl'></i><span class="text-[9px] font-bold">Earn</span></button>
        <button onclick="switchTab('promote')" id="nav-promote" class="flex flex-col items-center gap-1 text-slate-500"><i class='bx bxs-rocket text-xl'></i><span class="text-[9px] font-bold">Promote</span></button>
        <button onclick="switchTab('stats')" id="nav-stats" class="flex flex-col items-center gap-1 text-slate-500"><i class='bx bxs-bar-chart-alt-2 text-xl'></i><span class="text-[9px] font-bold">Stats</span></button>
    </nav>

    <script>
        const tg = window.Telegram.WebApp;
        const userId = tg.initDataUnsafe?.user?.id || 'test_user';

        async function loadData() {
            const res = await fetch(`/api/user/${userId}`);
            const data = await res.json();
            document.getElementById('balance').innerText = data.points;
        }

        async function publishCampaign() {
            const link = document.getElementById('post_link').value;
            const budget = document.getElementById('budget').value;
            const views = document.getElementById('views').value;

            if(!link || !budget || !views) return alert("Fill all fields!");

            const res = await fetch('/api/promote', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({userId, link, budget: parseInt(budget), views: parseInt(views)})
            });
            const result = await res.json();
            if(result.success) {
                alert("Promotion Live!");
                loadData();
            } else {
                alert(result.error);
            }
        }

        async function addChannel() {
            const channelId = document.getElementById('new_channel_id').value;
            if(!channelId) return alert("Enter channel username!");
            const res = await fetch('/api/add-channel', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({userId, channelId})
            });
            const data = await res.json();
            alert(data.message);
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active-section'));
            document.querySelectorAll('nav button').forEach(b => b.classList.replace('text-blue-500', 'text-slate-500'));
            document.getElementById(tabId).classList.add('active-section');
            document.getElementById('nav-'+tabId).classList.replace('text-slate-500', 'text-blue-500');
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

@app.post("/api/promote")
async def promote(request: Request):
    data = await request.json()
    user = users_col.find_one({"user_id": data['userId']})
    
    if user['points'] < data['budget']:
        return {"success": False, "error": "Insufficient points!"}
    
    # বাজেট কাটা
    users_col.update_one({"user_id": data['userId']}, {"$inc": {"points": -data['budget']}})
    
    # ক্যাম্পেইন সেভ করা
    campaigns_col.insert_one({
        "creator": data['userId'],
        "link": data['link'],
        "budget": data['budget'],
        "target_views": data['views'],
        "current_views": 0,
        "status": "active"
    })
    
    # এখানে লজিক শুরু হবে অন্য চ্যানেলে পোস্ট করার
    distribute_ads() 
    
    return {"success": True}

@app.post("/api/add-channel")
async def add_channel(request: Request):
    data = await request.json()
    try:
        # বট চেক করবে সে এডমিন কি না
        member = bot.get_chat_member(data['channelId'], bot.get_me().id)
        if member.status in ['administrator', 'creator']:
            channels_col.update_one(
                {"channelId": data['channelId']},
                {"$set": {"owner": data['userId'], "status": "active"}},
                upsert=True
            )
            return {"message": "Channel Added Successfully!"}
        else:
            return {"message": "Make bot Admin first!"}
    except:
        return {"message": "Invalid Channel or Bot is not Admin!"}

def distribute_ads():
    # এটি রিয়েল টাইমে একটি এড নিয়ে অন্য একটি চ্যানেলে পোস্ট করবে
    campaign = campaigns_col.find_one({"status": "active"})
    channel = channels_col.find_one({"status": "active"})
    
    if campaign and channel:
        try:
            # লিঙ্ক থেকে চ্যাট আইডি এবং মেসেজ আইডি বের করা
            # https://t.me/channel/123 -> channel, 123
            parts = campaign['link'].split('/')
            chat_username = parts[-2]
            msg_id = int(parts[-1])
            
            # পোস্ট কপি করে অন্য চ্যানেলে পাঠানো
            bot.copy_message(channel['channelId'], f"@{chat_username}", msg_id)
            
            # ক্যাম্পেইন আপডেট
            campaigns_col.update_one({"_id": campaign["_id"]}, {"$inc": {"current_views": 1}})
            
            # চ্যানেল মালিককে পয়েন্ট পুরস্কার দেওয়া (যেমন ৫ পয়েন্ট)
            users_col.update_one({"user_id": channel['owner']}, {"$inc": {"points": 5}})
            
        except Exception as e:
            print(f"Post failed: {e}")

@app.post("/api/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    update = telebot.types.Update.de_json(payload)
    bot.process_new_updates([update])
    return {"status": "ok"}
