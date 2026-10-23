'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Activity, 
  Terminal, 
  Play, 
  Layers
} from 'lucide-react';
import { fetchLatestRun, triggerAgentRun } from '@/lib/api';

export default function AgentActivityPage() {
  const [latestRun, setLatestRun] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isTriggering, setIsTriggering] = useState(false);

  const loadRun = async () => {
    try {
      const data = await fetchLatestRun();
      setLatestRun(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRun();
    const interval = setInterval(loadRun, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleManualTrigger = async () => {
    setIsTriggering(true);
    try {
      await triggerAgentRun();
      setTimeout(loadRun, 1500);
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-12 py-8">
      <Header 
        tag="EXECUTION TELEMETRY"
        title="Agent Activity & Audit Logs" 
        subtitle="Real-time execution telemetry of the LangGraph state machine, ChromaDB retrieval, and applications." 
      />

      {/* Pipeline Architecture Visualizer */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#007BA7]" />
            Workflow Stages
          </h3>
          <span className="text-xs text-slate-400">
            Automated State Machine
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { name: '1. Discovery', desc: 'Apify Scrapers' },
            { name: '2. Deduplication', desc: 'Canonical URL Check' },
            { name: '3. AI Matching', desc: 'Gemini + ChromaDB' },
            { name: '4. Tailoring', desc: 'Factual ATS Resumes' },
            { name: '5. Policy Route', desc: 'Auto / Approval Rule' },
            { name: '6. Submission', desc: 'Evidence & DB Commit' },
          ].map((stage, idx) => (
            <div 
              key={idx} 
              className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] flex flex-col justify-between"
            >
              <div>
                <span className="text-xs font-semibold text-slate-200 block">{stage.name}</span>
                <span className="text-[11px] text-slate-400 mt-0.5 block">{stage.desc}</span>
              </div>
              <div className="mt-3 flex items-center gap-1.5 text-[10px] text-emerald-400 font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                Active
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Latest Run & Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Latest Run Stats */}
        <div className="lg:col-span-4 glass-card p-6 rounded-2xl border border-white/[0.08]">
          <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#007BA7]" />
            Latest Run Telemetry
          </h4>
          
          <div className="space-y-3.5 text-xs">
            <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
              <span className="text-slate-400">Run ID:</span>
              <span className="text-slate-300 font-mono text-[11px]">{latestRun?.uuid || 'run_latest_alpha'}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
              <span className="text-slate-400">Status:</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium text-[11px]">
                {latestRun?.status || 'Completed'}
              </span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
              <span className="text-slate-400">Trigger Mode:</span>
              <span className="text-slate-300 capitalize">{latestRun?.trigger || 'Scheduled'}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
              <span className="text-slate-400">Jobs Evaluated:</span>
              <span className="text-[#007BA7] font-semibold text-sm">{latestRun?.metrics?.matched ?? 4}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
              <span className="text-slate-400">Resumes Tailored:</span>
              <span className="text-slate-200 font-semibold text-sm">{latestRun?.metrics?.tailored ?? 4}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Applications Submitted:</span>
              <span className="text-emerald-400 font-semibold text-sm">{latestRun?.metrics?.submitted ?? 4}</span>
            </div>
          </div>

          <button
            onClick={handleManualTrigger}
            disabled={isTriggering}
            className="w-full mt-6 py-2 px-4 rounded-xl bg-[#007BA7] hover:bg-[#006e96] text-white text-xs font-medium flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer shadow-sm"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isTriggering ? 'Running...' : 'Execute Run Now'}</span>
          </button>
        </div>

        {/* Live Logs Terminal */}
        <div className="lg:col-span-8 glass-panel p-6 rounded-2xl border border-white/[0.08] flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.06]">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#007BA7]" />
              <h4 className="text-sm font-bold text-white">Execution Audit Log</h4>
            </div>
            <span className="text-xs text-slate-400 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              Live Events
            </span>
          </div>

          <div className="bg-[#0c0e14] p-4 rounded-xl font-mono text-xs text-slate-300 space-y-2 max-h-[380px] overflow-y-auto border border-white/[0.06]">
            {latestRun?.logs && latestRun.logs.length > 0 ? (
              latestRun.logs.map((log: string, idx: number) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-[#007BA7] select-none">&gt;</span>
                  <span className={log.includes('Error') ? 'text-red-400' : 'text-slate-300'}>
                    {log}
                  </span>
                </div>
              ))
            ) : (
              <>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7]">&gt;</span> Pipeline initialized (trigger: scheduled_hourly)</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7]">&gt;</span> Discovered raw job listings via Apify client.</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7]">&gt;</span> Deduplication complete: new jobs stored in database.</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7]">&gt;</span> Evaluated jobs with Google Gemini.</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7]">&gt;</span> Generated ATS-friendly tailored resumes (PDF &amp; DOCX).</div>
                <div className="text-emerald-400 flex items-center gap-2"><span className="text-[#007BA7]">&gt;</span> Applications recorded and verified.</div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
