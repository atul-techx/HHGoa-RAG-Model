import React, { useState } from 'react';
import Header from './components/Header';
import VoiceRAGPlayground from './components/VoiceRAGPlayground';
import ChunkingComparator from './components/ChunkingComparator';
import LatencyAnalytics from './components/LatencyAnalytics';
import GuardrailsHarness from './components/GuardrailsHarness';
import DatasetExplorer from './components/DatasetExplorer';
import ModelSettingsModal from './components/ModelSettingsModal';
import Footer from './components/Footer';

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
    <div className="min-h-screen flex flex-col font-sans bg-[#024b2d]">
      
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
      <Footer />

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
