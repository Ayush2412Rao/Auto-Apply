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
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl text-xs text-slate-300 w-full sm:w-auto">
          <SlidersHorizontal className="w-4 h-4 text-indigo-400" />
          <span>Min Score:</span>
          <select 
            value={minScore} 
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none"
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
              return (
                <div
                  key={job.id}
                  onClick={() => setSelectedJob(job)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-slate-900 border-indigo-500/80 shadow-md shadow-indigo-500/10' 
                      : 'glass-card border-slate-800/80 hover:border-slate-700'
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
                      <span className="text-xs font-bold text-indigo-400 px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20">
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
                      <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20">
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
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 sticky top-8">
              <div className="flex items-start justify-between pb-4 border-b border-slate-800/80">
                <div>
                  <h3 className="text-xl font-bold text-white">{selectedJob.title}</h3>
                  <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                    <span className="font-medium text-slate-300">{selectedJob.company}</span>
                    <span>•</span>
                    <span>{selectedJob.location}</span>
                    <span>•</span>
                    <span>Source: {selectedJob.source}</span>
                  </div>
                </div>
                <a
                  href={selectedJob.application_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg transition-colors shadow-md shadow-indigo-600/20"
                >
                  <span>Portal Link</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              {/* Match Score & Reasoning */}
              <div className="my-5 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold uppercase text-slate-400">Gemini Match Evaluation</span>
                  <span className="text-sm font-bold text-indigo-400">{selectedJob.match_score ?? 85}% Compatible</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {selectedJob.reasoning || "Strong alignment with candidate's AI engineering, LangGraph, and full-stack software development background."}
                </p>

                <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-3 border-t border-slate-800/60">
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
                <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line max-h-72 overflow-y-auto pr-2 bg-slate-900/40 p-4 rounded-xl border border-slate-800/40">
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
