import React from 'react';
import { Mic, Zap, Cpu, ShieldCheck, Database, Settings } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onOpenSettings }) {
  return (
    <header className="border-b-4 border-[#00663c] bg-[#013720] sticky top-0 z-50 shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center justify-between py-4 gap-4">
          
          {/* Brand Logo & Hashtag */}
          <div className="flex items-center space-x-3 shrink-0">
            <div className="w-12 h-12 rounded-2xl bg-[#ffde00] flex items-center justify-center text-[#024b2d] shadow-lg border-2 border-[#e2c800] shrink-0">
              <Mic className="w-6 h-6 animate-pulse" />
            </div>

            <div className="flex flex-col">
              <div className="flex items-center space-x-2">
                <span className="text-[11px] font-black tracking-widest text-[#ffde00] uppercase font-mono bg-[#024b2d] px-2 py-0.5 rounded border border-[#00663c] shadow-inner">
                  HH GOA
                </span>
                <span className="px-2 py-0.5 text-[10px] font-extrabold bg-[#ff007a] text-white rounded-full font-mono shadow-sm shrink-0">
                  #IrisAI
                </span>
              </div>

              <h1 className="text-2xl sm:text-3xl font-black font-hh-serif tracking-tight text-[#ffde00] leading-none uppercase mt-1">
                IRIS
              </h1>

              <p className="text-xs text-[#a3c4b0] font-mono flex items-center gap-2 mt-1">
                <span>Voice RAG Intelligence Engine</span>
                <span className="text-[#ffde00]">⚡</span>
                <span className="text-emerald-300 font-extrabold">&lt; 200ms Latency</span>
              </p>
            </div>
          </div>

          {/* Navigation Bar - Responsive Wrap */}
          <nav className="flex flex-wrap items-center justify-center gap-2 bg-[#024b2d] p-2 rounded-2xl border-2 border-[#00663c]">
            {[
              { id: 'playground', label: 'Voice RAG', icon: Mic },
              { id: 'chunking', label: '5 Chunking Strategies', icon: Cpu },
              { id: 'latency', label: 'P50/P70/P100 Analytics', icon: Zap },
              { id: 'guardrails', label: 'Guardrails & Harness', icon: ShieldCheck },
              { id: 'dataset', label: 'MSMARCO Data', icon: Database }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[#ffde00] text-[#024b2d] shadow-md font-black'
                      : 'text-emerald-100 hover:text-white hover:bg-[#013720]'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Settings Action Button */}
          <div className="flex items-center shrink-0">
            <button
              onClick={onOpenSettings}
              className="flex items-center space-x-2 px-4 py-2.5 bg-[#ff007a] hover:bg-[#ff1a8c] text-white border-2 border-[#e6006e] rounded-xl text-xs font-extrabold transition shadow-md cursor-pointer"
            >
              <Settings className="w-4 h-4 text-[#ffde00]" />
              <span>Model &amp; STT Config</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
