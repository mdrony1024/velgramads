"use client";
import React, { useState, useEffect } from 'react';
import { LayoutGrid, PlusCircle, Settings, Share2, Activity } from 'lucide-react';

export default function Dashboard() {
  const [channels, setChannels] = useState([
    { id: 1, name: 'Free Promote Ostad', sub: '2.9k', status: 'Active' },
    { id: 2, name: 'Premium Store', sub: '1.5k', status: 'Paused' }
  ]);

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 p-5 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
          Ads Manager
        </h1>
        <div className="bg-white/10 p-2 rounded-full backdrop-blur-md border border-white/10">
          <Settings size={20} />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-white/5 border border-white/10 p-4 rounded-3xl backdrop-blur-xl">
          <Activity className="text-blue-400 mb-2" size={24} />
          <p className="text-xs text-slate-400">Total Reach</p>
          <h2 className="text-xl font-bold">12.5k</h2>
        </div>
        <div className="bg-white/5 border border-white/10 p-4 rounded-3xl backdrop-blur-xl">
          <Share2 className="text-emerald-400 mb-2" size={24} />
          <p className="text-xs text-slate-400">Total Posts</p>
          <h2 className="text-xl font-bold">48</h2>
        </div>
      </div>

      {/* Channel List Section */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <LayoutGrid size={18} /> Your Channels
        </h2>
        <button className="text-blue-400 text-sm flex items-center gap-1 font-medium">
          <PlusCircle size={16} /> Add New
        </button>
      </div>

      {/* Modern Channel Cards */}
      <div className="space-y-4">
        {channels.map((ch) => (
          <div key={ch.id} className="group relative bg-gradient-to-br from-white/10 to-white/5 border border-white/10 p-5 rounded-[2rem] overflow-hidden transition-all hover:border-blue-500/50">
            <div className="flex justify-between items-center relative z-10">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg font-bold text-xl">
                  {ch.name[0]}
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">{ch.name}</h3>
                  <p className="text-sm text-slate-400">{ch.sub} Subscribers</p>
                </div>
              </div>
              <div className={`px-4 py-1.5 rounded-full text-xs font-bold ${ch.status === 'Active' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-500/20 text-slate-400'}`}>
                {ch.status}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Floating Action Button */}
      <button className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-full shadow-2xl shadow-blue-500/40 flex items-center gap-2 font-bold transition-all active:scale-95">
        <PlusCircle size={20} /> Create Free Post
      </button>
    </div>
  );
}
