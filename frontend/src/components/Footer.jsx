import React from 'react';
import { Sparkles, Mic, Github, ExternalLink, Zap, ShieldCheck, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="relative bg-[#012515] text-white py-8 overflow-hidden border-t-4 border-[#00663c] mt-auto">
      
      {/* Background Watermark Typography: "IRIS" */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden z-0">
        <h1 className="text-[120px] sm:text-[200px] md:text-[280px] font-black tracking-tighter uppercase font-hh-serif text-white/[0.04]">
          IRIS
        </h1>
      </div>

      {/* Background Subtle Gradient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-full bg-gradient-to-b from-[#ffde00]/5 via-transparent to-transparent pointer-events-none z-0" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
          
          {/* Main Headline & Description Column */}
          <div className="md:col-span-6 flex flex-col justify-between">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-0.5 bg-[#024b2d] border border-[#00663c] rounded-full text-xs font-mono font-extrabold text-[#ffde00] mb-3 shadow-sm">
                <Sparkles className="w-3.5 h-3.5 text-[#ff007a]" />
                <span>HH GOA 2026 OFFICIAL ENTRY</span>
              </div>
              
              <h2 className="text-2xl sm:text-3xl font-black font-hh-serif tracking-tight text-white leading-tight">
                Your Next Move Starts Here.
              </h2>
              
              <p className="mt-2 text-xs text-[#a3c4b0] font-sans leading-relaxed max-w-md">
                Sub-200ms Voice Retrieval Augmented Generation Engine with multi-strategy chunking, 100% grounded extractive neural QA, and real-time model harness guardrails.
              </p>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-2.5">
              <a
                href="https://github.com/atul-techx/HHGoa-RAG-Model"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-2 px-3.5 py-1.5 bg-[#024b2d] hover:bg-[#00663c] text-[#ffde00] border border-[#ffde00]/30 rounded-xl text-xs font-extrabold transition cursor-pointer shadow-md"
              >
                <Github className="w-4 h-4" />
                <span>GitHub Repository</span>
                <ExternalLink className="w-3.5 h-3.5 ml-1 opacity-70" />
              </a>
              
              <div className="px-3 py-1.5 bg-[#ff007a]/20 border border-[#ff007a]/40 text-[#ff007a] rounded-xl text-xs font-extrabold font-mono">
                #RAGInGoa
              </div>

              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#ff007a]/20 via-[#ffde00]/20 to-[#00663c]/40 border border-[#ffde00]/30 text-[#ffde00] font-mono text-[11px] font-black uppercase shadow-sm">
                <span className="text-[#ff007a]">🌈</span> A Rainbow Messenger <span className="text-[#ffde00]">⚡</span>
              </div>
            </div>
          </div>

          {/* Right Navigation Columns (Integrations Column Removed) */}
          <div className="md:col-span-6 grid grid-cols-2 gap-6 text-xs font-mono">
            <div>
              <h3 className="text-[#ffde00] font-extrabold uppercase tracking-wider mb-3">Products &amp; Features</h3>
              <ul className="space-y-2 text-[#a3c4b0]">
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
              <h3 className="text-[#ffde00] font-extrabold uppercase tracking-wider mb-3">HH Goa 2026</h3>
              <ul className="space-y-2 text-[#a3c4b0]">
                <li className="hover:text-white transition cursor-pointer">MS MARCO Dataset</li>
                <li className="hover:text-white transition cursor-pointer">Accuracy Evaluation</li>
                <li className="hover:text-white transition cursor-pointer">P50/P70/P100 Suite</li>
                <li className="hover:text-white transition cursor-pointer">FastAPI Backend</li>
                <li className="hover:text-white transition cursor-pointer">Vite / React UI</li>
              </ul>
            </div>
          </div>

        </div>
      </div>
    </footer>
  );
}
