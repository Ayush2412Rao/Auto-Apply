'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Briefcase, 
  Sparkles, 
  Send, 
  Clock, 
  ArrowUpRight, 
  CheckCircle, 
  FileText, 
  ShieldCheck,
  Building,
  MapPin
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
        title="Agentic Operations Dashboard" 
        subtitle="Real-time monitoring of your automated career discovery, Gemini AI matching, and verified applications." 
      />

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Jobs Discovered</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
              <Briefcase className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{stats.jobs_discovered}</span>
            <span className="text-xs text-emerald-400 font-medium">via Apify</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Aggregated across LinkedIn & Indeed</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">High Match (≥75%)</span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{stats.high_matches}</span>
            <span className="text-xs text-indigo-400 font-medium">Gemini AI</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Semantically matched via ChromaDB</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Applications Submitted</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <Send className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{stats.applications_submitted}</span>
            <span className="text-xs text-emerald-400 font-medium">Verified</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Automated & proof-recorded</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Pending Review</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{stats.pending_approval}</span>
            <span className="text-xs text-slate-400 font-medium">In Queue</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Awaiting your one-click sign-off</p>
        </div>
      </div>

      {/* Main Workflow Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Link href="/jobs" className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-indigo-500/40 group block">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 group-hover:scale-110 transition-transform">
              <Briefcase className="w-6 h-6" />
            </div>
            <ArrowUpRight className="w-5 h-5 text-slate-500 group-hover:text-indigo-400 transition-colors" />
          </div>
          <h3 className="text-base font-bold text-white mb-1.5">Job Discovery Feed</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Browse discovered opportunities, review match score rubrics, and inspect missing qualification insights.
          </p>
        </Link>

        <Link href="/resumes" className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-indigo-500/40 group block">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 group-hover:scale-110 transition-transform">
              <FileText className="w-6 h-6" />
            </div>
            <ArrowUpRight className="w-5 h-5 text-slate-500 group-hover:text-violet-400 transition-colors" />
          </div>
          <h3 className="text-base font-bold text-white mb-1.5">Resume Studio</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Preview ATS-friendly tailored resumes generated with Google Gemini and download verified PDF or DOCX versions.
          </p>
        </Link>

        <Link href="/applications" className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-indigo-500/40 group block">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <ArrowUpRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 transition-colors" />
          </div>
          <h3 className="text-base font-bold text-white mb-1.5">Application Tracker</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Manage your pipeline across Kanban stages, inspect submission confirmation proofs, and approve pending applications.
          </p>
        </Link>
      </div>

      {/* Recent Discovered Jobs */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-white">Recent High-Match Listings</h3>
            <p className="text-xs text-slate-400">Evaluated against verified candidate profile</p>
          </div>
          <Link href="/jobs" className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1">
            View All Jobs <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800/80 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                <th className="pb-3 px-3">Role & Company</th>
                <th className="pb-3 px-3">Location</th>
                <th className="pb-3 px-3">Match Score</th>
                <th className="pb-3 px-3">Matched Skills</th>
                <th className="pb-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 text-sm">
              {recentJobs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-slate-500">
                    No jobs loaded yet. Click &quot;Run Pipeline Now&quot; to discover jobs!
                  </td>
                </tr>
              ) : (
                recentJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-semibold text-slate-200">{job.title}</div>
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
                        <span className="inline-block mt-1 text-[10px] bg-emerald-500/10 text-emerald-400 font-medium px-1.5 py-0.5 rounded border border-emerald-500/20">
                          Remote
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-indigo-400 text-sm">
                          {job.match_score ?? 85}%
                        </span>
                        <div className="w-16 h-2 rounded-full bg-slate-800 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400" 
                            style={{ width: `${job.match_score ?? 85}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {(job.matched_skills || ['Python', 'SQL', 'FastAPI']).slice(0, 3).map((s, idx) => (
                          <span key={idx} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700/60">
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
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors inline-block"
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
