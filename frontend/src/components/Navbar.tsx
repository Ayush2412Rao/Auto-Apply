'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Menu, X, ArrowUpRight } from 'lucide-react';
import { triggerAgentRun } from '@/lib/api';

const NAV_LINKS = [
  { name: 'EXPLORE', href: '/' },
  { name: 'DISCOVERY', href: '/jobs' },
  { name: 'RESUMES', href: '/resumes' },
  { name: 'TRACKER', href: '/applications' },
  { name: 'INTELLIGENCE', href: '/agent' },
  { name: 'SETTINGS', href: '/settings' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const handleRun = async () => {
    try {
      setIsRunning(true);
      setMsg(null);
      await triggerAgentRun();
      setMsg('RUNNING');
      setTimeout(() => setMsg(null), 3000);
    } catch {
      setMsg('TRIGGERED');
      setTimeout(() => setMsg(null), 3000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#050508]/80 backdrop-blur-xl border-b border-white/[0.06]">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 h-20 flex items-center justify-between">
        {/* Left: Minimal Hamburger + Brand */}
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setMobileOpen(!mobileOpen)}
            className="text-white hover:text-[#00E5FF] transition-colors p-1 md:hidden"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <Link href="/" className="flex items-center gap-2.5 group">
            <span className="w-2 h-2 rounded-full bg-[#00E5FF] shadow-[0_0_12px_#00E5FF]"></span>
            <span className="font-extrabold text-sm sm:text-base tracking-[0.25em] text-white uppercase font-['Outfit',sans-serif]">
              AUTO<span className="text-[#FF2D95]">//</span>APPLY
            </span>
          </Link>
        </div>

        {/* Center Navigation Links (Matching reference screenshot) */}
        <div className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`text-[11px] font-semibold tracking-[0.22em] transition-all relative py-1 ${
                  isActive
                    ? 'text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {link.name}
                {isActive && (
                  <span className="absolute -bottom-1 left-0 right-0 h-[2px] bg-gradient-to-r from-[#00E5FF] to-[#FF2D95] shadow-[0_0_8px_#00E5FF]"></span>
                )}
              </Link>
            );
          })}
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-4">
          <Link 
            href="/jobs" 
            className="text-slate-400 hover:text-[#00E5FF] transition-colors p-1.5"
            title="Search Jobs"
          >
            <Search className="w-4 h-4" />
          </Link>

          <button
            onClick={handleRun}
            disabled={isRunning}
            className="hidden sm:flex items-center gap-2 text-[10px] font-bold tracking-[0.2em] uppercase px-4 py-2 rounded-full border border-[#00E5FF]/40 text-[#00E5FF] hover:border-[#00E5FF] hover:bg-[#00E5FF]/10 transition-all shadow-[0_0_15px_rgba(0,229,255,0.15)] disabled:opacity-50 cursor-pointer"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] animate-pulse"></span>
            <span>{isRunning ? 'PIPELINE ACTIVE' : msg || 'RUN PIPELINE'}</span>
          </button>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileOpen && (
        <div className="md:hidden border-t border-white/[0.06] bg-[#050508]/95 px-6 py-4 space-y-3">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className="block text-xs font-semibold tracking-[0.2em] text-slate-300 hover:text-white py-2"
            >
              {link.name}
            </Link>
          ))}
          <div className="pt-2">
            <button
              onClick={handleRun}
              disabled={isRunning}
              className="w-full text-center text-[10px] font-bold tracking-[0.2em] uppercase py-2.5 rounded-full border border-[#00E5FF]/40 text-[#00E5FF]"
            >
              {isRunning ? 'PIPELINE ACTIVE' : 'RUN PIPELINE'}
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
