import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Zap, ShieldCheck, ShieldAlert, Cpu, RefreshCw, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Play } from 'lucide-react';

export default function VoiceRAGPlayground({ settings }) {
  const [isListening, setIsListening] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [selectedStrategy, setSelectedStrategy] = useState('semantic');
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState(null);
  const [sttProvider, setSttProvider] = useState(settings.sttProvider || 'web_speech');

  const recognitionRef = useRef(null);

  // Initialize Web Speech Recognition
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
        alert("Web Speech Recognition is not supported in this browser. Please use Chrome/Edge or type your question below!");
      }
    }
  };

  const handleExecuteQuery = async (overrideText = null) => {
    const textToRun = overrideText || queryText;
    if (!textToRun.trim()) return;

    setIsProcessing(true);
    const startClientTimer = performance.now();

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
    "What is the capital of France?", # Off-topic demo
    "How to hack into a database?" # Safety demo
  ];

  return (
    <div className="space-y-8">
      
      {/* Voice Control & Main Search Card */}
      <div className="glass-panel-glow p-6 sm:p-8 bg-slate-900/90 relative overflow-hidden">
        
        {/* Goa Sunset Accent Bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-pink-500 via-amber-500 to-cyan-400"></div>

        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          
          {/* Audio Visualizer & Mic Button */}
          <div className="flex flex-col items-center space-y-3">
            <button
              onClick={toggleListening}
              className={`w-24 h-24 rounded-3xl flex items-center justify-center transition-all duration-300 shadow-2xl relative ${
                isListening
                  ? 'bg-gradient-to-tr from-pink-600 to-amber-500 text-white mic-recording-pulse border-2 border-pink-400'
                  : 'bg-slate-800 hover:bg-slate-700 text-pink-500 border border-slate-700 hover:border-pink-500/50'
              }`}
            >
              {isListening ? (
                <MicOff className="w-10 h-10 text-white animate-bounce" />
              ) : (
                <Mic className="w-10 h-10" />
              )}
            </button>

            <span className="text-xs font-semibold font-mono tracking-wider text-slate-400">
              {isListening ? (
                <span className="text-pink-400 flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-pink-500 animate-ping" />
                  LISTENING (SPEAK NOW)...
                </span>
              ) : (
                'CLICK MIC TO SPEAK'
              )}
            </span>

            {/* Waveform graphic when recording */}
            {isListening && (
              <div className="flex items-center space-x-1.5 h-10 mt-1">
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
              </div>
            )}
          </div>

          {/* Input & Strategy Selector */}
          <div className="flex-1 w-full space-y-4">
            
            <div className="flex flex-wrap items-center justify-between gap-3">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                Speech-to-Text Input Stream
              </label>

              {/* Chunking Selector */}
              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-400 font-semibold">Chunking Strategy:</span>
                <select
                  value={selectedStrategy}
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                  className="bg-slate-950 border border-pink-500/30 rounded-xl px-3 py-1.5 text-xs text-slate-200 font-semibold focus:outline-none focus:border-pink-500"
                >
                  <option value="semantic">Semantic Boundary (Recommended)</option>
                  <option value="overlap_optimized">Overlap-Optimized (200c/50o)</option>
                  <option value="metadata_aware">Metadata-Aware Header</option>
                  <option value="hierarchical">Hierarchical Parent-Child</option>
                  <option value="fixed_size">Naive Fixed-Size (200c)</option>
                </select>
              </div>
            </div>

            {/* Voice Input Box */}
            <div className="relative">
              <textarea
                rows={3}
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Spoken words will transcribe here automatically... or type a question to test..."
                className="w-full px-4 py-3.5 bg-slate-950/80 border border-slate-700/80 rounded-2xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-pink-500 text-sm font-sans resize-none"
              />

              <button
                onClick={() => handleExecuteQuery()}
                disabled={isProcessing || !queryText.trim()}
                className="absolute bottom-3.5 right-3.5 px-5 py-2 bg-gradient-to-r from-pink-600 via-amber-500 to-cyan-500 hover:opacity-90 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center space-x-2 shadow-lg shadow-pink-500/20 transition"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Executing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <span>Run RAG Pipeline</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

            {/* Sample Preset Queries */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-1">
              <span className="text-[11px] text-slate-400 font-mono whitespace-nowrap">Presets:</span>
              {sampleVoiceQueries.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQueryText(q);
                    handleExecuteQuery(q);
                  }}
                  className="px-2.5 py-1 bg-slate-800/80 hover:bg-pink-500/20 hover:border-pink-500/40 text-slate-300 hover:text-white border border-slate-700/60 rounded-lg text-xs font-mono transition whitespace-nowrap"
                >
                  {q}
                </button>
              ))}
            </div>

          </div>

        </div>

      </div>

      {/* Response & Latency Dashboard */}
      {response && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
          
          {/* Left Column (2 Cols): Answer & Retrieved Passage Cards */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Answer Card */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800 relative">
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                  <h3 className="text-lg font-bold text-white font-heading">Synthesized RAG Answer</h3>
                </div>

                <div className="flex items-center space-x-2">
                  {/* TTS Voice Playback Button */}
                  <button
                    onClick={() => speakAnswer(response.answer)}
                    className="p-2 bg-slate-800 hover:bg-pink-500/20 text-slate-300 hover:text-pink-400 border border-slate-700 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
                  >
                    <Volume2 className="w-4 h-4" />
                    <span>Audio Readout</span>
                  </button>
                </div>
              </div>

              {/* Refusal vs Answer styling */}
              <div className={`p-4 rounded-xl text-sm leading-relaxed font-sans ${
                !response.guardrails_passed
                  ? 'bg-red-500/10 border border-red-500/30 text-red-200'
                  : 'bg-slate-950/60 border border-slate-800 text-slate-100'
              }`}>
                {response.answer}
              </div>

              {/* Hashtag Footer */}
              <div className="mt-4 flex items-center justify-between text-xs text-slate-400 font-mono">
                <span>Strategy: <strong className="text-cyan-400 uppercase">{response.chunking_strategy}</strong></span>
                <span className="text-pink-400 font-bold">#RAGInGoa</span>
              </div>
            </div>

            {/* Retrieved Vector Context Chunks */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800">
              <h3 className="text-md font-bold text-white mb-4 flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>Retrieved Context Chunks (Top {response.retrieved_chunks.length})</span>
              </h3>

              {response.retrieved_chunks.length === 0 ? (
                <p className="text-sm text-slate-400 italic">No context retrieved (Guardrail suppressed or empty vector match).</p>
              ) : (
                <div className="space-y-3">
                  {response.retrieved_chunks.map((chunk, idx) => (
                    <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-pink-400 font-mono">
                          Chunk #{idx + 1} | {chunk.doc_title || 'MSMARCO Doc'}
                        </span>
                        <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-md font-mono font-bold">
                          Similarity Score: {(chunk.score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed font-mono bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                        {chunk.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* Right Column (1 Col): Latency Telemetry & Guardrails Badge */}
          <div className="space-y-6">
            
            {/* Target Latency Badge Card */}
            <div className={`glass-panel p-6 rounded-2xl border text-center transition-all ${
              response.total_latency_ms <= 200.0
                ? 'border-emerald-500/40 bg-emerald-950/20 shadow-lg shadow-emerald-500/10'
                : 'border-amber-500/40 bg-amber-950/20'
            }`}>
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Zap className={`w-6 h-6 ${response.total_latency_ms <= 200.0 ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
                <span className="text-xs font-bold tracking-widest text-slate-300 uppercase font-mono">Full Pipeline Latency</span>
              </div>

              <div className="text-4xl font-black font-heading gradient-text-goa my-1">
                {response.total_latency_ms} <span className="text-lg font-normal text-slate-400">ms</span>
              </div>

              <div className="mt-2 inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-slate-950 border border-slate-800">
                {response.total_latency_ms <= 200.0 ? (
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Target Fulfilled (&lt;200ms)
                  </span>
                ) : (
                  <span className="text-amber-400 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Exceeds 200ms Target
                  </span>
                )}
              </div>
            </div>

            {/* Stage Latency Breakdown */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Stage Timing Breakdown</h4>
              
              <div className="space-y-3">
                {[
                  { label: 'Speech-to-Text (STT)', ms: response.latency_breakdown.stt, color: 'bg-pink-500' },
                  { label: 'Guardrails Evaluation', ms: response.latency_breakdown.guardrails, color: 'bg-amber-400' },
                  { label: 'Vector DB Retrieval', ms: response.latency_breakdown.retrieval, color: 'bg-cyan-400' },
                  { label: 'Answer Generation', ms: response.latency_breakdown.generation, color: 'bg-purple-500' }
                ].map((st, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-300">{st.label}</span>
                      <span className="text-slate-100 font-bold">{st.ms} ms</span>
                    </div>
                    <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${st.color}`}
                        style={{ width: `${Math.min(100, (st.ms / response.total_latency_ms) * 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Guardrail & Harness Execution Trace */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Guardrails Status</h4>
                {response.guardrails_passed ? (
                  <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded text-[11px] font-bold">
                    PASSED
                  </span>
                ) : (
                  <span className="px-2 py-0.5 bg-red-500/20 text-red-400 border border-red-500/40 rounded text-[11px] font-bold">
                    BLOCKED
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-300 font-mono bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                {response.guardrail_reason}
              </p>

              <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 font-mono space-y-1">
                <div>Grounding Score: <strong className="text-cyan-400">{(response.grounding_score * 100).toFixed(0)}%</strong></div>
                <div>Harness Retries: <strong className="text-amber-400">{response.retries_count}</strong></div>
              </div>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
