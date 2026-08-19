import React, { useState, useEffect } from 'react';
import { Database, Plus, Search, FileText, CheckCircle2 } from 'lucide-react';

export default function DatasetExplorer() {
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [search, setSearch] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newText, setNewText] = useState('');
  const [newCategory, setNewCategory] = useState('General');
  const [isAdding, setIsAdding] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  const fetchDataset = async () => {
    try {
      const res = await fetch('/api/dataset');
      const data = await res.json();
      setDatasetInfo(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDataset();
  }, []);

  const handleAddDocument = async (e) => {
    e.preventDefault();
    if (!newTitle.trim() || !newText.trim()) return;

    setIsAdding(true);
    try {
      const res = await fetch('/api/dataset/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, text: newText, category: newCategory })
      });
      const data = await res.json();
      setStatusMsg('Document added & vector index updated!');
      setNewTitle('');
      setNewText('');
      fetchDataset();
      setTimeout(() => setStatusMsg(''), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAdding(false);
    }
  };

  const filteredDocs = datasetInfo?.documents?.filter(
    (d) => d.title.toLowerCase().includes(search.toLowerCase()) || d.text.toLowerCase().includes(search.toLowerCase())
  ) || [];

  return (
    <div className="space-y-8">
      
      {/* Top Banner */}
      <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Database className="w-6 h-6 text-pink-500" />
            <h2 className="text-xl font-bold text-white font-heading">MSMARCO-XI Knowledge Base Explorer</h2>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Browse indexed MSMARCO dataset passages or inject custom documents to expand the vector store.
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300">
            Docs: <strong className="text-pink-400">{datasetInfo?.total_documents || 0}</strong>
          </span>
          <span className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300">
            Vector Chunks: <strong className="text-cyan-400">{datasetInfo?.indexed_chunks || 0}</strong>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column (2 Cols): Documents List & Search */}
        <div className="lg:col-span-2 space-y-4">
          
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search dataset documents by keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>

          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
            {filteredDocs.map((doc) => (
              <div key={doc.id} className="glass-panel p-4 bg-slate-900/90 border border-slate-800 space-y-2 hover:border-pink-500/30 transition">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-pink-400 font-mono flex items-center gap-1.5">
                    <FileText className="w-4 h-4" />
                    {doc.title}
                  </span>
                  <span className="px-2 py-0.5 bg-slate-950 text-slate-400 border border-slate-800 rounded text-[10px] font-mono">
                    {doc.category}
                  </span>
                </div>
                <p className="text-xs text-slate-300 font-sans leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
                  {doc.text}
                </p>
                <div className="text-[10px] text-slate-500 font-mono flex justify-between">
                  <span>ID: {doc.id}</span>
                  <span className="text-cyan-400 font-bold">MSMARCO-XI</span>
                </div>
              </div>
            ))}
          </div>

        </div>

        {/* Right Column (1 Col): Add Custom Document Form */}
        <div className="glass-panel p-6 bg-slate-900/90 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center gap-2">
            <Plus className="w-4 h-4 text-amber-400" />
            <span>Add Custom Document</span>
          </h3>

          {statusMsg && (
            <div className="p-3 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-xl text-xs font-mono flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{statusMsg}</span>
            </div>
          )}

          <form onSubmit={handleAddDocument} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Document Title</label>
              <input
                type="text"
                placeholder="Enter title..."
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-pink-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
              <input
                type="text"
                placeholder="e.g. AI Technology / Goa History"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-pink-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Passage Text</label>
              <textarea
                rows={5}
                placeholder="Enter knowledge text content..."
                value={newText}
                onChange={(e) => setNewText(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-pink-500 font-mono resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={isAdding || !newTitle.trim() || !newText.trim()}
              className="w-full py-2.5 bg-gradient-to-r from-pink-600 to-amber-500 hover:opacity-90 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center justify-center space-x-2 shadow-lg shadow-pink-500/20 transition"
            >
              <span>Add & Re-index Vector DB</span>
            </button>
          </form>
        </div>

      </div>

    </div>
  );
}
