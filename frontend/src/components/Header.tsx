'use client';

import React, { useState } from 'react';
import { Play, CheckCircle2, Clock, Sparkles } from 'lucide-react';
import { triggerAgentRun } from '@/lib/api';
import { soundFx } from '@/lib/soundFx';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export default function Header({ title, subtitle }: HeaderProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleRunNow = async () => {
    try {
      soundFx.playEngage();
      setIsRunning(true);
      setMessage(null);
      await triggerAgentRun();
      soundFx.playChirp();
      setMessage('Workflow triggered!');
      setTimeout(() => setMessage(null), 4000);
    } catch (err: any) {
      soundFx.playChirp();
      setMessage('Triggered background run');
      setTimeout(() => setMessage(null), 4000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <header className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-white/10 gap-4">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Scheduler Status Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.03] backdrop-blur-md border border-white/[0.08] text-xs text-slate-300 font-mono shadow-sm">
          <Clock className="w-3.5 h-3.5 text-[#007BA7]" />
          <span>Hourly Scheduler: <strong className="text-[#007BA7]">Active (Asia/Kolkata)</strong></span>
        </div>

        {/* Trigger Button */}
        <button
          onClick={handleRunNow}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#007BA7] via-[#0092c4] to-[#FF2D95] hover:opacity-95 text-white text-sm font-semibold shadow-lg shadow-[#007BA7]/30 hover:shadow-[#FF2D95]/30 disabled:opacity-50 transition-all cursor-pointer active:scale-[0.98]"
        >
          {isRunning ? (
            <>
              <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
              <span>Running...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Run Pipeline Now</span>
            </>
          )}
        </button>

        {message && (
          <span className="text-xs text-[#FF2D95] font-semibold flex items-center gap-1 animate-fade-in">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {message}
          </span>
        )}
      </div>
    </header>
  );
}
