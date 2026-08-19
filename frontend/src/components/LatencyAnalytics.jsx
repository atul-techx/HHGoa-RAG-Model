import React, { useState, useEffect } from 'react';
import { Zap, Play, CheckCircle2, AlertTriangle, RefreshCw, BarChart2, Check, Clock } from 'lucide-react';

export default function LatencyAnalytics() {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState('semantic');

  const runBenchmark = async () => {
    setIsRunning(true);
    try {
      const res = await fetch(`/api/benchmark?strategy=${selectedStrategy}&num_queries=25`);
      const data = await res.json();
      setBenchmarkData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    runBenchmark();
  }, [selectedStrategy]);

  return (
    <div className="space-y-8">
      
      {/* Control Banner */}
      <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Zap className="w-6 h-6 text-amber-400" />
            <h2 className="text-xl font-bold text-white font-heading">Pipeline Latency Benchmarking Suite</h2>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Automated P50, P70, and P100 latency analytics measured across 25 real MSMARCO test queries.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedStrategy}
            onChange={(e) => setSelectedStrategy(e.target.value)}
            className="bg-slate-950 border border-pink-500/30 rounded-xl px-3 py-2 text-xs text-slate-200 font-semibold focus:outline-none focus:border-pink-500"
          >
            <option value="semantic">Semantic Boundary</option>
            <option value="overlap_optimized">Overlap-Optimized</option>
            <option value="metadata_aware">Metadata-Aware</option>
            <option value="fixed_size">Fixed-Size</option>
          </select>

          <button
            onClick={runBenchmark}
            disabled={isRunning}
            className="px-5 py-2.5 bg-gradient-to-r from-pink-600 via-amber-500 to-cyan-500 hover:opacity-90 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center space-x-2 shadow-lg shadow-pink-500/20 transition"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Benchmarking 25 Queries...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Run Latency Harness</span>
              </>
            )}
          </button>
        </div>
      </div>

      {benchmarkData && (
        <>
          {/* Key Percentiles Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            
            {/* P50 Card */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-pink-500/30 text-center">
              <div className="text-xs font-bold font-mono text-slate-400 uppercase tracking-widest">P50 Latency (Median)</div>
              <div className="text-4xl font-black font-heading text-pink-400 my-2">
                {benchmarkData.p50_latency_ms} <span className="text-sm font-normal text-slate-400">ms</span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono">50% queries faster than this</div>
            </div>

            {/* P70 Card */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-amber-500/30 text-center">
              <div className="text-xs font-bold font-mono text-slate-400 uppercase tracking-widest">P70 Latency (70th %)</div>
              <div className="text-4xl font-black font-heading text-amber-400 my-2">
                {benchmarkData.p70_latency_ms} <span className="text-sm font-normal text-slate-400">ms</span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono">70% queries faster than this</div>
            </div>

            {/* P100 Max Card */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-cyan-500/30 text-center">
              <div className="text-xs font-bold font-mono text-slate-400 uppercase tracking-widest">P100 Latency (Max)</div>
              <div className="text-4xl font-black font-heading text-cyan-400 my-2">
                {benchmarkData.p100_max_latency_ms} <span className="text-sm font-normal text-slate-400">ms</span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono">Absolute worst-case run</div>
            </div>

            {/* Target Compliance Card */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-emerald-500/40 text-center flex flex-col items-center justify-center">
              <div className="text-xs font-bold font-mono text-slate-400 uppercase tracking-widest">Sub-200ms Compliance</div>
              <div className="text-3xl font-black font-heading text-emerald-400 my-1">
                {benchmarkData.under_200ms_percentage}%
              </div>
              <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-full text-[11px] font-bold font-mono">
                &lt;200ms TARGET FULFILLED
              </span>
            </div>

          </div>

          {/* Average Stage Breakdown & Query List */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Stage Averages */}
            <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-pink-500" />
                <span>Average Stage Timings</span>
              </h3>

              <div className="space-y-4 pt-2">
                {[
                  { label: 'Speech-to-Text (STT)', ms: benchmarkData.averages.stt_ms, color: 'bg-pink-500' },
                  { label: 'Guardrails Check', ms: benchmarkData.averages.guardrails_ms, color: 'bg-amber-400' },
                  { label: 'Vector DB Retrieval', ms: benchmarkData.averages.retrieval_ms, color: 'bg-cyan-400' },
                  { label: 'Answer Synthesis', ms: benchmarkData.averages.generation_ms, color: 'bg-purple-500' }
                ].map((st, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-300">{st.label}</span>
                      <span className="text-slate-100 font-bold">{st.ms} ms</span>
                    </div>
                    <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden">
                      <div className={`h-full ${st.color}`} style={{ width: `${Math.min(100, st.ms * 4)}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-4 border-t border-slate-800 text-xs text-slate-400 font-mono">
                Total Queries Tested: <strong className="text-white">{benchmarkData.total_queries_tested}</strong>
              </div>
            </div>

            {/* Individual Query Log */}
            <div className="lg:col-span-2 glass-panel p-6 bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <span>Detailed Query Benchmark Log</span>
              </h3>

              <div className="max-h-80 overflow-y-auto space-y-2 pr-1">
                {benchmarkData.query_results.map((q) => (
                  <div key={q.id} className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-3 truncate mr-4">
                      <span className="text-slate-500 font-bold">#{q.id}</span>
                      <span className="text-slate-200 truncate">{q.query}</span>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        q.total_latency_ms <= 200.0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                      }`}>
                        {q.total_latency_ms} ms
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </>
      )}

    </div>
  );
}
