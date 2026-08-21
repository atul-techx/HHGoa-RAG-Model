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
      if (res.ok) {
        setDatasetInfo(data);
      }
    } catch (err) {
      console.error("Fetch dataset error:", err);
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
      if (!res.ok) {
        throw new Error(data.detail || "Failed to add document");
      }
      setStatusMsg('Document added & vector index updated!');
      setNewTitle('');
      setNewText('');
      fetchDataset();
      setTimeout(() => setStatusMsg(''), 3000);
    } catch (err) {
      console.error("Add document error:", err);
      alert(`Add document error: ${err.message || 'Server error'}`);
    } finally {
      setIsAdding(false);
    }
  };

  const filteredDocs = datasetInfo?.documents?.filter(
    (d) => d.title.toLowerCase().includes(search.toLowerCase()) || d.text.toLowerCase().includes(search.toLowerCase())
  ) || [];

  return (
    <div className="space-y-8">
      
      {/* Top Banner Card */}
      <div className="hh-card-cream p-6 border-4 border-[#e2dac0] flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Database className="w-6 h-6 text-[#ff007a]" />
            <h2 className="text-xl font-bold text-[#092014] font-hh-serif">MSMARCO-XI Knowledge Base Explorer</h2>
          </div>
          <p className="text-xs text-[#4a6855] font-mono mt-1">
            Browse indexed MSMARCO dataset passages or inject custom documents into vector store.
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="px-3 py-1.5 bg-[#024b2d] text-[#ffde00] rounded-xl font-bold">
            Docs: {datasetInfo?.total_documents || 0}
          </span>
          <span className="px-3 py-1.5 bg-[#024b2d] text-[#ffde00] rounded-xl font-bold">
            Vector Chunks: {datasetInfo?.indexed_chunks || 0}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column (2 Cols): Documents List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="relative">
            <Search className="w-4 h-4 text-[#024b2d] absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search dataset documents by keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white border-2 border-[#024b2d]/30 rounded-xl text-xs text-[#092014] focus:outline-none focus:border-[#024b2d] font-mono"
            />
          </div>

          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
            {filteredDocs.map((doc) => (
              <div key={doc.id} className="hh-card-cream p-4 border-2 border-[#e2dac0] space-y-2 hover:border-[#024b2d] transition">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-[#024b2d] font-mono flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-[#ff007a]" />
                    {doc.title}
                  </span>
                  <span className="px-2 py-0.5 bg-[#ffde00] text-[#024b2d] rounded text-[10px] font-mono font-bold">
                    {doc.category}
                  </span>
                </div>
                <p className="text-xs text-[#092014] font-sans leading-relaxed bg-white p-3 rounded-lg border border-[#024b2d]/15">
                  {doc.text}
                </p>
                <div className="text-[10px] text-[#4a6855] font-mono flex justify-between font-bold">
                  <span>ID: {doc.id}</span>
                  <span className="text-[#ff007a]">MSMARCO-XI</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column (1 Col): Form */}
        <div className="hh-card-dark p-6 space-y-4 border-2 border-[#00663c]">
          <h3 className="text-sm font-bold text-[#ffde00] uppercase font-mono tracking-wider flex items-center gap-2">
            <Plus className="w-4 h-4 text-[#ff007a]" />
            <span>Add Custom Document</span>
          </h3>

          {statusMsg && (
            <div className="p-3 bg-[#ffde00] text-[#024b2d] rounded-xl text-xs font-mono font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#ff007a]" />
              <span>{statusMsg}</span>
            </div>
          )}

          <form onSubmit={handleAddDocument} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-[#a3c4b0] mb-1">Document Title</label>
              <input
                type="text"
                placeholder="Enter title..."
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="w-full px-3 py-2 bg-[#024b2d] border border-[#00663c] rounded-xl text-xs text-white focus:outline-none focus:border-[#ffde00] font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#a3c4b0] mb-1">Category</label>
              <input
                type="text"
                placeholder="e.g. AI Technology / Goa History"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full px-3 py-2 bg-[#024b2d] border border-[#00663c] rounded-xl text-xs text-white focus:outline-none focus:border-[#ffde00] font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#a3c4b0] mb-1">Passage Text</label>
              <textarea
                rows={5}
                placeholder="Enter text content..."
                value={newText}
                onChange={(e) => setNewText(e.target.value)}
                className="w-full px-3 py-2 bg-[#024b2d] border border-[#00663c] rounded-xl text-xs text-white focus:outline-none focus:border-[#ffde00] font-mono resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={isAdding || !newTitle.trim() || !newText.trim()}
              className="w-full py-2.5 hh-btn-yellow text-[#024b2d] font-extrabold text-xs rounded-xl flex items-center justify-center space-x-2 shadow-md transition disabled:opacity-50"
            >
              <span>Add &amp; Re-index Vector DB</span>
            </button>
          </form>
        </div>

      </div>

    </div>
  );
}
