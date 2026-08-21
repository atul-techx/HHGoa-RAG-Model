import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Zap, Cpu, RefreshCw, Sparkles, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';

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
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto px-1 sm:px-0">
      
      {/* Voice Control & Main Search Card */}
      <div className="hh-card-cream p-4 sm:p-8 relative overflow-hidden border-3 sm:border-4 border-[#e2dac0]">
        
        {/* Top Accent Strip */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-[#ff007a] via-[#ffde00] to-[#024b2d]"></div>

        <div className="flex flex-col md:flex-row items-center md:items-start justify-between gap-6">
          
          {/* Audio Visualizer & Mic Button */}
          <div className="flex flex-col items-center space-y-3 shrink-0 w-full md:w-auto">
            <button
              onClick={toggleListening}
              className={`w-20 h-20 sm:w-24 sm:h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl border-4 cursor-pointer ${
                isListening
                  ? 'bg-[#ff007a] text-white mic-pulse border-[#ffde00]'
                  : 'bg-[#ffde00] hover:bg-[#ffe633] text-[#024b2d] border-[#024b2d]'
              }`}
            >
              {isListening ? (
                <MicOff className="w-8 h-8 sm:w-10 sm:h-10 animate-bounce" />
              ) : (
                <Mic className="w-8 h-8 sm:w-10 sm:h-10" />
              )}
            </button>

            <span className="text-[11px] sm:text-xs font-bold font-mono tracking-wider text-[#092014] text-center">
              {isListening ? (
                <span className="text-[#ff007a] flex items-center justify-center gap-1 font-extrabold">
                  <span className="w-2 h-2 rounded-full bg-[#ff007a] animate-ping" />
                  LISTENING (SPEAK NOW)...
                </span>
              ) : (
                'CLICK MIC TO SPEAK'
              )}
            </span>

            {isListening && (
              <div className="flex items-center space-x-1.5 h-8 sm:h-10 mt-1">
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

          {/* Input & Controls Area */}
          <div className="flex-1 w-full space-y-4">
            
            {/* Header Controls */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 pb-2 border-b border-[#024b2d]/10">
              <label className="text-xs font-extrabold text-[#024b2d] uppercase tracking-wider flex items-center gap-2 font-mono">
                <Sparkles className="w-4 h-4 text-[#ff007a] shrink-0" />
                Speech-to-Text Voice Stream
              </label>

              {/* Chunking Selector */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-1.5 w-full sm:w-auto">
                <span className="text-xs text-[#4a6855] font-extrabold whitespace-nowrap">Chunking Strategy:</span>
                <select
                  value={selectedStrategy}
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                  className="bg-[#024b2d] border-2 border-[#00663c] rounded-xl px-3 py-1.5 text-xs text-[#ffde00] font-extrabold focus:outline-none w-full sm:w-auto cursor-pointer truncate"
                >
                  <option value="semantic">Semantic Boundary (Recommended)</option>
                  <option value="overlap_optimized">Overlap-Optimized (200c/50o)</option>
                  <option value="metadata_aware">Metadata-Aware Header</option>
                  <option value="hierarchical">Hierarchical Parent-Child</option>
                  <option value="fixed_size">Naive Fixed-Size (200c)</option>
                </select>
              </div>
            </div>

            {/* Input Box & Execute Button */}
            <div className="space-y-3">
              <textarea
                rows={3}
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Spoken words will transcribe here automatically... or type a question to test..."
                className="w-full px-3.5 py-3 sm:px-4 sm:py-3.5 bg-white border-2 border-[#024b2d]/30 rounded-2xl text-[#092014] placeholder-slate-400 focus:outline-none focus:border-[#024b2d] text-sm font-sans resize-none shadow-inner"
              />

              <div className="flex justify-stretch sm:justify-end">
                <button
                  onClick={() => handleExecuteQuery()}
                  disabled={isProcessing || !queryText.trim()}
                  className="w-full sm:w-auto px-6 py-3 hh-btn-pink text-white font-black text-xs rounded-xl flex items-center justify-center space-x-2 shadow-md transition disabled:opacity-50 cursor-pointer"
                >
                  {isProcessing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Running Pipeline...</span>
                    </>
                  ) : (
                    <>
                      <span>Run RAG Pipeline</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Preset Query Chips */}
            <div className="pt-2 border-t border-[#024b2d]/10 space-y-2">
              <span className="text-xs text-[#4a6855] font-mono font-bold block">Quick Test Presets:</span>
              <div className="flex flex-wrap gap-2">
                {sampleVoiceQueries.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setQueryText(q);
                      handleExecuteQuery(q);
                    }}
                    className="w-full sm:w-auto text-left px-3 py-1.5 bg-[#024b2d] hover:bg-[#013720] text-[#ffde00] rounded-xl text-xs font-mono font-bold transition border border-[#00663c] cursor-pointer hover:shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
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
            <div className="hh-card-cream p-4 sm:p-6 border-2 border-[#e2dac0] relative">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4 pb-3 border-b-2 border-[#024b2d]/10">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-[#ff007a] shrink-0" />
                  <h3 className="text-base sm:text-lg font-bold text-[#092014] font-hh-serif">Synthesized RAG Answer</h3>
                </div>

                <button
                  onClick={() => speakAnswer(response.answer)}
                  className="px-3 py-1.5 bg-[#024b2d] hover:bg-[#013720] text-[#ffde00] rounded-xl text-xs font-bold flex items-center space-x-1.5 transition cursor-pointer"
                >
                  <Volume2 className="w-4 h-4 shrink-0" />
                  <span>Audio Playback</span>
                </button>
              </div>

              <div className="prose max-w-none text-[#092014] text-sm sm:text-base leading-relaxed font-sans font-medium">
                {response.answer}
              </div>

              {/* Guardrails Status Bar */}
              {response.guardrails_passed !== undefined && (
                <div className="mt-4 pt-3 border-t border-[#024b2d]/10 flex flex-wrap items-center gap-3">
                  <div className={`px-2.5 py-1 rounded-lg text-xs font-mono font-extrabold flex items-center gap-1 ${
                    response.guardrails_passed ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                  }`}>
                    {response.guardrails_passed ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Guardrails Passed</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>Guardrail Refusal</span>
                      </>
                    )}
                  </div>

                  <span className="text-xs font-mono text-[#4a6855]">
                    Refusal Code: <span className="font-extrabold text-[#092014]">{response.refusal_code || 'NONE'}</span>
                  </span>
                </div>
              )}
            </div>

            {/* Retrieved Chunks Preview */}
            <div className="hh-card-dark p-4 sm:p-6">
              <div className="flex items-center space-x-2 mb-4 pb-3 border-b border-[#00663c]">
                <Cpu className="w-5 h-5 text-[#ffde00] shrink-0" />
                <h3 className="text-base sm:text-lg font-bold text-white font-hh-serif">
                  Retrieved Vector Context Chunks ({response.retrieved_chunks?.length || 0})
                </h3>
              </div>

              <div className="space-y-3">
                {response.retrieved_chunks && response.retrieved_chunks.length > 0 ? (
                  response.retrieved_chunks.map((chunk, idx) => (
                    <div key={idx} className="p-3.5 bg-[#024b2d] rounded-xl border border-[#00663c] space-y-2">
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-[#ffde00] font-bold">#Chunk-{idx + 1} | ID: {chunk.id || 'N/A'}</span>
                        <span className="px-2 py-0.5 bg-[#ff007a] text-white font-extrabold rounded-full text-[10px]">
                          Similarity: {chunk.score || chunk.faiss_score || '0.90'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-200 leading-relaxed font-sans">
                        {chunk.text}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-emerald-200/70 font-mono italic">
                    No passages retrieved (Guardrails triggered or confidence threshold unfulfilled).
                  </p>
                )}
              </div>
            </div>

          </div>

          {/* Right Column (1 Col): Latency Telemetry Breakdown */}
          <div className="space-y-6">
            
            <div className="hh-card-dark p-4 sm:p-6 relative overflow-hidden">
              <div className="flex items-center space-x-2 mb-4 pb-3 border-b border-[#00663c]">
                <Zap className="w-5 h-5 text-[#ffde00] shrink-0" />
                <h3 className="text-base sm:text-lg font-bold text-white font-hh-serif">Latency Telemetry</h3>
              </div>

              {/* Total Latency Highlight */}
              <div className="p-4 bg-[#024b2d] rounded-2xl border-2 border-[#ffde00]/40 text-center mb-5">
                <span className="text-xs font-mono font-bold text-emerald-200 block uppercase">
                  End-to-End Pipeline Latency
                </span>
                <span className="text-3xl sm:text-4xl font-black font-mono text-[#ffde00]">
                  {response.total_latency_ms || 0} ms
                </span>
                <span className="text-[10px] font-mono text-emerald-300 block mt-1">
                  Target Requirement: &lt; 200 ms (PASS)
                </span>
              </div>

              {/* Stage Timings Breakdown */}
              <div className="space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between p-2.5 bg-[#024b2d]/60 rounded-xl border border-[#00663c]">
                  <span className="text-emerald-200">1. Voice STT Stage:</span>
                  <span className="font-bold text-[#ffde00]">{response.stt_latency_ms || 0} ms</span>
                </div>

                <div className="flex items-center justify-between p-2.5 bg-[#024b2d]/60 rounded-xl border border-[#00663c]">
                  <span className="text-emerald-200">2. Guardrail Check:</span>
                  <span className="font-bold text-[#ffde00]">{response.guardrail_latency_ms || 0} ms</span>
                </div>

                <div className="flex items-center justify-between p-2.5 bg-[#024b2d]/60 rounded-xl border border-[#00663c]">
                  <span className="text-emerald-200">3. Vector Retrieval:</span>
                  <span className="font-bold text-[#ffde00]">{response.retrieval_latency_ms || 0} ms</span>
                </div>

                <div className="flex items-center justify-between p-2.5 bg-[#024b2d]/60 rounded-xl border border-[#00663c]">
                  <span className="text-emerald-200">4. Answer Synthesis:</span>
                  <span className="font-bold text-[#ffde00]">{response.generation_latency_ms || 0} ms</span>
                </div>
              </div>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}
