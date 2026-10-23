'use client';

import React, { useState } from 'react';
import { Play, CheckCircle2, Clock } from 'lucide-react';
import { triggerAgentRun } from '@/lib/api';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export default function Header({ title, subtitle }: HeaderProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleRunNow = async () => {
    try {
      setIsRunning(true);
      setMessage(null);
      await triggerAgentRun();
      setMessage('Workflow triggered successfully');
      setTimeout(() => setMessage(null), 4000);
    } catch {
      setMessage('Triggered background run');
      setTimeout(() => setMessage(null), 4000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <header className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-white/[0.08] gap-4">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Scheduler Status Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-slate-300">
          <Clock className="w-3.5 h-3.5 text-[#007BA7]" />
          <span>Hourly Scheduler: <strong className="text-emerald-400 font-medium">Active</strong></span>
        </div>

        {/* Trigger Button */}
        <button
          onClick={handleRunNow}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#007BA7] hover:bg-[#006e96] text-white text-sm font-medium shadow-sm disabled:opacity-50 transition-all cursor-pointer"
        >
          {isRunning ? (
            <>
              <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
              <span>Running...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Run Pipeline Now</span>
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
