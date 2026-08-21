import React from 'react';
import { X, Server, Key, Mic } from 'lucide-react';

export default function ModelSettingsModal({ isOpen, onClose, settings, setSettings }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#013720]/80 backdrop-blur-sm">
      <div className="hh-card-cream w-full max-w-lg p-6 border-4 border-[#e2dac0] shadow-2xl relative">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b-2 border-[#024b2d]/15">
          <div className="flex items-center space-x-2">
            <Server className="w-5 h-5 text-[#ff007a]" />
            <h3 className="text-lg font-bold text-[#092014] font-hh-serif">Model &amp; STT Configuration</h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-[#4a6855] hover:text-[#092014] hover:bg-[#024b2d]/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-5 py-4">
          
          {/* AI Model Mode Choice */}
          <div>
            <label className="block text-xs font-bold text-[#024b2d] mb-1.5 flex items-center gap-1.5 font-mono">
              <Server className="w-3.5 h-3.5 text-[#ff007a]" />
              AI Answer Engine Mode
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'extractive_qa', label: 'DistilBERT Neural QA', desc: 'Local Transformer (<50ms)' },
                { id: 'generative_llm', label: 'Gemini LLM', desc: 'Generative Synthesis' },
                { id: 'hybrid_auto', label: 'Hybrid Auto', desc: 'Neural QA + LLM Fallback' }
              ].map((mode) => (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setSettings({ ...settings, modelMode: mode.id })}
                  className={`p-3 rounded-xl border-2 text-left transition ${
                    (settings.modelMode || 'extractive_qa') === mode.id
                      ? 'border-[#ff007a] bg-[#ff007a]/10 text-[#092014] font-bold'
                      : 'border-[#024b2d]/20 bg-white text-[#4a6855] hover:border-[#024b2d]'
                  }`}
                >
                  <div className="text-xs font-bold">{mode.label}</div>
                  <div className="text-[10px] text-[#4a6855] mt-0.5">{mode.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Custom Model Endpoint */}
          <div>
            <label className="block text-xs font-bold text-[#024b2d] mb-1.5 flex items-center gap-1.5 font-mono">
              <Server className="w-3.5 h-3.5 text-[#ff007a]" />
              Custom Model Endpoint URL (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. http://localhost:11434/api/generate"
              value={settings.customModelEndpoint || ''}
              onChange={(e) => setSettings({ ...settings, customModelEndpoint: e.target.value })}
              className="w-full px-3.5 py-2.5 bg-white border-2 border-[#024b2d]/30 rounded-xl text-sm text-[#092014] placeholder-slate-400 focus:outline-none focus:border-[#024b2d] font-mono"
            />
            <p className="text-[11px] text-[#4a6855] mt-1 font-sans">
              Connect your own LLM model backend server or choose local Transformer Neural QA engine.
            </p>
          </div>

          {/* STT Choice */}
          <div>
            <label className="block text-xs font-bold text-[#024b2d] mb-1.5 flex items-center gap-1.5 font-mono">
              <Mic className="w-3.5 h-3.5 text-[#ff007a]" />
              Speech-to-Text (STT) Provider
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'web_speech', label: 'Web Speech API', desc: 'Instant 0-latency' },
                { id: 'sarvam', label: 'Sarvam AI', desc: 'Saarika STT' },
                { id: 'elevenlabs', label: 'ElevenLabs', desc: 'Streaming STT' }
              ].map((provider) => (
                <button
                  key={provider.id}
                  type="button"
                  onClick={() => setSettings({ ...settings, sttProvider: provider.id })}
                  className={`p-3 rounded-xl border-2 text-left transition ${
                    settings.sttProvider === provider.id
                      ? 'border-[#ff007a] bg-[#ff007a]/10 text-[#092014] font-bold'
                      : 'border-[#024b2d]/20 bg-white text-[#4a6855] hover:border-[#024b2d]'
                  }`}
                >
                  <div className="text-xs font-bold">{provider.label}</div>
                  <div className="text-[10px] text-[#4a6855] mt-0.5">{provider.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Keys */}
          {settings.sttProvider === 'sarvam' && (
            <div>
              <label className="block text-xs font-bold text-[#024b2d] mb-1 flex items-center gap-1.5 font-mono">
                <Key className="w-3.5 h-3.5 text-[#ff007a]" />
                Sarvam AI Subscription Key
              </label>
              <input
                type="password"
                placeholder="Enter Sarvam Subscription Key..."
                value={settings.sarvamKey || ''}
                onChange={(e) => setSettings({ ...settings, sarvamKey: e.target.value })}
                className="w-full px-3.5 py-2.5 bg-white border-2 border-[#024b2d]/30 rounded-xl text-sm text-[#092014] focus:outline-none focus:border-[#024b2d] font-mono"
              />
            </div>
          )}

          {settings.sttProvider === 'elevenlabs' && (
            <div>
              <label className="block text-xs font-bold text-[#024b2d] mb-1 flex items-center gap-1.5 font-mono">
                <Key className="w-3.5 h-3.5 text-[#ff007a]" />
                ElevenLabs API Key
              </label>
              <input
                type="password"
                placeholder="Enter ElevenLabs API Key..."
                value={settings.elevenKey || ''}
                onChange={(e) => setSettings({ ...settings, elevenKey: e.target.value })}
                className="w-full px-3.5 py-2.5 bg-white border-2 border-[#024b2d]/30 rounded-xl text-sm text-[#092014] focus:outline-none focus:border-[#024b2d] font-mono"
              />
            </div>
          )}

        </div>

        <div className="pt-4 border-t-2 border-[#024b2d]/15 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 hh-btn-yellow text-[#024b2d] font-extrabold text-sm rounded-xl shadow-md"
          >
            Save Settings
          </button>
        </div>

      </div>
    </div>
  );
}
