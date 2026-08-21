import React from 'react';
import { Mic, Zap, Cpu, ShieldCheck, Database, Settings } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onOpenSettings }) {
  const tabs = [
    { id: 'playground', label: 'Voice RAG', icon: Mic },
    { id: 'chunking', label: '5 Strategies', icon: Cpu },
    { id: 'latency', label: 'Latency Stats', icon: Zap },
    { id: 'guardrails', label: 'Guardrails', icon: ShieldCheck },
    { id: 'dataset', label: 'MS MARCO', icon: Database }
  ];

  return (
    <header className="border-b-4 border-[#00663c] bg-[#013720] sticky top-0 z-50 shadow-xl">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        
        {/* Top Header Bar */}
        <div className="flex items-center justify-between py-2 sm:py-2.5 gap-2">
          
          {/* Brand Logo & Hashtags */}
          <div className="flex items-center space-x-2 shrink-0">
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-[#ffde00] flex items-center justify-center text-[#024b2d] shadow-md border-2 border-[#e2c800] shrink-0">
              <Mic className="w-4 h-4 sm:w-4.5 sm:h-4.5 animate-pulse" />
            </div>

            <div className="flex items-center space-x-1.5">
              <h1 className="text-base sm:text-2xl font-black font-hh-serif tracking-tight text-[#ffde00] leading-none uppercase">
                IRIS
              </h1>
              <span className="text-[8px] sm:text-[10px] font-black tracking-widest text-[#ffde00] uppercase font-mono bg-[#024b2d] px-1.5 py-0.5 rounded border border-[#00663c]">
                HH GOA
              </span>
              <span className="hidden xs:inline-block px-1.5 py-0.5 text-[8px] sm:text-[9px] font-extrabold bg-[#ff007a] text-white rounded-full font-mono shadow-sm shrink-0">
                #IrisAI
              </span>
            </div>
          </div>

          {/* Desktop Navigation Tabs (MD+ Screens) */}
          <div className="hidden md:flex flex-1 justify-center min-w-0 px-2">
            <nav className="flex items-center gap-1 bg-[#024b2d] p-1 rounded-xl border border-[#00663c] shadow-inner">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-extrabold whitespace-nowrap transition-all cursor-pointer ${
                      isActive
                        ? 'bg-[#ffde00] text-[#024b2d] shadow-sm font-black scale-105'
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

          {/* Settings Action Button */}
          <div className="flex items-center shrink-0">
            <button
              onClick={onOpenSettings}
              className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 bg-[#ff007a] hover:bg-[#ff1a8c] text-white border-2 border-[#e6006e] rounded-xl text-xs font-extrabold transition shadow-md cursor-pointer whitespace-nowrap"
            >
              <Settings className="w-3.5 h-3.5 text-[#ffde00] shrink-0" />
              <span className="hidden sm:inline">Model &amp; STT Config</span>
              <span className="inline sm:hidden">Config</span>
            </button>
          </div>

        </div>

        {/* Mobile Horizontal Scrollable Tab Bar (Mobile `< md` Screens) */}
        <div className="md:hidden pb-2 pt-1 border-t border-[#00663c]/40">
          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 px-0.5">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-extrabold whitespace-nowrap transition-all shrink-0 cursor-pointer ${
                    isActive
                      ? 'bg-[#ffde00] text-[#024b2d] shadow-md border-2 border-[#e2c800] font-black'
                      : 'bg-[#024b2d] text-emerald-100 border border-[#00663c] hover:text-white'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5 shrink-0" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

      </div>
    </header>
  );
}
