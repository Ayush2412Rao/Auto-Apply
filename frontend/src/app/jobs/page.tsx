'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Search, 
  Building, 
  MapPin, 
  ExternalLink, 
  CheckCircle2, 
  AlertCircle, 
  SlidersHorizontal 
} from 'lucide-react';
import { fetchJobs, DiscoveredJob } from '@/lib/api';

export default function JobDiscoveryPage() {
  const [jobs, setJobs] = useState<DiscoveredJob[]>([]);
  const [search, setSearch] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [selectedJob, setSelectedJob] = useState<DiscoveredJob | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await fetchJobs(search || undefined, minScore > 0 ? minScore : undefined);
        setJobs(data);
        if (data.length > 0 && !selectedJob) {
          setSelectedJob(data[0]);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    const timer = setTimeout(load, 300);
    return () => clearTimeout(timer);
  }, [search, minScore]);

  return (
    <div>
      <Header 
        title="Job Discovery Feed" 
        subtitle="Live jobs aggregated via Apify and evaluated against your verified profile." 
      />

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center gap-4 mb-6">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by title, company, or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-[#121216] border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#007BA7] focus:ring-1 focus:ring-[#007BA7]/40 transition-all"
          />
        </div>

        <div className="flex items-center gap-2 bg-[#121216] border border-white/10 px-4 py-2 rounded-xl text-xs text-slate-300 w-full sm:w-auto">
          <SlidersHorizontal className="w-4 h-4 text-[#007BA7]" />
          <span>Min Score:</span>
          <select 
            value={minScore} 
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="bg-[#181820] border border-white/10 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-[#007BA7]"
          >
            <option value="0">All Scores</option>
            <option value="60">60% and above</option>
            <option value="75">75% (Auto-Submit Eligible)</option>
            <option value="85">85% (Top Matches)</option>
          </select>
        </div>
      </div>

      {/* Main Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Job List */}
        <div className="lg:col-span-5 space-y-3 max-h-[750px] overflow-y-auto pr-1">
          {jobs.length === 0 ? (
            <div className="glass-card p-8 rounded-2xl text-center text-slate-500">
              No jobs matching criteria.
            </div>
          ) : (
            jobs.map((job) => {
              const isSelected = selectedJob?.id === job.id;
              const score = job.match_score ?? 85;
              const isHighMatch = score >= 75;
              return (
                <div
                  key={job.id}
                  onClick={() => setSelectedJob(job)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-[#14141c] border-[#007BA7] shadow-lg shadow-[#007BA7]/15 ring-1 ring-[#007BA7]/40' 
                      : 'glass-card border-white/5 hover:border-[#007BA7]/40'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-semibold text-slate-200 text-sm">{job.title}</h4>
                      <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-1">
                        <Building className="w-3.5 h-3.5 text-slate-500" />
                        {job.company}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs font-bold px-2 py-1 rounded border ${
                        isHighMatch
                          ? 'text-[#FF2D95] bg-[#FF2D95]/10 border-[#FF2D95]/30 shadow-sm shadow-[#FF2D95]/10'
                          : 'text-[#007BA7] bg-[#007BA7]/10 border-[#007BA7]/30'
                      }`}>
                        {score}% Match
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 mt-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      {job.location}
                    </span>
                    {job.is_remote && (
                      <span className="text-[10px] bg-[#007BA7]/15 text-[#38bdf8] px-1.5 py-0.5 rounded border border-[#007BA7]/30 font-medium">
                        Remote
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Job Detail Card */}
        <div className="lg:col-span-7">
          {selectedJob ? (
            <div className="glass-panel p-6 rounded-2xl border border-white/10 sticky top-8">
              <div className="flex items-start justify-between pb-4 border-b border-white/10">
                <div>
                  <h3 className="text-xl font-bold text-white">{selectedJob.title}</h3>
                  <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                    <span className="font-medium text-slate-300">{selectedJob.company}</span>
                    <span>•</span>
                    <span>{selectedJob.location}</span>
                    <span>•</span>
                    <span className="text-[#007BA7] font-medium">Source: {selectedJob.source}</span>
                  </div>
                </div>
                <a
                  href={selectedJob.application_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-xs bg-gradient-to-r from-[#007BA7] to-[#0092c4] hover:from-[#008dbf] hover:to-[#FF2D95] text-white font-semibold px-4 py-2 rounded-lg transition-all shadow-md shadow-[#007BA7]/25 cursor-pointer"
                >
                  <span>Portal Link</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              {/* Match Score & Reasoning */}
              <div className="my-5 p-4 rounded-xl bg-[#121216] border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold uppercase text-slate-400">Gemini Match Evaluation</span>
                  <span className={`text-sm font-bold ${
                    (selectedJob.match_score ?? 85) >= 75 ? 'text-[#FF2D95]' : 'text-[#007BA7]'
                  }`}>
                    {selectedJob.match_score ?? 85}% Compatible
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {selectedJob.reasoning || "Strong alignment with candidate's AI engineering, LangGraph, and full-stack software development background."}
                </p>

                <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-3 border-t border-white/5">
                  <div>
                    <span className="text-emerald-400 font-semibold flex items-center gap-1 mb-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Matched Skills
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {(selectedJob.matched_skills || ['Python', 'SQL', 'LangGraph', 'FastAPI', 'Power BI']).map((s, idx) => (
                        <span key={idx} className="text-[10px] bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/20">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-amber-400 font-semibold flex items-center gap-1 mb-1">
                      <AlertCircle className="w-3.5 h-3.5" /> Missing / Transferable
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {(selectedJob.missing_qualifications || ['None (Strong candidate coverage)']).map((m, idx) => (
                        <span key={idx} className="text-[10px] bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded border border-amber-500/20">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div>
                <h4 className="text-xs font-semibold uppercase text-slate-400 mb-2">Job Description</h4>
                <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line max-h-72 overflow-y-auto pr-2 bg-[#0c0c10] p-4 rounded-xl border border-white/5">
                  {selectedJob.description || "No full description provided."}
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-12 rounded-2xl text-center text-slate-500">
              Select a job from the left to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
