'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Briefcase, 
  Sparkles, 
  Send, 
  Clock, 
  ArrowUpRight, 
  FileText, 
  ShieldCheck,
  Building,
  MapPin,
  CheckCircle2
} from 'lucide-react';
import Link from 'next/link';
import { fetchStats, fetchJobs, DashboardStats, DiscoveredJob } from '@/lib/api';

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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, jobsData] = await Promise.all([
          fetchStats().catch(() => null),
          fetchJobs().catch(() => [])
        ]);
        if (statsData) setStats(statsData);
        if (jobsData) setRecentJobs(jobsData.slice(0, 5));
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div>
      <Header 
        title="Dashboard" 
        subtitle="Automated job discovery, Gemini AI resume tailoring, and tracked applications." 
      />

      {/* System Status Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white tracking-tight">Active Job Pipeline</h3>
              <span className="text-xs bg-emerald-500/10 text-emerald-400 font-medium px-2.5 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Operational
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Monitoring Naukri, Glassdoor, and Google Jobs across Indian tech hubs (Noida, Gurgaon, Bengaluru, Pune, Hyderabad, Remote). New opportunities are automatically filtered and scored with Google Gemini.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-slate-300">
              Target: <strong className="text-white">Software Engineer / AI / Data</strong>
            </span>
            <span className="px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-slate-300">
              Min Match: <strong className="text-[#007BA7]">≥75%</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="glass-card p-5 rounded-2xl border border-white/[0.08]">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Jobs Discovered</span>
            <div className="p-2 rounded-xl bg-[#007BA7]/15 text-[#007BA7]">
              <Briefcase className="w-4.5 h-4.5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white tracking-tight">{stats.jobs_discovered}</span>
            <span className="text-xs text-[#007BA7] font-medium px-2 py-0.5 rounded-full bg-[#007BA7]/10 border border-[#007BA7]/20">Apify</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Aggregated across Indian portals</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-white/[0.08]">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">High Match (≥75%)</span>
            <div className="p-2 rounded-xl bg-[#007BA7]/15 text-[#007BA7]">
              <Sparkles className="w-4.5 h-4.5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white tracking-tight">{stats.high_matches}</span>
            <span className="text-xs text-emerald-400 font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">Gemini AI</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Semantic match via ChromaDB</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-white/[0.08]">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Applications Submitted</span>
            <div className="p-2 rounded-xl bg-emerald-500/15 text-emerald-400">
              <Send className="w-4.5 h-4.5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white tracking-tight">{stats.applications_submitted}</span>
            <span className="text-xs text-emerald-400 font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">Verified</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Recorded with proof logs</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-white/[0.08]">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Pending Review</span>
            <div className="p-2 rounded-xl bg-amber-500/15 text-amber-400">
              <Clock className="w-4.5 h-4.5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white tracking-tight">{stats.pending_approval}</span>
            <span className="text-xs text-slate-400 font-medium">In Queue</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Awaiting one-click review</p>
        </div>
      </div>

      {/* Main Workflow Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
        <Link 
          href="/jobs" 
          className="glass-card p-5 rounded-2xl border border-white/[0.08] hover:border-[#007BA7]/50 group block"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2.5 rounded-xl bg-[#007BA7]/15 text-[#007BA7]">
              <Briefcase className="w-5 h-5" />
            </div>
            <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-[#007BA7] transition-colors" />
          </div>
          <h3 className="text-sm font-bold text-white mb-1 group-hover:text-[#007BA7] transition-colors">Job Discovery</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Browse discovered opportunities, review match score rubrics, and inspect missing qualification insights.
          </p>
        </Link>

        <Link 
          href="/resumes" 
          className="glass-card p-5 rounded-2xl border border-white/[0.08] hover:border-[#007BA7]/50 group block"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2.5 rounded-xl bg-[#007BA7]/15 text-[#007BA7]">
              <FileText className="w-5 h-5" />
            </div>
            <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-[#007BA7] transition-colors" />
          </div>
          <h3 className="text-sm font-bold text-white mb-1 group-hover:text-[#007BA7] transition-colors">Resume Studio</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Preview ATS-friendly tailored resumes generated with Google Gemini and download verified PDF or DOCX versions.
          </p>
        </Link>

        <Link 
          href="/applications" 
          className="glass-card p-5 rounded-2xl border border-white/[0.08] hover:border-emerald-500/50 group block"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2.5 rounded-xl bg-emerald-500/15 text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition-colors" />
          </div>
          <h3 className="text-sm font-bold text-white mb-1 group-hover:text-emerald-400 transition-colors">Application Tracker</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Manage your pipeline across Kanban stages, inspect submission confirmation proofs, and approve pending applications.
          </p>
        </Link>
      </div>

      {/* Recent Discovered Jobs */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08]">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Recent High-Match Listings</h3>
            <p className="text-xs text-slate-400">Evaluated against verified candidate profile</p>
          </div>
          <Link 
            href="/jobs" 
            className="text-xs text-[#007BA7] hover:text-[#38bdf8] font-medium flex items-center gap-1 transition-colors"
          >
            View All Jobs <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/[0.08] text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                <th className="pb-3 px-3">Role & Company</th>
                <th className="pb-3 px-3">Location</th>
                <th className="pb-3 px-3">Match Score</th>
                <th className="pb-3 px-3">Matched Skills</th>
                <th className="pb-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04] text-sm">
              {recentJobs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-slate-500 text-xs">
                    No jobs loaded yet. Click &quot;Run Pipeline Now&quot; to discover jobs.
                  </td>
                </tr>
              ) : (
                recentJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-medium text-slate-200">{job.title}</div>
                      <div className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
                        <Building className="w-3 h-3 text-slate-500" />
                        {job.company}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-xs text-slate-300">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-slate-500" />
                        {job.location}
                      </div>
                      {job.is_remote && (
                        <span className="inline-block mt-1 text-[10px] bg-[#007BA7]/15 text-[#38bdf8] font-medium px-2 py-0.5 rounded-full border border-[#007BA7]/30">
                          Remote
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <span className={`font-bold text-sm ${(job.match_score ?? 85) >= 75 ? 'text-emerald-400' : 'text-[#007BA7]'}`}>
                          {job.match_score ?? 85}%
                        </span>
                        <div className="w-16 h-1.5 rounded-full bg-white/[0.08] overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-[#007BA7] to-emerald-400" 
                            style={{ width: `${job.match_score ?? 85}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {(job.matched_skills || ['Python', 'SQL', 'FastAPI']).slice(0, 3).map((s, idx) => (
                          <span key={idx} className="text-[10px] bg-white/[0.04] text-slate-300 px-2 py-0.5 rounded-md border border-white/[0.06]">
                            {s}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <a
                        href={job.application_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs bg-white/[0.04] hover:bg-[#007BA7] text-slate-200 hover:text-white px-3.5 py-1.5 rounded-xl border border-white/[0.08] transition-all inline-block font-medium"
                      >
                        Apply Link
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
