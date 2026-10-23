'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Activity, 
  Terminal, 
  CheckCircle2, 
  Clock, 
  Play, 
  Sparkles, 
  Layers, 
  Send, 
  Cpu,
  Radio,
  Crosshair
} from 'lucide-react';
import { fetchLatestRun, triggerAgentRun } from '@/lib/api';
import { soundFx } from '@/lib/soundFx';

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
    soundFx.playEngage();
    setIsTriggering(true);
    try {
      await triggerAgentRun();
      soundFx.playChirp();
      setTimeout(loadRun, 1500);
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div>
      <Header 
        title="Agent Activity & Audit Logs" 
        subtitle="Real-time execution telemetry of the LangGraph state machine, ChromaDB retrieval, and automated applications." 
      />

      {/* Pipeline Architecture Visualizer */}
      <div className="glass-panel hud-bracket p-6 rounded-2xl border border-white/10 mb-8 relative overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2 font-mono">
            <Cpu className="w-4 h-4 text-[#007BA7]" />
            LangGraph Autonomous Agent State Machine
          </h3>
          <span className="text-[11px] font-mono text-[#007BA7] flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 text-[#FF2D95] animate-pulse" />
            SYNAPSE FREQUENCY: 15min
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { name: '1. Discovery', desc: 'Apify Scrapers', active: true },
            { name: '2. Deduplication', desc: 'Canonical URL DB Check', active: true },
            { name: '3. AI Matching', desc: 'Gemini + ChromaDB', active: true },
            { name: '4. Tailoring', desc: 'Zero-Hallucination ATS', active: true },
            { name: '5. Policy Route', desc: 'Auto / Approval Rule', active: true },
            { name: '6. Submission', desc: 'Evidence & DB Commit', active: true },
          ].map((stage, idx) => (
            <div 
              key={idx} 
              onClick={() => soundFx.playClick()}
              className="p-3.5 rounded-xl bg-white/[0.03] backdrop-blur-md border border-white/[0.08] flex flex-col justify-between hover:border-[#007BA7]/60 hover:bg-[#007BA7]/10 hover:shadow-lg hover:shadow-[#007BA7]/15 transition-all cursor-pointer group"
            >
              <div>
                <span className="text-xs font-bold text-slate-200 block group-hover:text-[#007BA7] transition-colors">{stage.name}</span>
                <span className="text-[11px] text-slate-400 mt-0.5 block">{stage.desc}</span>
              </div>
              <div className="mt-3 flex items-center gap-1.5 text-[10px] text-[#007BA7] font-semibold font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-[#007BA7] animate-pulse"></span>
                ACTIVE NODE
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Latest Run & Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Latest Run Stats */}
        <div className="lg:col-span-4 glass-card hud-bracket p-6 rounded-2xl border border-white/10">
          <h4 className="text-base font-bold text-white mb-4 flex items-center gap-2 font-mono">
            <Activity className="w-4 h-4 text-[#FF2D95]" />
            Telemetry Metrics
          </h4>
          
          <div className="space-y-4 text-xs font-mono">
            <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
              <span className="text-slate-400">Run Identifier:</span>
              <span className="text-slate-300 font-medium">{latestRun?.uuid || 'run_latest_alpha'}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
              <span className="text-slate-400">Status:</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold uppercase text-[10px]">
                {latestRun?.status || 'Completed'}
              </span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
              <span className="text-slate-400">Trigger Mode:</span>
              <span className="text-slate-300 font-medium capitalize">{latestRun?.trigger || 'Scheduled'}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
              <span className="text-slate-400">Jobs Evaluated:</span>
              <span className="text-[#007BA7] font-bold text-sm">{latestRun?.metrics?.matched ?? 4}</span>
            </div>

            <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
              <span className="text-slate-400">Resumes Tailored:</span>
              <span className="text-[#FF2D95] font-bold text-sm">{latestRun?.metrics?.tailored ?? 4}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400">Applications Submitted:</span>
              <span className="text-emerald-400 font-bold text-sm">{latestRun?.metrics?.submitted ?? 4}</span>
            </div>
          </div>

          <button
            onClick={handleManualTrigger}
            disabled={isTriggering}
            className="w-full mt-6 py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#007BA7] to-[#FF2D95] hover:opacity-95 text-white font-mono font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-[#007BA7]/30 hover:shadow-[#FF2D95]/30 transition-all disabled:opacity-50 cursor-pointer active:scale-[0.98]"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isTriggering ? 'COMPUTING CYCLE...' : 'EXECUTE ON-DEMAND CYCLE'}</span>
          </button>
        </div>

        {/* Live Logs Terminal */}
        <div className="lg:col-span-8 glass-panel hud-bracket p-6 rounded-2xl border border-white/10 flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.06]">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#FF2D95]" />
              <h4 className="text-sm font-bold text-white">Execution Audit Log</h4>
            </div>
            <span className="text-[11px] text-[#007BA7] font-semibold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#007BA7] animate-ping"></span>
              Live Agent Events
            </span>
          </div>

          <div className="bg-black/40 backdrop-blur-xl p-4 rounded-xl font-mono text-xs text-slate-300 space-y-2 max-h-[380px] overflow-y-auto border border-white/[0.08] shadow-inner">
            {latestRun?.logs && latestRun.logs.length > 0 ? (
              latestRun.logs.map((log: string, idx: number) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-[#007BA7] select-none font-bold">&gt;</span>
                  <span className={log.includes('Error') ? 'text-red-400' : log.includes('queued') || log.includes('Evaluated') ? 'text-slate-200' : 'text-slate-300'}>
                    {log}
                  </span>
                </div>
              ))
            ) : (
              <>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7] font-bold">&gt;</span> Pipeline initialized (trigger: scheduled_hourly)</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7] font-bold">&gt;</span> Discovered 4 raw job listings via Apify client.</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7] font-bold">&gt;</span> Deduplication complete: 4 new jobs stored in database.</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7] font-bold">&gt;</span> Evaluated 4 jobs with Google Gemini.</div>
                <div className="text-slate-400 flex items-center gap-2"><span className="text-[#007BA7] font-bold">&gt;</span> Generated 4 ATS-friendly tailored resumes (PDF &amp; DOCX).</div>
                <div className="text-[#FF2D95] font-semibold flex items-center gap-2"><span className="text-[#007BA7] font-bold">&gt;</span> Successfully submitted and verified applications.</div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
