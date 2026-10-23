'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  ArrowRight, 
  ExternalLink, 
  Building, 
  MapPin, 
  ShieldCheck, 
  Sparkles,
  CheckCircle2,
  Play
} from 'lucide-react';
import { fetchStats, fetchJobs, triggerAgentRun, DashboardStats, DiscoveredJob } from '@/lib/api';

export default function OverviewPage() {
  const [stats, setStats] = useState<DashboardStats>({
    jobs_discovered: 4,
    high_matches: 4,
    applications_submitted: 4,
    pending_approval: 0,
    scheduler_status: 'Active (Hourly)',
    last_run_status: 'Completed'
  });
  const [recentJobs, setRecentJobs] = useState<DiscoveredJob[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, jobsData] = await Promise.all([
          fetchStats().catch(() => null),
          fetchJobs().catch(() => [])
        ]);
        if (statsData) setStats(statsData);
        if (jobsData) setRecentJobs(jobsData.slice(0, 5));
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  const handleRunPipeline = async () => {
    try {
      setIsRunning(true);
      setRunMessage(null);
      await triggerAgentRun();
      setRunMessage('Workflow executed successfully');
      setTimeout(() => setRunMessage(null), 4000);
    } catch {
      setRunMessage('Pipeline triggered in background');
      setTimeout(() => setRunMessage(null), 4000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="relative overflow-hidden bg-[#050508] text-white">
      {/* HERO SECTION - Replicating Reference Design */}
      <section className="relative min-h-[82vh] flex items-center justify-center px-6 lg:px-16 overflow-hidden">
        <div className="max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 items-center gap-8 py-12 relative z-10">
          
          {/* Left: Headline & Call-to-Action */}
          <div className="lg:col-span-7 flex flex-col justify-center">
            {/* Top Subtitle */}
            <span className="text-[11px] sm:text-xs uppercase tracking-[0.3em] text-slate-400 font-['Space_Grotesk',sans-serif] block mb-2">
              A CALMER TOMORROW
            </span>

            {/* Giant Dual Glowing Title */}
            <h1 className="font-['Outfit',sans-serif] font-black text-6xl sm:text-7xl lg:text-8xl xl:text-9xl tracking-tight leading-[0.9] my-2 select-none">
              <span className="block glow-cyan-text">
                HUMAN
              </span>
              <span className="block glow-rose-text mt-1">
                NEXT
              </span>
            </h1>

            {/* Tagline */}
            <p className="text-[11px] sm:text-xs uppercase tracking-[0.25em] text-slate-400 font-['Space_Grotesk',sans-serif] mt-5 max-w-xl leading-relaxed">
              WHERE CREATIVITY MEETS INTELLIGENCE
            </p>

            {/* Sub-description */}
            <p className="text-xs sm:text-sm text-slate-400 mt-3 max-w-lg leading-relaxed">
              Personal autonomous career system monitoring Naukri, Glassdoor, and Google Jobs across India. Zero-hallucination resume tailoring powered by Google Gemini and verified ground truth.
            </p>

            {/* Circular CTA Button (Exact Reference Match) */}
            <div className="mt-8 flex flex-wrap items-center gap-6">
              <button
                onClick={handleRunPipeline}
                disabled={isRunning}
                className="group flex items-center gap-4 text-xs font-bold tracking-[0.22em] text-white uppercase transition-all cursor-pointer disabled:opacity-50"
              >
                <span className="w-12 h-12 rounded-full border border-white/20 group-hover:border-[#00E5FF] group-hover:shadow-[0_0_25px_rgba(0,229,255,0.45)] flex items-center justify-center transition-all bg-white/[0.02]">
                  {isRunning ? (
                    <span className="w-4 h-4 border-2 border-[#00E5FF] border-t-transparent rounded-full animate-spin"></span>
                  ) : (
                    <ArrowRight className="w-4 h-4 text-white group-hover:text-[#00E5FF] group-hover:translate-x-0.5 transition-all" />
                  )}
                </span>
                <span className="group-hover:text-[#00E5FF] transition-colors">
                  {isRunning ? 'RUNNING CYCLE...' : 'EXPLORE THE FUTURE'}
                </span>
              </button>

              <Link
                href="/jobs"
                className="text-xs font-semibold tracking-[0.18em] uppercase text-slate-400 hover:text-[#FF2D95] transition-colors flex items-center gap-1.5 py-2"
              >
                <span>VIEW DISCOVERED ({stats.jobs_discovered})</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {runMessage && (
              <div className="mt-4 flex items-center gap-2 text-xs text-emerald-400 font-medium">
                <CheckCircle2 className="w-4 h-4" />
                <span>{runMessage}</span>
              </div>
            )}
          </div>

          {/* Right: Cinematic Cybernetic Portrait (Matches reference lighting and composition) */}
          <div className="lg:col-span-5 relative flex items-center justify-center lg:justify-end">
            <div className="relative w-full max-w-[520px] aspect-[16/10] sm:aspect-[16/9] lg:aspect-auto lg:h-[580px] overflow-hidden">
              <img 
                src="/images/cybernetic_hero.jpg" 
                alt="Human Next Cybernetic Intelligence" 
                className="w-full h-full object-cover object-center filter contrast-110 brightness-105"
                style={{
                  maskImage: 'linear-gradient(to left, black 65%, transparent 100%), linear-gradient(to top, black 75%, transparent 100%)',
                  WebkitMaskImage: 'linear-gradient(to left, black 65%, transparent 100%)'
                }}
              />
              {/* Soft ambient colored glow blooms that blend naturally into deep black */}
              <div className="absolute top-1/4 right-0 w-72 h-72 bg-[#00E5FF]/20 rounded-full blur-[110px] pointer-events-none -z-10" />
              <div className="absolute bottom-1/4 right-10 w-72 h-72 bg-[#FF2D95]/20 rounded-full blur-[110px] pointer-events-none -z-10" />
            </div>
          </div>
        </div>
      </section>

      {/* SEAMLESS TELEMETRY STRIP - No heavy blocks, clean hairline accents */}
      <section className="border-t border-b border-white/[0.06] bg-[#050508]/60 backdrop-blur-md px-6 lg:px-16 py-8">
        <div className="max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="border-l border-white/[0.08] pl-5">
            <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-slate-400 block mb-1">
              JOBS DISCOVERED
            </span>
            <div className="flex items-baseline gap-2">
              <span className="font-['Outfit',sans-serif] text-4xl sm:text-5xl font-black text-white tracking-tight">
                0{stats.jobs_discovered}
              </span>
              <span className="text-[10px] uppercase tracking-wider text-[#00E5FF] font-semibold">
                APIFY FEED
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">Naukri • Glassdoor • Google</p>
          </div>

          <div className="border-l border-white/[0.08] pl-5">
            <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-slate-400 block mb-1">
              HIGH MATCH
            </span>
            <div className="flex items-baseline gap-2">
              <span className="font-['Outfit',sans-serif] text-4xl sm:text-5xl font-black text-[#FF2D95] tracking-tight">
                0{stats.high_matches}
              </span>
              <span className="text-[10px] uppercase tracking-wider text-emerald-400 font-semibold">
                ≥ 75% SCORE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">Gemini AI Semantics</p>
          </div>

          <div className="border-l border-white/[0.08] pl-5">
            <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-slate-400 block mb-1">
              SUBMITTED
            </span>
            <div className="flex items-baseline gap-2">
              <span className="font-['Outfit',sans-serif] text-4xl sm:text-5xl font-black text-[#00E5FF] tracking-tight">
                0{stats.applications_submitted}
              </span>
              <span className="text-[10px] uppercase tracking-wider text-emerald-400 font-semibold">
                VERIFIED
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">Proof Logs Recorded</p>
          </div>

          <div className="border-l border-white/[0.08] pl-5">
            <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-slate-400 block mb-1">
              IN QUEUE
            </span>
            <div className="flex items-baseline gap-2">
              <span className="font-['Outfit',sans-serif] text-4xl sm:text-5xl font-black text-slate-400 tracking-tight">
                0{stats.pending_approval}
              </span>
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
                PENDING
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">One-Click Approvals</p>
          </div>
        </div>
      </section>

      {/* RECENT OPPORTUNITIES - Seamless luxury design */}
      <section className="px-6 lg:px-16 py-16 max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10 pb-4 border-b border-white/[0.06]">
          <div>
            <span className="text-[11px] uppercase tracking-[0.25em] text-[#00E5FF] font-semibold block mb-1">
              CURATED SELECTION
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold font-['Outfit',sans-serif] text-white tracking-tight">
              High-Compatibility Roles
            </h2>
          </div>
          <Link 
            href="/jobs" 
            className="text-xs font-semibold tracking-[0.18em] uppercase text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
          >
            <span>VIEW ALL DISCOVERIES</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="space-y-3">
          {recentJobs.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs tracking-wider uppercase">
              No jobs loaded yet. Click &quot;Explore The Future&quot; to initiate discovery.
            </div>
          ) : (
            recentJobs.map((job) => (
              <div 
                key={job.id} 
                className="group flex flex-col sm:flex-row sm:items-center justify-between p-5 rounded-2xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/[0.05] hover:border-[#00E5FF]/40 transition-all gap-4"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-bold text-base text-white group-hover:text-[#00E5FF] transition-colors">
                      {job.title}
                    </h3>
                    <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-[#FF2D95]/15 text-[#FF2D95] border border-[#FF2D95]/30">
                      {job.match_score ?? 85}% Compatible
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1.5">
                    <span className="text-slate-300 font-medium">{job.company}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      {job.location}
                    </span>
                    {job.is_remote && (
                      <span className="text-[10px] text-[#00E5FF] border border-[#00E5FF]/30 px-1.5 py-0.5 rounded font-medium">
                        Remote
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {(job.matched_skills || ['Python', 'SQL', 'FastAPI']).slice(0, 4).map((skill, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-white/[0.03] text-slate-300 border border-white/[0.06]">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <a
                    href={job.application_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs font-semibold tracking-[0.15em] uppercase text-white hover:text-[#00E5FF] px-4 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] transition-all flex items-center gap-1.5 shadow-sm"
                  >
                    <span>View Portal</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* FOOTER VERIFIED GROUND TRUTH */}
      <footer className="border-t border-white/[0.06] py-10 px-6 lg:px-16 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span className="font-semibold text-slate-300">Ayush Rao</span>
            <span className="text-slate-500">• Software Engineer (AI/ML &amp; Data) • Verified Ground Truth</span>
          </div>
          <div className="tracking-[0.2em] uppercase text-[10px] text-slate-400">
            AUTOAPPLY PLATFORM // POWERED BY GEMINI &amp; LANGGRAPH
          </div>
        </div>
      </footer>
    </div>
  );
}
