import React, { useState, useEffect } from 'react';
import { Cpu, RefreshCw, Layers } from 'lucide-react';

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
    fixed_size: "Splits text rigidly by character count (200 chars). Fast, but splits words and sentences.",
    overlap_optimized: "Sliding window with 50-char overlap. Preserves boundary context across chunk breaks.",
    semantic: "Detects sentence boundaries (. ! ?) and semantic breaks. Preserves coherent thoughts.",
    metadata_aware: "Injects document title, passage ID, and category headers into every chunk before vector embedding.",
    hierarchical: "Generates micro 100-char child chunks for pin-point vector similarity mapped to full parent passage."
  };

  return (
    <div className="space-y-8">
      
      {/* Top Banner Card */}
      <div className="hh-card-cream p-6 border-4 border-[#e2dac0]">
        <div className="flex items-center space-x-3 mb-2">
          <Cpu className="w-6 h-6 text-[#ff007a]" />
          <h2 className="text-xl font-bold text-[#092014] font-hh-serif">5 Engineered Chunking Strategies</h2>
        </div>
        <p className="text-xs text-[#4a6855] font-mono">
          Compare 5 distinct chunking strategies on MSMARCO text. Inspect chunk boundaries, total counts, and vector match score.
        </p>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2 space-y-1.5">
            <label className="text-xs font-bold text-[#024b2d]">Test Retrieval Query</label>
            <input
              type="text"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              className="w-full px-3.5 py-2 bg-white border-2 border-[#024b2d]/30 rounded-xl text-xs text-[#092014] focus:outline-none focus:border-[#024b2d] font-mono"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={runComparison}
              disabled={isLoading}
              className="w-full py-2 px-4 hh-btn-yellow text-[#024b2d] font-extrabold text-xs rounded-xl flex items-center justify-center space-x-2 transition"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Comparing...</span>
                </>
              ) : (
                <>
                  <Layers className="w-4 h-4" />
                  <span>Run 5-Strategy Test</span>
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
            <div key={stratKey} className="hh-card-cream p-5 border-2 border-[#e2dac0] flex flex-col justify-between space-y-4 hover:border-[#024b2d] transition">
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-extrabold text-[#024b2d] uppercase font-mono tracking-wider flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#ff007a]" />
                    {stratKey.replace('_', ' ')}
                  </h3>
                  <span className="px-2.5 py-0.5 bg-[#ffde00] text-[#024b2d] border border-[#e2c800] rounded-md text-xs font-mono font-extrabold">
                    {data.chunk_count} Chunks
                  </span>
                </div>

                <p className="text-xs text-[#4a6855] font-sans leading-relaxed">
                  {strategyDescriptions[stratKey]}
                </p>

                <div className="p-2.5 bg-[#024b2d] rounded-xl text-white flex items-center justify-between font-mono">
                  <span className="text-xs text-[#a3c4b0]">Vector Match:</span>
                  <span className="text-xs font-bold text-[#ffde00]">
                    {(data.top_retrieval_score * 100).toFixed(1)}% Score
                  </span>
                </div>

                <div className="space-y-2 pt-1">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-[#024b2d] font-mono">
                    Chunk Snippet Preview:
                  </div>
                  <div className="p-3 bg-white text-[11px] font-mono text-[#092014] rounded-xl border border-[#024b2d]/20 leading-relaxed max-h-32 overflow-y-auto">
                    {data.sample_chunk}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-[#024b2d]/10 text-[10px] text-[#4a6855] font-mono flex justify-between font-bold">
                <span>Retrieval: {data.retrieval_ms} ms</span>
                <span className="text-[#ff007a]">#RAGInGoa</span>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}
