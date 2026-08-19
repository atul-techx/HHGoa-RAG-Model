import React, { useState, useEffect } from 'react';
import { Cpu, RefreshCw, CheckCircle, ArrowRight, Layers, FileText } from 'lucide-react';

export default function ChunkingComparator() {
  const [testQuery, setTestQuery] = useState('What are optimal Chunking Strategies for Vector DBs?');
  const [sampleText, setSampleText] = useState(
    'Retrieval-Augmented Generation (RAG) is an architectural framework that improves Large Language Model responses by grounding the model on external knowledge bases. RAG combines vector retrieval engines with generative language models. During inference, the query is converted into an embedding, relevant passage chunks are retrieved from a vector database (such as FAISS, Qdrant, or HNSW index), and the context is prepended to the user prompt. Naive fixed-size chunking splits text rigidly by character length. Overlap-optimized chunking preserves context across boundaries. Semantic chunking splits text along sentence and paragraph breaks. Metadata-aware chunking injects document title and tags into chunks. Hierarchical chunking maps small child vectors back to parent context.'
  );
  const [comparison, setComparison] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const runComparison = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/chunking/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: testQuery, sample_text: sampleText })
      });
      const data = await res.json();
      setComparison(data.strategies);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runComparison();
  }, []);

  const strategyDescriptions = {
    fixed_size: "Splits text blindly by character/token count (e.g., 200 chars). Fastest, but destroys sentence structure.",
    overlap_optimized: "Sliding window with 50-char overlap. Preserves boundary context and prevents phrase truncation.",
    semantic: "Detects sentence boundaries (. ! ?) and semantic breaks. Maintains coherent human thoughts in each chunk.",
    metadata_aware: "Prepends document title, passage ID, and category tags to every chunk before embedding.",
    hierarchical: "Creates micro 100-char child chunks for pin-point vector similarity mapped back to parent document."
  };

  return (
    <div className="space-y-8">
      
      {/* Header Info */}
      <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800">
        <div className="flex items-center space-x-3 mb-2">
          <Cpu className="w-6 h-6 text-pink-500" />
          <h2 className="text-xl font-bold text-white font-heading">Engineered Chunking Strategy Comparator</h2>
        </div>
        <p className="text-xs text-slate-400 font-mono">
          Compare 5 distinct chunking strategies on MSMARCO text. Inspect chunk boundaries, total chunk counts, and retrieval precision.
        </p>

        {/* Input & Run Button */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2 space-y-2">
            <label className="text-xs font-semibold text-slate-300">Test Retrieval Query</label>
            <input
              type="text"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={runComparison}
              disabled={isLoading}
              className="w-full px-4 py-2 bg-gradient-to-r from-pink-600 to-amber-500 hover:opacity-90 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center justify-center space-x-2 transition"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Layers className="w-4 h-4" />
                  <span>Compare 5 Strategies</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Strategies Grid */}
      {comparison && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(comparison).map(([stratKey, data]) => (
            <div key={stratKey} className="glass-panel p-5 bg-slate-900/90 border border-slate-800 flex flex-col justify-between space-y-4 hover:border-pink-500/40 transition">
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-pink-500" />
                    {stratKey.replace('_', ' ')}
                  </h3>
                  <span className="px-2 py-0.5 bg-pink-500/10 text-pink-400 border border-pink-500/30 rounded text-xs font-mono font-bold">
                    {data.chunk_count} Chunks
                  </span>
                </div>

                <p className="text-xs text-slate-400 font-sans leading-relaxed">
                  {strategyDescriptions[stratKey]}
                </p>

                {/* Score badge */}
                <div className="p-2.5 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-mono">Retrieval Score:</span>
                  <span className="text-xs font-bold text-cyan-400 font-mono">
                    {(data.top_retrieval_score * 100).toFixed(1)}% Match
                  </span>
                </div>

                {/* Chunks Preview */}
                <div className="space-y-2 pt-2">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                    Chunk Snippet Preview:
                  </div>
                  <div className="p-3 bg-slate-950 text-[11px] font-mono text-slate-300 rounded-xl border border-slate-800/80 leading-relaxed max-h-32 overflow-y-auto">
                    {data.sample_chunk}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 text-[10px] text-slate-400 font-mono flex justify-between">
                <span>Retrieval Time: {data.retrieval_ms} ms</span>
                <span className="text-amber-400">#RAGInGoa</span>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}
