'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Briefcase, 
  FileText, 
  Send, 
  Activity, 
  Settings,
  Sparkles,
  Bot
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Job Discovery', href: '/jobs', icon: Briefcase },
  { name: 'Resume Studio', href: '/resumes', icon: FileText },
  { name: 'Application Tracker', href: '/applications', icon: Send },
  { name: 'Agent Activity', href: '/agent', icon: Activity },
  { name: 'Settings & Policy', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between h-screen fixed left-0 top-0 z-30">
      <div>
        {/* Brand */}
        <div className="p-6 border-b border-slate-800/60 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
              Auto-Apply
              <span className="text-[10px] bg-indigo-500/20 text-indigo-300 font-semibold px-1.5 py-0.5 rounded border border-indigo-500/30">AI</span>
            </h1>
            <p className="text-xs text-slate-400">Agentic Career Engine</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md shadow-indigo-600/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4.5 h-4.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Candidate Footer */}
      <div className="p-4 border-t border-slate-800/60 m-3 rounded-xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-slate-800 border border-indigo-500/40 flex items-center justify-center text-indigo-400 font-semibold text-sm">
            AR
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-semibold text-slate-200 truncate">Ayush Rao</p>
            <p className="text-xs text-emerald-400 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Auto-Apply Active
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
