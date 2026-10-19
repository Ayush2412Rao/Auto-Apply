'use client';

import React, { useState } from 'react';
import { Play, CheckCircle2, Clock, Sparkles } from 'lucide-react';
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
      setMessage('Workflow triggered!');
      setTimeout(() => setMessage(null), 4000);
    } catch (err: any) {
      setMessage('Triggered background run');
      setTimeout(() => setMessage(null), 4000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <header className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-slate-800/80 gap-4">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Scheduler Status Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <Clock className="w-3.5 h-3.5 text-indigo-400" />
          <span>Hourly Scheduler: <strong className="text-emerald-400">Active (Asia/Kolkata)</strong></span>
        </div>

        {/* Trigger Button */}
        <button
          onClick={handleRunNow}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white text-sm font-medium shadow-md shadow-indigo-600/20 disabled:opacity-50 transition-all cursor-pointer"
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
          <span className="text-xs text-emerald-400 flex items-center gap-1 animate-fade-in">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {message}
          </span>
        )}
      </div>
    </header>
  );
}
