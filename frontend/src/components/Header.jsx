import React from 'react';
import { Mic, Zap, Cpu, ShieldCheck, Database, Settings, Sun, Palmtree } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onOpenSettings }) {
  return (
    <header className="border-b-2 border-[#00663c] bg-[#013720] sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-22 py-3">
          
          {/* Brand Logo - Styled matching Hacker House Goa website serif headline */}
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-[#ffde00] flex items-center justify-center text-[#024b2d] shadow-md border border-[#e2c800]">
              <Mic className="w-6 h-6 animate-pulse" />
            </div>

            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-black font-hh-serif tracking-tight text-[#ffde00] uppercase">
                  Hacker House <span className="text-[#ff007a] italic">Goa</span>
                </h1>
                <span className="px-2.5 py-0.5 text-xs font-extrabold bg-[#ff007a] text-white rounded-full font-mono shadow-sm">
                  #RAGInGoa
                </span>
              </div>
              <p className="text-xs text-[#a3c4b0] font-mono flex items-center gap-1.5 mt-0.5">
                <span>Task 2: Voice RAG Pipeline</span>
                <span className="text-[#ffde00]">🌴</span>
                <span className="text-emerald-300 font-bold">&lt; 200ms Latency</span>
              </p>
            </div>
          </div>

          {/* Navigation Bar */}
          <nav className="hidden md:flex space-x-1.5 bg-[#024b2d] p-1.5 rounded-xl border border-[#00663c]">
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
                  className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-[#ffde00] text-[#024b2d] shadow-sm font-extrabold'
                      : 'text-emerald-100 hover:text-white hover:bg-[#013720]'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Settings Button */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onOpenSettings}
              className="flex items-center space-x-1.5 px-3.5 py-2 bg-[#ff007a] hover:bg-[#ff1a8c] text-white border border-[#e6006e] rounded-xl text-xs font-bold transition shadow-sm"
            >
              <Settings className="w-3.5 h-3.5 text-[#ffde00]" />
              <span>Model & STT Config</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
