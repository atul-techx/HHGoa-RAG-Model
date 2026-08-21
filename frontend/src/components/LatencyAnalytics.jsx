import React, { useState, useEffect } from 'react';
import { Zap, Play, RefreshCw, BarChart2, Clock } from 'lucide-react';

export default function LatencyAnalytics() {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState('semantic');

  const runBenchmark = async () => {
    setIsRunning(true);
    try {
      const res = await fetch(`/api/benchmark?strategy=${selectedStrategy}&num_queries=25`);
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Benchmark request failed");
      }
      setBenchmarkData(data);
    } catch (err) {
      console.error("Benchmark error:", err);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    runBenchmark();
  }, [selectedStrategy]);

  return (
    <div className="space-y-8">
      
      {/* Top Banner Card */}
      <div className="hh-card-cream p-6 border-4 border-[#e2dac0] flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Zap className="w-6 h-6 text-[#ff007a]" />
            <h2 className="text-xl font-bold text-[#092014] font-hh-serif">Pipeline Latency Benchmarking Suite</h2>
          </div>
          <p className="text-xs text-[#4a6855] font-mono mt-1">
            P50, P70, and P100 latency analytics measured across 25 real MSMARCO test queries.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedStrategy}
            onChange={(e) => setSelectedStrategy(e.target.value)}
            className="bg-[#024b2d] border-2 border-[#00663c] rounded-xl px-3 py-2 text-xs text-[#ffde00] font-bold focus:outline-none"
          >
            <option value="semantic">Semantic Boundary</option>
            <option value="overlap_optimized">Overlap-Optimized</option>
            <option value="metadata_aware">Metadata-Aware</option>
            <option value="fixed_size">Fixed-Size</option>
          </select>

          <button
            onClick={runBenchmark}
            disabled={isRunning}
            className="px-5 py-2.5 hh-btn-pink text-white font-extrabold text-xs rounded-xl flex items-center space-x-2 shadow-md transition disabled:opacity-50"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Benchmarking...</span>
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
            <div className="hh-card-cream p-6 border-2 border-[#e2dac0] text-center">
              <div className="text-xs font-bold font-mono text-[#4a6855] uppercase tracking-widest">P50 Latency (Median)</div>
              <div className="text-4xl font-black font-hh-serif text-[#024b2d] my-2">
                {benchmarkData.p50_latency_ms} <span className="text-sm font-normal text-[#4a6855]">ms</span>
              </div>
              <div className="text-[11px] text-[#4a6855] font-mono font-semibold">50% queries faster than this</div>
            </div>

            {/* P70 Card */}
            <div className="hh-card-cream p-6 border-2 border-[#e2dac0] text-center">
              <div className="text-xs font-bold font-mono text-[#4a6855] uppercase tracking-widest">P70 Latency (70th %)</div>
              <div className="text-4xl font-black font-hh-serif text-[#ff007a] my-2">
                {benchmarkData.p70_latency_ms} <span className="text-sm font-normal text-[#4a6855]">ms</span>
              </div>
              <div className="text-[11px] text-[#4a6855] font-mono font-semibold">70% queries faster than this</div>
            </div>

            {/* P100 Max Card */}
            <div className="hh-card-cream p-6 border-2 border-[#e2dac0] text-center">
              <div className="text-xs font-bold font-mono text-[#4a6855] uppercase tracking-widest">P100 Latency (Max)</div>
              <div className="text-4xl font-black font-hh-serif text-[#024b2d] my-2">
                {benchmarkData.p100_max_latency_ms} <span className="text-sm font-normal text-[#4a6855]">ms</span>
              </div>
              <div className="text-[11px] text-[#4a6855] font-mono font-semibold">Absolute worst-case run</div>
            </div>

            {/* Target Compliance Card */}
            <div className="hh-card-dark p-6 text-center flex flex-col items-center justify-center border-2 border-[#ffde00]">
              <div className="text-xs font-bold font-mono text-[#a3c4b0] uppercase tracking-widest">Sub-200ms Compliance</div>
              <div className="text-3xl font-black font-hh-serif text-[#ffde00] my-1">
                {benchmarkData.under_200ms_percentage}%
              </div>
              <span className="px-3 py-1 bg-[#ffde00] text-[#024b2d] rounded-full text-[11px] font-extrabold font-mono">
                &lt;200ms TARGET FULFILLED
              </span>
            </div>

          </div>

          {/* Average Stage Breakdown & Query List */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Stage Averages */}
            <div className="hh-card-dark p-6 space-y-4 border-2 border-[#00663c]">
              <h3 className="text-sm font-bold text-[#ffde00] uppercase font-mono tracking-wider flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-[#ff007a]" />
                <span>Average Stage Timings</span>
              </h3>

              <div className="space-y-4 pt-2">
                {[
                  { label: 'Speech-to-Text (STT)', ms: benchmarkData.averages.stt_ms, color: 'bg-[#ffde00]' },
                  { label: 'Guardrails Check', ms: benchmarkData.averages.guardrails_ms, color: 'bg-[#ff007a]' },
                  { label: 'Vector DB Retrieval', ms: benchmarkData.averages.retrieval_ms, color: 'bg-emerald-400' },
                  { label: 'Answer Synthesis', ms: benchmarkData.averages.generation_ms, color: 'bg-yellow-300' }
                ].map((st, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-[#a3c4b0]">{st.label}</span>
                      <span className="text-white font-bold">{st.ms} ms</span>
                    </div>
                    <div className="w-full h-2.5 bg-[#024b2d] rounded-full overflow-hidden">
                      <div className={`h-full ${st.color}`} style={{ width: `${Math.min(100, st.ms * 4)}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-4 border-t border-[#00663c] text-xs text-[#a3c4b0] font-mono">
                Total Queries Tested: <strong className="text-white">{benchmarkData.total_queries_tested}</strong>
              </div>
            </div>

            {/* Individual Query Log */}
            <div className="lg:col-span-2 hh-card-cream p-6 border-2 border-[#e2dac0] space-y-4">
              <h3 className="text-sm font-bold text-[#092014] uppercase font-mono tracking-wider flex items-center gap-2 font-hh-serif">
                <Clock className="w-4 h-4 text-[#024b2d]" />
                <span>Detailed Query Benchmark Log</span>
              </h3>

              <div className="max-h-80 overflow-y-auto space-y-2 pr-1">
                {benchmarkData.query_results.map((q) => (
                  <div key={q.id} className="p-3 bg-white rounded-xl border border-[#024b2d]/15 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-3 truncate mr-4">
                      <span className="text-[#024b2d] font-bold">#{q.id}</span>
                      <span className="text-[#092014] truncate">{q.query}</span>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      <span className={`px-2.5 py-0.5 rounded text-[11px] font-extrabold ${
                        q.total_latency_ms <= 200.0 ? 'bg-[#ffde00] text-[#024b2d] border border-[#e2c800]' : 'bg-red-100 text-red-700'
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
