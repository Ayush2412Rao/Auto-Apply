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
  Sparkles
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
    <aside className="w-64 border-r border-white/[0.08] flex flex-col justify-between h-screen fixed left-0 top-0 z-30 bg-[#0C0E14] shadow-xl">
      <div>
        {/* Brand */}
        <div className="p-6 border-b border-white/[0.08] flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#007BA7] to-[#0092c4] flex items-center justify-center text-white shadow-md shadow-[#007BA7]/25 shrink-0">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-base text-white tracking-tight">AutoApply</h1>
            <p className="text-[11px] text-slate-400">Career Intelligence</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[#007BA7]/15 text-[#38bdf8] font-semibold border-l-2 border-[#007BA7]'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-white/[0.04]'
                }`}
              >
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-[#38bdf8]' : 'text-slate-400 group-hover:text-slate-200'}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User Footer */}
      <div className="p-4 m-3 rounded-xl bg-white/[0.02] border border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-white/[0.06] border border-white/10 flex items-center justify-center text-slate-200 font-semibold text-xs shrink-0">
            AR
          </div>
          <div className="overflow-hidden">
            <p className="text-xs font-semibold text-slate-200 truncate">Ayush Rao</p>
            <p className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span>Active Profile</span>
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
