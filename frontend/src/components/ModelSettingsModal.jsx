import React from 'react';
import { X, Server, Key, Mic, ShieldAlert } from 'lucide-react';

export default function ModelSettingsModal({ isOpen, onClose, settings, setSettings }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="glass-panel-glow w-full max-w-lg p-6 bg-slate-900 border border-pink-500/30 rounded-2xl shadow-2xl relative">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Server className="w-5 h-5 text-pink-500" />
            <h3 className="text-lg font-bold text-white font-heading">Model & STT Configuration</h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-5 py-4">
          
          {/* Custom Model Endpoint */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-cyan-400" />
              Custom Model Endpoint URL (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. http://localhost:11434/api/generate or https://api.openai.com/v1/chat/completions"
              value={settings.customModelEndpoint || ''}
              onChange={(e) => setSettings({ ...settings, customModelEndpoint: e.target.value })}
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Connect your own LLM model backend server. Defaults to sub-200ms grounded synthesizer.
            </p>
          </div>

          {/* STT Provider Choice */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Mic className="w-3.5 h-3.5 text-pink-500" />
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
                  className={`p-3 rounded-xl border text-left transition ${
                    settings.sttProvider === provider.id
                      ? 'border-pink-500 bg-pink-500/10 text-white'
                      : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs font-bold">{provider.label}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{provider.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* API Key Inputs */}
          {settings.sttProvider === 'sarvam' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-amber-400" />
                Sarvam AI Subscription Key
              </label>
              <input
                type="password"
                placeholder="Enter Sarvam Subscription Key..."
                value={settings.sarvamKey || ''}
                onChange={(e) => setSettings({ ...settings, sarvamKey: e.target.value })}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
          )}

          {settings.sttProvider === 'elevenlabs' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-cyan-400" />
                ElevenLabs API Key
              </label>
              <input
                type="password"
                placeholder="Enter ElevenLabs API Key..."
                value={settings.elevenKey || ''}
                onChange={(e) => setSettings({ ...settings, elevenKey: e.target.value })}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-gradient-to-r from-pink-600 to-amber-500 text-white font-semibold text-sm rounded-xl hover:opacity-90 shadow-lg shadow-pink-500/25"
          >
            Save Settings
          </button>
        </div>

      </div>
    </div>
  );
}
