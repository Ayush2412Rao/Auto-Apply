'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Shield, 
  Sliders, 
  CheckCircle2, 
  Save, 
  Key, 
  Mail, 
  Database,
  Bot
} from 'lucide-react';
import { fetchPreferences, updatePreferences } from '@/lib/api';

export default function SettingsPage() {
  const [preferences, setPreferences] = useState({
    target_titles: [
      'Software Engineer',
      'Software Development Engineer',
      'AI Engineer',
      'Data Engineer',
      'Data Analyst',
      'Business Analyst'
    ],
    preferred_locations: [
      'Remote',
      'Noida',
      'Gurgaon',
      'Delhi',
      'Bengaluru',
      'Pune',
      'Hyderabad',
      'Indore',
      'Mysore',
      'Kolkata'
    ],
    min_match_score: 75,
    automation_mode: 'automatic',
    max_applications_per_hour: 5,
    max_applications_per_day: 25,
    notice_period_days: 15,
    work_authorization: 'Authorized to work in India (Citizen)'
  });
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchPreferences();
        if (data) setPreferences(prev => ({ ...prev, ...data }));
      } catch (e) {
        console.error(e);
      }
    }
    load();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await updatePreferences(preferences);
      setSavedMessage('Settings successfully saved to database.');
      setTimeout(() => setSavedMessage(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-12 py-8">
      <Header 
        tag="POLICY & INTEGRATIONS"
        title="Settings & Policy" 
        subtitle="Configure target roles, locations, automation thresholds, and integrations." 
      />

      {savedMessage && (
        <div className="mb-6 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {savedMessage}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Automation Mode Selector */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08]">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-5 h-5 text-[#007BA7]" />
            <h3 className="text-base font-bold text-white">Automation Submission Policy</h3>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            Select how AutoApply handles submissions after generating and validating tailored resumes.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                mode: 'automatic',
                title: 'Automatic Submission',
                desc: 'Submits automatically when match score ≥ threshold and verified qualifications exist.'
              },
              {
                mode: 'approval_required',
                title: 'Approval Required',
                desc: 'Prepares tailored resume and waits for your one-click approval before submitting.'
              },
              {
                mode: 'discovery_only',
                title: 'Discovery Only',
                desc: 'Finds, ranks, and generates tailored resumes without submitting.'
              }
            ].map(item => {
              const isSelected = preferences.automation_mode === item.mode;
              return (
                <div
                  key={item.mode}
                  onClick={() => setPreferences({ ...preferences, automation_mode: item.mode })}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-[#007BA7]/10 border-[#007BA7] shadow-sm' 
                      : 'bg-white/[0.02] border-white/[0.06] hover:border-[#007BA7]/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <h4 className="font-semibold text-sm text-slate-200">{item.title}</h4>
                    <input 
                      type="radio" 
                      name="automation_mode" 
                      checked={isSelected} 
                      onChange={() => {}} 
                      className="accent-[#007BA7]" 
                    />
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Search & Matching Criteria */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08]">
          <div className="flex items-center gap-2 mb-4">
            <Sliders className="w-5 h-5 text-[#007BA7]" />
            <h3 className="text-base font-bold text-white">Search Preferences & Match Limits</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1.5">Target Job Titles (Comma-separated)</label>
              <textarea
                rows={3}
                value={preferences.target_titles.join(', ')}
                onChange={(e) => setPreferences({ 
                  ...preferences, 
                  target_titles: e.target.value.split(',').map(s => s.trim()).filter(Boolean) 
                })}
                className="w-full p-3 bg-white/[0.02] border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:border-[#007BA7] focus:ring-1 focus:ring-[#007BA7]/30 transition-all"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1.5">Preferred Locations (Comma-separated)</label>
              <textarea
                rows={3}
                value={preferences.preferred_locations.join(', ')}
                onChange={(e) => setPreferences({ 
                  ...preferences, 
                  preferred_locations: e.target.value.split(',').map(s => s.trim()).filter(Boolean) 
                })}
                className="w-full p-3 bg-white/[0.02] border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:border-[#007BA7] focus:ring-1 focus:ring-[#007BA7]/30 transition-all"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1.5">
                Minimum Match Score for Auto-Apply: <strong className="text-[#007BA7] font-semibold">{preferences.min_match_score}%</strong>
              </label>
              <input
                type="range"
                min="50"
                max="95"
                step="5"
                value={preferences.min_match_score}
                onChange={(e) => setPreferences({ ...preferences, min_match_score: Number(e.target.value) })}
                className="w-full accent-[#007BA7] cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>50% (Permissive)</span>
                <span className="text-[#007BA7] font-semibold">75% (Recommended)</span>
                <span>95% (Strict)</span>
              </div>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1.5">Notice Period / Availability</label>
              <input
                type="text"
                value="Immediate / 15 days or less"
                readOnly
                className="w-full p-2.5 bg-white/[0.02] border border-white/[0.04] rounded-xl text-slate-400 cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* Integration Status Cards */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08]">
          <h3 className="text-base font-bold text-white mb-4">Connected Integrations</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-[#007BA7]/30 transition-all">
              <div className="flex items-center gap-2 mb-2">
                <Bot className="w-4 h-4 text-[#007BA7]" />
                <span className="font-semibold text-slate-200">Google Gemini</span>
              </div>
              <p className="text-slate-400 text-[11px]">Model: <strong>gemini-3.8-flash</strong></p>
              <span className="text-[10px] text-emerald-400 font-medium mt-2 inline-block">● Authenticated</span>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-[#007BA7]/30 transition-all">
              <div className="flex items-center gap-2 mb-2">
                <Key className="w-4 h-4 text-[#007BA7]" />
                <span className="font-semibold text-slate-200">Apify API</span>
              </div>
              <p className="text-slate-400 text-[11px]">Actor: <strong>Multi-Source Scraper</strong></p>
              <span className="text-[10px] text-emerald-400 font-medium mt-2 inline-block">● Token Configured</span>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-[#007BA7]/30 transition-all">
              <div className="flex items-center gap-2 mb-2">
                <Mail className="w-4 h-4 text-[#007BA7]" />
                <span className="font-semibold text-slate-200">Gmail SMTP</span>
              </div>
              <p className="text-slate-400 text-[11px]">User: <strong>ayushrao786420...</strong></p>
              <span className="text-[10px] text-emerald-400 font-medium mt-2 inline-block">● SMTP Ready</span>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-[#007BA7]/30 transition-all">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-4 h-4 text-[#007BA7]" />
                <span className="font-semibold text-slate-200">ChromaDB</span>
              </div>
              <p className="text-slate-400 text-[11px]">Vector Storage: <strong>./data/chromadb</strong></p>
              <span className="text-[10px] text-emerald-400 font-medium mt-2 inline-block">● 26 Chunks Ingested</span>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#007BA7] hover:bg-[#006e96] text-white text-xs font-semibold shadow-sm transition-all cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>Save Preferences</span>
          </button>
        </div>
      </form>
    </div>
  );
}
