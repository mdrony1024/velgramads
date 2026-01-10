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
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { background-color: #020617; font-family: 'Poppins', sans-serif; color: #f8fafc; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .nav-active { color: #3b82f6; }
        .tab-content { display: none; animation: fadeIn 0.3s ease; }
        .active-section { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .point-box { background: linear-gradient(135deg, #1e40af, #7e22ce); }
    </style>
</head>
<body class="pb-24">

    <!-- Header & Points -->
    <div class="p-6 flex justify-between items-center sticky top-0 z-50 bg-[#020617]/80 backdrop-blur-md">
        <div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Balance</p>
            <h2 class="text-2xl font-black text-blue-500 flex items-center gap-1">
                <i class='bx bxs-zap text-yellow-400'></i> <span id="user-points">--</span>
            </h2>
        </div>
        <div class="w-10 h-10 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center">
            <i class='bx bxs-user-circle text-2xl text-slate-400'></i>
        </div>
    </div>

    <!-- Main Content Sections -->
    <main class="px-5">

        <!-- EARN TAB -->
        <section id="earn" class="tab-content active-section space-y-6">
            <div class="flex justify-between items-center">
                <h3 class="font-bold text-lg italic">My Channels</h3>
                <button class="bg-blue-600/20 text-blue-400 text-[10px] px-3 py-1.5 rounded-full font-bold border border-blue-500/30">+ Add Channel</button>
            </div>
            
            <div class="glass p-5 rounded-[2.5rem] flex items-center justify-between border-emerald-500/20">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-slate-800 rounded-2xl flex items-center justify-center font-bold text-blue-500">F</div>
                    <div>
                        <h4 class="font-bold text-sm">Free Promote Ostad</h4>
                        <p class="text-[10px] text-emerald-400 font-bold tracking-tighter">● Bot is Active</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-xs font-bold text-slate-400">+50 pts</p>
                </div>
            </div>
        </section>

        <!-- PROMOTE TAB -->
        <section id="promote" class="tab-content space-y-5">
            <h3 class="font-bold text-lg">Promote Your Content</h3>
            <div class="glass p-6 rounded-[2.5rem] space-y-4">
                <div>
                    <label class="text-[10px] font-bold text-slate-500 uppercase ml-2">Post Link</label>
                    <input type="text" placeholder="https://t.me/channel/123" class="w-full bg-white/5 border border-white/10 p-4 rounded-2xl outline-none text-sm focus:border-blue-500">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-[10px] font-bold text-slate-500 uppercase ml-2">Total Budget</label>
                        <input type="number" placeholder="Pts" class="w-full bg-white/5 border border-white/10 p-4 rounded-2xl outline-none text-sm">
                    </div>
                    <div>
                        <label class="text-[10px] font-bold text-slate-500 uppercase ml-2">Views</label>
                        <input type="number" placeholder="Target" class="w-full bg-white/5 border border-white/10 p-4 rounded-2xl outline-none text-sm">
                    </div>
                </div>
                <button class="w-full bg-blue-600 py-4 rounded-2xl font-bold text-sm shadow-xl shadow-blue-600/20">Publish Promotion</button>
            </div>
        </section>

        <!-- STATS TAB -->
        <section id="stats" class="tab-content">
            <h3 class="font-bold text-lg mb-4">Ad Statistics</h3>
            <div class="grid grid-cols-2 gap-4">
                <div class="glass p-5 rounded-[2rem]">
                    <p class="text-[10px] text-slate-500 font-bold uppercase">Ads Run</p>
                    <h2 class="text-2xl font-bold">12</h2>
                </div>
                <div class="glass p-5 rounded-[2rem]">
                    <p class="text-[10px] text-slate-500 font-bold uppercase">Earned</p>
                    <h2 class="text-2xl font-bold">4.2k</h2>
                </div>
            </div>
        </section>

    </main>

    <!-- Bottom Navigation -->
    <nav class="fixed bottom-0 left-0 right-0 bg-[#020617]/90 backdrop-blur-2xl border-t border-white/5 flex justify-around p-4 z-50">
        <button onclick="switchTab('earn')" id="nav-earn" class="flex flex-col items-center gap-1 nav-active">
            <i class='bx bxs-megaphone text-xl'></i><span class="text-[9px] font-bold">Earn</span>
        </button>
        <button onclick="switchTab('promote')" id="nav-promote" class="flex flex-col items-center gap-1 text-slate-500">
            <i class='bx bxs-rocket text-xl'></i><span class="text-[9px] font-bold">Promote</span>
        </button>
        <button onclick="switchTab('stats')" id="nav-stats" class="flex flex-col items-center gap-1 text-slate-500">
            <i class='bx bxs-bar-chart-alt-2 text-xl'></i><span class="text-[9px] font-bold">Stats</span>
        </button>
        <button onclick="switchTab('profile')" id="nav-profile" class="flex flex-col items-center gap-1 text-slate-500">
            <i class='bx bxs-wallet text-xl'></i><span class="text-[9px] font-bold">Wallet</span>
        </button>
    </nav>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        const userId = tg.initDataUnsafe?.user?.id || 'test_user';

        // ডাটাবেস থেকে রিয়েল পয়েন্ট আনা
        async function loadData() {
            try {
                const res = await fetch(`/api/user/${userId}`);
                const data = await res.json();
                document.getElementById('user-points').innerText = data.points;
            } catch (e) {
                document.getElementById('user-points').innerText = "Err";
            }
        }

        // ট্যাব সুইচিং লজিক
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active-section'));
            document.querySelectorAll('nav button').forEach(b => b.classList.replace('nav-active', 'text-slate-500'));
            
            const target = document.getElementById(tabId);
            if(target) target.classList.add('active-section');
            document.getElementById(`nav-${tabId}`).classList.replace('text-slate-500', 'nav-active');
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
    user = db.users.find_one({"user_id": user_id})
    if not user:
        # নতুন ইউজারের জন্য পয়েন্ট ১০০ সেট করা (ডাটাবেসে সেভ হবে)
        user = {"user_id": user_id, "points": 100}
        db.users.insert_one(user)
    user["_id"] = str(user["_id"])
    return user

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
    markup.add(telebot.types.InlineKeyboardButton("Open Ads Manager 🚀", web_app=web_app))
    bot.send_message(message.chat.id, "স্বাগতম! আপনার এডস ও পয়েন্ট ম্যানেজ করতে নিচের বাটন ক্লিক করুন।", reply_markup=markup)
