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
    <aside className="w-64 glass-panel border-r border-white/10 flex flex-col justify-between h-screen fixed left-0 top-0 z-30 bg-[#0A0A0A]/90">
      <div>
        {/* Brand */}
        <div className="p-6 border-b border-white/10 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#007BA7] to-[#FF2D95] flex items-center justify-center shadow-lg shadow-[#007BA7]/30">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
              Auto-Apply
              <span className="text-[10px] bg-[#FF2D95]/15 text-[#FF2D95] font-extrabold px-1.5 py-0.5 rounded border border-[#FF2D95]/30">AI</span>
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
                className={`group flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-[#007BA7] to-[#005c7d] text-white shadow-lg shadow-[#007BA7]/25 border-l-4 border-[#FF2D95]'
                    : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
                }`}
              >
                <Icon className={`w-4.5 h-4.5 transition-colors ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-[#007BA7]'}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Candidate Footer */}
      <div className="p-4 m-3 rounded-2xl bg-[#121216] border border-white/10 shadow-inner">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-[#181820] border border-[#007BA7]/50 flex items-center justify-center text-[#007BA7] font-bold text-sm shadow-sm">
            AR
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-semibold text-slate-200 truncate">Ayush Rao</p>
            <p className="text-xs text-[#FF2D95] flex items-center gap-1.5 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-[#FF2D95] animate-pulse"></span>
              Auto-Apply Active
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
