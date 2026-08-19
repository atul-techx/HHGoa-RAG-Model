import React from 'react';
import { Mic, Zap, Cpu, ShieldCheck, Database, Settings, Flame } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onOpenSettings }) {
  return (
    <header className="border-b border-pink-500/20 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Brand Logo & Hashtag */}
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-pink-500 via-amber-500 to-cyan-400 p-0.5 shadow-lg shadow-pink-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Mic className="w-6 h-6 text-pink-500 animate-pulse" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-extrabold tracking-tight gradient-text-goa">
                  Voice RAG Engine
                </h1>
                <span className="px-2 py-0.5 text-xs font-bold bg-pink-500/20 text-pink-400 border border-pink-500/40 rounded-full font-mono">
                  #RAGInGoa
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono flex items-center gap-1">
                HH Goa 2026 Shortlist Task 2 <span className="text-cyan-400">|</span> Target &lt; 200ms
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <nav className="hidden md:flex space-x-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab('playground')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === 'playground'
                  ? 'bg-gradient-to-r from-pink-600 to-amber-500 text-white shadow-md shadow-pink-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Mic className="w-4 h-4" />
              <span>Voice RAG</span>
            </button>

            <button
              onClick={() => setActiveTab('chunking')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === 'chunking'
                  ? 'bg-gradient-to-r from-pink-600 to-amber-500 text-white shadow-md shadow-pink-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Cpu className="w-4 h-4" />
              <span>5 Chunking Strategies</span>
            </button>

            <button
              onClick={() => setActiveTab('latency')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === 'latency'
                  ? 'bg-gradient-to-r from-pink-600 to-amber-500 text-white shadow-md shadow-pink-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Zap className="w-4 h-4" />
              <span>P50/P70/P100 Analytics</span>
            </button>

            <button
              onClick={() => setActiveTab('guardrails')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === 'guardrails'
                  ? 'bg-gradient-to-r from-pink-600 to-amber-500 text-white shadow-md shadow-pink-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Guardrails & Harness</span>
            </button>

            <button
              onClick={() => setActiveTab('dataset')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === 'dataset'
                  ? 'bg-gradient-to-r from-pink-600 to-amber-500 text-white shadow-md shadow-pink-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Database className="w-4 h-4" />
              <span>MSMARCO Data</span>
            </button>
          </nav>

          {/* Right Action Controls */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onOpenSettings}
              className="flex items-center space-x-2 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 rounded-xl text-xs font-semibold transition"
            >
              <Settings className="w-4 h-4 text-cyan-400" />
              <span>Model & API Config</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
