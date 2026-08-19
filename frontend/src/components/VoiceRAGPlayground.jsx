import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Zap, ShieldCheck, ShieldAlert, Cpu, RefreshCw, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Play } from 'lucide-react';

export default function VoiceRAGPlayground({ settings }) {
  const [isListening, setIsListening] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [selectedStrategy, setSelectedStrategy] = useState('semantic');
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState(null);

  const recognitionRef = useRef(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = true;
      rec.lang = 'en-US';

      rec.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setQueryText(transcript);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setQueryText('');
      setResponse(null);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
          setIsListening(true);
        } catch (e) {
          console.error(e);
        }
      } else {
        alert("Web Speech Recognition is not supported in this browser. Please use Chrome/Edge or type your question!");
      }
    }
  };

  const handleExecuteQuery = async (overrideText = null) => {
    const textToRun = overrideText || queryText;
    if (!textToRun.trim()) return;

    setIsProcessing(true);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: textToRun,
          chunking_strategy: selectedStrategy,
          stt_provider: settings.sttProvider || 'web_speech',
          stt_latency_ms: isListening ? 42.0 : 12.0,
          custom_model_endpoint: settings.customModelEndpoint || null
        })
      });

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      alert("Failed to execute RAG pipeline query.");
    } finally {
      setIsProcessing(false);
    }
  };

  const speakAnswer = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const sampleVoiceQueries = [
    "What is Retrieval-Augmented Generation (RAG)?",
    "What is the capital of Goa and its history?",
    "How do Chunking Strategies affect vector retrieval?",
    "What is P50 and P100 latency in software systems?",
    "What is the capital of France?", // Off-topic demo
    "How to hack into a database?" // Safety demo
  ];

  return (
    <div className="space-y-8">
      
      {/* Top Banner Card - HH Goa Cream Theme */}
      <div className="hh-card-cream p-6 sm:p-8 relative overflow-hidden border-4 border-[#e2dac0]">
        
        {/* Top Accent Strip */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-[#ff007a] via-[#ffde00] to-[#024b2d]"></div>

        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          
          {/* Mic Button & Waveform */}
          <div className="flex flex-col items-center space-y-3 shrink-0">
            <button
              onClick={toggleListening}
              className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl border-4 ${
                isListening
                  ? 'bg-[#ff007a] text-white mic-pulse border-[#ffde00]'
                  : 'bg-[#ffde00] hover:bg-[#ffe633] text-[#024b2d] border-[#024b2d]'
              }`}
            >
              {isListening ? (
                <MicOff className="w-10 h-10 animate-bounce" />
              ) : (
                <Mic className="w-10 h-10" />
              )}
            </button>

            <span className="text-xs font-bold font-mono tracking-wider text-[#092014]">
              {isListening ? (
                <span className="text-[#ff007a] flex items-center gap-1 font-extrabold">
                  <span className="w-2 h-2 rounded-full bg-[#ff007a] animate-ping" />
                  LISTENING (SPEAK NOW)...
                </span>
              ) : (
                'CLICK MIC TO SPEAK'
              )}
            </span>

            {isListening && (
              <div className="flex items-center space-x-1.5 h-10 mt-1">
                <div className="wave-bar-hh"></div>
                <div className="wave-bar-hh"></div>
                <div className="wave-bar-hh"></div>
                <div className="wave-bar-hh"></div>
                <div className="wave-bar-hh"></div>
                <div className="wave-bar-hh"></div>
                <div className="wave-bar-hh"></div>
              </div>
            )}
          </div>

          {/* Voice Input Textarea & Strategy Selector */}
          <div className="flex-1 w-full space-y-4">
            
            <div className="flex flex-wrap items-center justify-between gap-3">
              <label className="text-xs font-extrabold text-[#024b2d] uppercase tracking-wider flex items-center gap-2 font-mono">
                <Sparkles className="w-4 h-4 text-[#ff007a]" />
                Speech-to-Text Voice Stream
              </label>

              {/* Strategy Selector */}
              <div className="flex items-center space-x-2">
                <span className="text-xs text-[#4a6855] font-bold">Chunking:</span>
                <select
                  value={selectedStrategy}
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                  className="bg-[#024b2d] border-2 border-[#00663c] rounded-xl px-3 py-1.5 text-xs text-[#ffde00] font-bold focus:outline-none"
                >
                  <option value="semantic">Semantic Boundary (Recommended)</option>
                  <option value="overlap_optimized">Overlap-Optimized (200c/50o)</option>
                  <option value="metadata_aware">Metadata-Aware Header</option>
                  <option value="hierarchical">Hierarchical Parent-Child</option>
                  <option value="fixed_size">Naive Fixed-Size (200c)</option>
                </select>
              </div>
            </div>

            {/* Input Box */}
            <div className="relative">
              <textarea
                rows={3}
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Spoken words will transcribe here automatically... or type a query..."
                className="w-full px-4 py-3.5 bg-white border-2 border-[#024b2d]/30 rounded-2xl text-[#092014] placeholder-slate-400 focus:outline-none focus:border-[#024b2d] text-sm font-sans resize-none shadow-inner"
              />

              <button
                onClick={() => handleExecuteQuery()}
                disabled={isProcessing || !queryText.trim()}
                className="absolute bottom-3.5 right-3.5 px-5 py-2.5 hh-btn-pink text-white font-extrabold text-xs rounded-xl flex items-center space-x-2 shadow-md transition disabled:opacity-50"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Processing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <span>Run RAG Engine</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

            {/* Preset Query Chips - Designed like HH Goa directional signs */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-1">
              <span className="text-[11px] text-[#4a6855] font-mono font-bold whitespace-nowrap">Presets:</span>
              {sampleVoiceQueries.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQueryText(q);
                    handleExecuteQuery(q);
                  }}
                  className="px-3 py-1 bg-[#024b2d] hover:bg-[#013720] text-[#ffde00] rounded-lg text-xs font-mono font-bold transition whitespace-nowrap border border-[#00663c]"
                >
                  {q}
                </button>
              ))}
            </div>

          </div>

        </div>

      </div>

      {/* Response Cards */}
      {response && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
          
          {/* Left Column (2 Cols): Answer & Context Chunks */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Answer Card */}
            <div className="hh-card-cream p-6 border-2 border-[#e2dac0] relative">
              <div className="flex items-center justify-between mb-4 pb-3 border-b-2 border-[#024b2d]/10">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-[#ff007a]" />
                  <h3 className="text-lg font-bold text-[#092014] font-hh-serif">Synthesized RAG Answer</h3>
                </div>

                <button
                  onClick={() => speakAnswer(response.answer)}
                  className="px-3 py-1.5 bg-[#024b2d] hover:bg-[#013720] text-[#ffde00] rounded-xl text-xs font-bold flex items-center space-x-1.5 transition"
                >
                  <Volume2 className="w-4 h-4" />
                  <span>Audio Playback</span>
                </button>
              </div>

              <div className={`p-4 rounded-xl text-sm leading-relaxed font-sans ${
                !response.guardrails_passed
                  ? 'bg-red-100 border-2 border-red-400 text-red-900 font-medium'
                  : 'bg-white border-2 border-[#024b2d]/20 text-[#092014]'
              }`}>
                {response.answer}
              </div>

              <div className="mt-4 flex items-center justify-between text-xs text-[#4a6855] font-mono font-bold">
                <span>Strategy: <strong className="text-[#024b2d] uppercase">{response.chunking_strategy}</strong></span>
                <span className="px-2.5 py-0.5 bg-[#ff007a] text-white rounded-full text-[10px] font-bold">#RAGInGoa</span>
              </div>
            </div>

            {/* Retrieved Chunks Card */}
            <div className="hh-card-cream p-6 border-2 border-[#e2dac0]">
              <h3 className="text-md font-bold text-[#092014] mb-4 flex items-center space-x-2 font-hh-serif">
                <Cpu className="w-4 h-4 text-[#024b2d]" />
                <span>Retrieved MSMARCO Passages ({response.retrieved_chunks.length})</span>
              </h3>

              {response.retrieved_chunks.length === 0 ? (
                <p className="text-sm text-[#4a6855] italic">No context retrieved (Guardrail block or low vector score).</p>
              ) : (
                <div className="space-y-3">
                  {response.retrieved_chunks.map((chunk, idx) => (
                    <div key={idx} className="p-4 bg-white border-2 border-[#024b2d]/15 rounded-xl space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-[#024b2d] font-mono">
                          Chunk #{idx + 1} | {chunk.doc_title || 'MSMARCO Doc'}
                        </span>
                        <span className="px-2 py-0.5 bg-[#ffde00] text-[#024b2d] font-bold rounded-md font-mono text-[11px] border border-[#e2c800]">
                          Match: {(chunk.score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-xs text-[#092014] leading-relaxed font-mono bg-[#fffdf0] p-3 rounded-lg border border-[#e2dac0]">
                        {chunk.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* Right Column (1 Col): Latency Telemetry & Guardrail Status */}
          <div className="space-y-6">
            
            {/* Target Latency Badge Card */}
            <div className={`hh-card-dark p-6 text-center border-2 ${
              response.total_latency_ms <= 200.0 ? 'border-[#ffde00]' : 'border-[#ff007a]'
            }`}>
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Zap className="w-6 h-6 text-[#ffde00] animate-pulse" />
                <span className="text-xs font-extrabold tracking-widest text-[#a3c4b0] uppercase font-mono">Pipeline Latency</span>
              </div>

              <div className="text-4xl font-black font-hh-serif text-[#ffde00] my-1">
                {response.total_latency_ms} <span className="text-lg font-normal text-white">ms</span>
              </div>

              <div className="mt-2 inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-[#024b2d] border border-[#00663c]">
                {response.total_latency_ms <= 200.0 ? (
                  <span className="text-emerald-300 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Target Fulfilled (&lt;200ms)
                  </span>
                ) : (
                  <span className="text-[#ff007a] flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Exceeds 200ms Target
                  </span>
                )}
              </div>
            </div>

            {/* Stage Timing Breakdown */}
            <div className="hh-card-dark p-6 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#ffde00] font-mono">Stage Latency Breakdown</h4>
              
              <div className="space-y-3">
                {[
                  { label: 'Speech-to-Text (STT)', ms: response.latency_breakdown.stt, color: 'bg-[#ffde00]' },
                  { label: 'Guardrails Check', ms: response.latency_breakdown.guardrails, color: 'bg-[#ff007a]' },
                  { label: 'Vector DB Retrieval', ms: response.latency_breakdown.retrieval, color: 'bg-emerald-400' },
                  { label: 'Answer Generation', ms: response.latency_breakdown.generation, color: 'bg-yellow-300' }
                ].map((st, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-[#a3c4b0] font-semibold">{st.label}</span>
                      <span className="text-white font-bold">{st.ms} ms</span>
                    </div>
                    <div className="w-full h-2.5 bg-[#024b2d] rounded-full overflow-hidden">
                      <div
                        className={`h-full ${st.color}`}
                        style={{ width: `${Math.min(100, (st.ms / response.total_latency_ms) * 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Guardrails Status */}
            <div className="hh-card-dark p-6 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#ffde00] font-mono">Guardrails Status</h4>
                {response.guardrails_passed ? (
                  <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-[11px] font-bold">
                    PASSED
                  </span>
                ) : (
                  <span className="px-2.5 py-0.5 bg-[#ff007a]/20 text-[#ff007a] border border-[#ff007a]/40 rounded text-[11px] font-bold">
                    BLOCKED
                  </span>
                )}
              </div>

              <p className="text-xs text-[#a3c4b0] font-mono bg-[#024b2d] p-3 rounded-lg border border-[#00663c]">
                {response.guardrail_reason}
              </p>

              <div className="pt-2 border-t border-[#00663c] text-[11px] text-[#a3c4b0] font-mono space-y-1">
                <div>Grounding Score: <strong className="text-[#ffde00]">{(response.grounding_score * 100).toFixed(0)}%</strong></div>
                <div>Harness Retries: <strong className="text-[#ff007a]">{response.retries_count}</strong></div>
              </div>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
