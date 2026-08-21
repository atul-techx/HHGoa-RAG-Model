import React from 'react';
import { Sparkles, Mic, Github, ExternalLink, Zap, ShieldCheck, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="relative bg-[#012515] text-white pt-14 pb-8 overflow-hidden border-t-4 border-[#00663c] mt-auto">
      {/* Background Subtle Gradient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-64 bg-gradient-to-b from-[#ffde00]/5 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 pb-12 border-b border-[#00663c]/60">
          
          {/* Main Headline & Description Column */}
          <div className="md:col-span-5 flex flex-col justify-between">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#024b2d] border border-[#00663c] rounded-full text-xs font-mono font-extrabold text-[#ffde00] mb-4 shadow-sm">
                <Sparkles className="w-3.5 h-3.5 text-[#ff007a]" />
                <span>HH GOA 2026 OFFICIAL ENTRY</span>
              </div>
              
              <h2 className="text-3xl sm:text-4xl font-black font-hh-serif tracking-tight text-white leading-tight">
                Your Next Move Starts Here.
              </h2>
              
              <p className="mt-3 text-xs sm:text-sm text-[#a3c4b0] font-sans leading-relaxed max-w-md">
                Sub-200ms Voice Retrieval Augmented Generation Engine with multi-strategy chunking, 100% grounded extractive neural QA, and real-time model harness guardrails.
              </p>
            </div>

            <div className="mt-6 flex items-center space-x-3">
              <a
                href="https://github.com/atul-techx/HHGoa-RAG-Model"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-2 px-4 py-2 bg-[#024b2d] hover:bg-[#00663c] text-[#ffde00] border border-[#ffde00]/30 rounded-xl text-xs font-extrabold transition cursor-pointer shadow-md"
              >
                <Github className="w-4 h-4" />
                <span>GitHub Repository</span>
                <ExternalLink className="w-3.5 h-3.5 ml-1 opacity-70" />
              </a>
              
              <div className="px-3.5 py-2 bg-[#ff007a]/20 border border-[#ff007a]/40 text-[#ff007a] rounded-xl text-xs font-extrabold font-mono">
                #IrisAI
              </div>
            </div>
          </div>

          {/* Right Navigation Columns */}
          <div className="md:col-span-7 grid grid-cols-2 sm:grid-cols-3 gap-8 text-xs font-mono">
            <div>
              <h3 className="text-[#ffde00] font-extrabold uppercase tracking-wider mb-4">Products &amp; Features</h3>
              <ul className="space-y-2.5 text-[#a3c4b0]">
                <li className="hover:text-white transition cursor-pointer flex items-center gap-1.5">
                  <Mic className="w-3 h-3 text-[#ff007a]" /> Voice RAG Engine
                </li>
                <li className="hover:text-white transition cursor-pointer flex items-center gap-1.5">
                  <Zap className="w-3 h-3 text-[#ffde00]" /> Sub-200ms Latency
                </li>
                <li className="hover:text-white transition cursor-pointer">5 Chunking Strategies</li>
                <li className="hover:text-white transition cursor-pointer">Extractive Neural QA</li>
                <li className="hover:text-white transition cursor-pointer flex items-center gap-1.5">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" /> Guardrails Harness
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-[#ffde00] font-extrabold uppercase tracking-wider mb-4">Integrations</h3>
              <ul className="space-y-2.5 text-[#a3c4b0]">
                <li className="hover:text-white transition cursor-pointer">Sarvam AI STT</li>
                <li className="hover:text-white transition cursor-pointer">ElevenLabs Voice</li>
                <li className="hover:text-white transition cursor-pointer">Gemini 2.5 Flash</li>
                <li className="hover:text-white transition cursor-pointer">FAISS Vector Index</li>
                <li className="hover:text-white transition cursor-pointer">TF-IDF Typo Engine</li>
              </ul>
            </div>

            <div className="col-span-2 sm:col-span-1">
              <h3 className="text-[#ffde00] font-extrabold uppercase tracking-wider mb-4">HH Goa 2026</h3>
              <ul className="space-y-2.5 text-[#a3c4b0]">
                <li className="hover:text-white transition cursor-pointer">MS MARCO Dataset</li>
                <li className="hover:text-white transition cursor-pointer">Accuracy Evaluation</li>
                <li className="hover:text-white transition cursor-pointer">P50/P70/P100 Suite</li>
                <li className="hover:text-white transition cursor-pointer">FastAPI Backend</li>
                <li className="hover:text-white transition cursor-pointer">Vite / React UI</li>
              </ul>
            </div>
          </div>

        </div>

        {/* Bottom Giant Watermark Typography Section (Matching Redrob AI Reference UI) */}
        <div className="relative pt-6 pb-2 flex flex-col items-center justify-center text-center overflow-hidden">
          
          {/* Subtitle / Description requested by user */}
          <div className="mb-2 inline-flex items-center gap-2 px-4 py-1 rounded-full bg-gradient-to-r from-[#ff007a]/20 via-[#ffde00]/20 to-[#00663c]/40 border border-[#ffde00]/40 text-[#ffde00] font-mono text-xs font-black tracking-widest uppercase shadow-lg backdrop-blur-sm">
            <span className="text-[#ff007a]">🌈</span> A Rainbow Messenger <span className="text-[#ffde00]">⚡</span>
          </div>

          {/* Huge Semi-Transparent Typography Overlay: "IRIS" */}
          <h1 className="text-[110px] sm:text-[180px] md:text-[250px] font-black tracking-tighter leading-none select-none pointer-events-none uppercase font-hh-serif bg-gradient-to-b from-white/20 via-white/10 to-transparent bg-clip-text text-transparent opacity-80 hover:opacity-100 transition-opacity">
            IRIS
          </h1>

          <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-4 mt-2 pt-4 border-t border-[#00663c]/40 text-xs font-mono text-[#a3c4b0]">
            <div>
              © 2026 <span className="text-[#ffde00] font-bold">IRIS</span> — Voice RAG Intelligence Engine. Built for House of Hackers Goa.
            </div>
            <div className="flex items-center gap-1 text-slate-400">
              Crafted with <Heart className="w-3.5 h-3.5 text-[#ff007a] fill-[#ff007a]" /> for <span className="text-white font-bold">#HHGoa2026</span>
            </div>
          </div>

        </div>
      </div>
    </footer>
  );
}
