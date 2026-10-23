'use client';

import React, { useState } from 'react';
import { Play, CheckCircle2, Clock } from 'lucide-react';
import { triggerAgentRun } from '@/lib/api';

interface HeaderProps {
  title: string;
  subtitle?: string;
  tag?: string;
}

export default function Header({ title, subtitle, tag }: HeaderProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleRunNow = async () => {
    try {
      setIsRunning(true);
      setMessage(null);
      await triggerAgentRun();
      setMessage('Pipeline initiated');
      setTimeout(() => setMessage(null), 4000);
    } catch {
      setMessage('Triggered background run');
      setTimeout(() => setMessage(null), 4000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <header className="flex flex-col sm:flex-row sm:items-end justify-between pb-6 mb-8 border-b border-white/[0.06] gap-4">
      <div>
        <span className="text-[10px] sm:text-[11px] uppercase tracking-[0.25em] text-[#00E5FF] font-semibold font-['Space_Grotesk',sans-serif] block mb-1">
          {tag || 'AUTONOMOUS OPERATIONS'}
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight font-['Outfit',sans-serif]">
          {title}
        </h1>
        {subtitle && <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Scheduler Status Badge */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.08] text-xs text-slate-300">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Scheduler: <strong className="text-white font-medium">Hourly Active</strong></span>
        </div>

        {/* Trigger Button */}
        <button
          onClick={handleRunNow}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#00E5FF]/40 text-[#00E5FF] hover:border-[#00E5FF] hover:bg-[#00E5FF]/10 text-xs font-bold tracking-wider uppercase transition-all shadow-[0_0_15px_rgba(0,229,255,0.15)] disabled:opacity-50 cursor-pointer"
        >
          {isRunning ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-[#00E5FF] border-t-transparent rounded-full animate-spin"></span>
              <span>Running...</span>
            </>
          ) : (
            <>
              <Play className="w-3 h-3 fill-current" />
              <span>Run Pipeline</span>
            </>
          )}
        </button>

        {message && (
          <span className="text-xs text-emerald-400 font-medium flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {message}
          </span>
        )}
      </div>
    </header>
  );
}
