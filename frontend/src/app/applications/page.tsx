'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Clock, 
  CheckCircle2, 
  Building, 
  ShieldCheck,
  Calendar
} from 'lucide-react';
import { fetchApplications, approveApplication, rejectApplication, JobApplicationItem } from '@/lib/api';

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<JobApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const data = await fetchApplications();
      setApplications(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApprove = async (id: number) => {
    try {
      await approveApplication(id);
      setActionFeedback(`Application #${id} approved`);
      loadData();
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await rejectApplication(id);
      setActionFeedback(`Application #${id} rejected`);
      loadData();
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  // Group applications by status
  const appliedApps = applications.filter(a => a.status === 'applied');
  const pendingApps = applications.filter(a => a.status === 'pending_approval');

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-12 py-8">
      <Header 
        tag="PIPELINE KANBAN"
        title="Application Tracker" 
        subtitle="Manage submissions, review pending items, and inspect verification evidence." 
      />

      {actionFeedback && (
        <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {actionFeedback}
        </div>
      )}

      {/* Kanban Columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Column 1: Awaiting Approval */}
        <div className="glass-panel p-5 rounded-2xl border border-white/[0.08] flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <h3 className="font-bold text-sm text-white">Pending Approval</h3>
            </div>
            <span className="text-xs bg-amber-500/10 text-amber-400 font-semibold px-2 py-0.5 rounded-full border border-amber-500/20">
              {pendingApps.length}
            </span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-[600px] pr-1">
            {pendingApps.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-8">No applications awaiting approval.</p>
            ) : (
              pendingApps.map(app => (
                <div key={app.id} className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-[#007BA7]/40 transition-all">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-slate-200 text-sm">{app.title}</h4>
                      <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                        <Building className="w-3.5 h-3.5 text-slate-500" />
                        {app.company}
                      </p>
                    </div>
                    <span className="text-xs font-semibold text-[#007BA7]">{app.match_score ?? 85}%</span>
                  </div>

                  <div className="flex items-center gap-2 mt-4 pt-3 border-t border-white/[0.04]">
                    <button
                      onClick={() => handleApprove(app.id)}
                      className="flex-1 text-xs bg-[#007BA7] hover:bg-[#006e96] text-white font-medium py-1.5 rounded-lg transition-all cursor-pointer shadow-sm"
                    >
                      Approve & Submit
                    </button>
                    <button
                      onClick={() => handleReject(app.id)}
                      className="text-xs bg-white/[0.04] hover:bg-white/[0.08] text-slate-300 font-medium px-3 py-1.5 rounded-lg border border-white/[0.08] transition-colors cursor-pointer"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Column 2: Submitted / Applied */}
        <div className="glass-panel p-5 rounded-2xl border border-white/[0.08] flex flex-col md:col-span-2">
          <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <h3 className="font-bold text-sm text-white">Applied & Verified</h3>
            </div>
            <span className="text-xs bg-emerald-500/10 text-emerald-400 font-semibold px-2 py-0.5 rounded-full border border-emerald-500/20">
              {appliedApps.length}
            </span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-[600px] pr-1">
            {appliedApps.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-8">No applications submitted yet.</p>
            ) : (
              appliedApps.map(app => (
                <div key={app.id} className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-[#007BA7]/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-slate-200 text-sm">{app.title}</h4>
                      <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-medium flex items-center gap-1">
                        <ShieldCheck className="w-3 h-3" /> Submitted
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                      <span className="flex items-center gap-1">
                        <Building className="w-3.5 h-3.5 text-slate-500" />
                        {app.company}
                      </span>
                      <span>•</span>
                      <span>{app.location}</span>
                      <span>•</span>
                      <span className="text-emerald-400 font-medium">Match: {app.match_score ?? 85}%</span>
                    </div>

                    {app.evidence && (
                      <div className="mt-2 text-[11px] text-slate-400 bg-white/[0.03] px-2.5 py-1 rounded border border-white/[0.06] inline-block">
                        Confirmation: <span className="text-slate-200 font-medium">{app.evidence.confirmation_code || 'VERIFIED'}</span>
                      </div>
                    )}
                  </div>

                  <div className="text-right text-xs text-slate-500">
                    <span className="flex items-center gap-1 sm:justify-end">
                      <Calendar className="w-3.5 h-3.5" />
                      {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : 'Today'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
