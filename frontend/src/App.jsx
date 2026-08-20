import React, { useState } from 'react';
import Header from './components/Header';
import VoiceRAGPlayground from './components/VoiceRAGPlayground';
import ChunkingComparator from './components/ChunkingComparator';
import LatencyAnalytics from './components/LatencyAnalytics';
import GuardrailsHarness from './components/GuardrailsHarness';
import DatasetExplorer from './components/DatasetExplorer';
import ModelSettingsModal from './components/ModelSettingsModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('playground');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settings, setSettings] = useState({
    sttProvider: 'web_speech',
    customModelEndpoint: '',
    sarvamKey: '',
    elevenKey: ''
  });

  return (
    <div className="min-h-screen flex flex-col font-sans">
      
      {/* Navigation Header */}
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main App Canvas */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'playground' && <VoiceRAGPlayground settings={settings} />}
        {activeTab === 'chunking' && <ChunkingComparator />}
        {activeTab === 'latency' && <LatencyAnalytics />}
        {activeTab === 'guardrails' && <GuardrailsHarness />}
        {activeTab === 'dataset' && <DatasetExplorer />}
      </main>

      {/* Footer Branding */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            Iris AI Voice RAG Engine <span className="text-pink-500">#IrisAI</span>
          </div>
          <div className="text-slate-400">
            Voice-Enabled Sub-200ms RAG Pipeline <span className="text-cyan-400">|</span> Sarvam &amp; ElevenLabs STT Engine
          </div>
        </div>
      </footer>

      {/* Settings Modal */}
      <ModelSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        setSettings={setSettings}
      />

    </div>
  );
}
