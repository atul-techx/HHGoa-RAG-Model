import React from 'react';
import { Mic, Zap, Cpu, ShieldCheck, Database, Settings } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onOpenSettings }) {
  return (
    <header className="border-b-4 border-[#00663c] bg-[#013720] sticky top-0 z-50 shadow-xl">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex flex-row items-center justify-between py-2.5 gap-2">
          
          {/* Brand Logo & Hashtag */}
          <div className="flex items-center space-x-2 shrink-0">
            <div className="w-9 h-9 rounded-xl bg-[#ffde00] flex items-center justify-center text-[#024b2d] shadow-md border-2 border-[#e2c800] shrink-0">
              <Mic className="w-4.5 h-4.5 animate-pulse" />
            </div>

            <div className="flex items-center space-x-1.5">
              <h1 className="text-xl sm:text-2xl font-black font-hh-serif tracking-tight text-[#ffde00] leading-none uppercase">
                IRIS
              </h1>
              <span className="text-[10px] font-black tracking-widest text-[#ffde00] uppercase font-mono bg-[#024b2d] px-1.5 py-0.5 rounded border border-[#00663c]">
                HH GOA
              </span>
              <span className="px-1.5 py-0.5 text-[9px] font-extrabold bg-[#ff007a] text-white rounded-full font-mono shadow-sm shrink-0">
                #IrisAI
              </span>
            </div>
          </div>

          {/* Navigation Bar - Compact Horizontal Tabs */}
          <div className="flex-1 flex justify-center min-w-0 px-1">
            <nav className="flex items-center gap-0.5 sm:gap-1 bg-[#024b2d] p-1 rounded-xl border border-[#00663c] shadow-inner">
              {[
                { id: 'playground', label: 'Voice RAG', icon: Mic },
                { id: 'chunking', label: '5 Strategies', icon: Cpu },
                { id: 'latency', label: 'Latency Stats', icon: Zap },
                { id: 'guardrails', label: 'Guardrails', icon: ShieldCheck },
                { id: 'dataset', label: 'MS MARCO', icon: Database }
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[11px] font-extrabold whitespace-nowrap transition-all cursor-pointer ${
                      isActive
                        ? 'bg-[#ffde00] text-[#024b2d] shadow-sm font-black'
                        : 'text-emerald-100 hover:text-white hover:bg-[#013720]'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5 shrink-0" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Settings Action Button - Scaled & Padding Adjusted */}
          <div className="flex items-center shrink-0">
            <button
              onClick={onOpenSettings}
              className="flex items-center space-x-1.5 px-2.5 py-1.5 bg-[#ff007a] hover:bg-[#ff1a8c] text-white border-2 border-[#e6006e] rounded-xl text-xs font-extrabold transition shadow-md cursor-pointer whitespace-nowrap"
            >
              <Settings className="w-3.5 h-3.5 text-[#ffde00] shrink-0" />
              <span>Model &amp; STT Config</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
