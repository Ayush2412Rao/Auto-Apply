'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Send, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Building, 
  ShieldCheck,
  Calendar,
  ExternalLink
} from 'lucide-react';
import { fetchApplications, approveApplication, rejectApplication, JobApplicationItem } from '@/lib/api';
import { soundFx } from '@/lib/soundFx';

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
      soundFx.playChirp();
      await approveApplication(id);
      setActionFeedback(`Application #${id} approved!`);
      loadData();
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleReject = async (id: number) => {
    try {
      soundFx.playClick();
      await rejectApplication(id);
      setActionFeedback(`Application #${id} rejected.`);
      loadData();
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  // Group applications by status
  const appliedApps = applications.filter(a => a.status === 'applied');
  const pendingApps = applications.filter(a => a.status === 'pending_approval');
  const otherApps = applications.filter(a => a.status !== 'applied' && a.status !== 'pending_approval');

  return (
    <div>
      <Header 
        title="Application Tracker" 
        subtitle="Manage end-to-end submissions, review pending items, and inspect verification evidence." 
      />

      {actionFeedback && (
        <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {actionFeedback}
        </div>
      )}

      {/* Kanban Columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Column 1: Awaiting Approval */}
        <div className="glass-panel hud-bracket p-5 rounded-2xl border border-white/10 flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#FF2D95]" />
              <h3 className="font-bold text-sm text-white">Pending Approval</h3>
            </div>
            <span className="text-xs bg-[#FF2D95]/10 text-[#FF2D95] font-bold px-2 py-0.5 rounded-full border border-[#FF2D95]/30">
              {pendingApps.length}
            </span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-[600px] pr-1">
            {pendingApps.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-8">No applications awaiting approval.</p>
            ) : (
              pendingApps.map(app => (
                <div key={app.id} className="p-4 rounded-xl bg-[#121216] border border-white/10 shadow-sm hover:border-[#007BA7]/30 transition-all">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-slate-200 text-sm">{app.title}</h4>
                      <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                        <Building className="w-3 h-3 text-slate-500" />
                        {app.company}
                      </p>
                    </div>
                    <span className="text-xs font-bold text-[#FF2D95]">{app.match_score ?? 85}%</span>
                  </div>

                  <div className="flex items-center gap-2 mt-4 pt-3 border-t border-white/5">
                    <button
                      onClick={() => handleApprove(app.id)}
                      className="flex-1 text-xs bg-gradient-to-r from-[#007BA7] to-[#0092c4] hover:from-[#008dbf] hover:to-[#FF2D95] text-white font-medium py-1.5 rounded-lg transition-all shadow-md shadow-[#007BA7]/20 cursor-pointer"
                    >
                      Approve & Submit
                    </button>
                    <button
                      onClick={() => handleReject(app.id)}
                      className="text-xs bg-[#181820] hover:bg-[#202028] text-slate-300 font-medium px-3 py-1.5 rounded-lg border border-white/10 transition-colors cursor-pointer"
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
        <div className="glass-panel hud-bracket p-5 rounded-2xl border border-white/10 flex flex-col md:col-span-2">
          <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#007BA7]" />
              <h3 className="font-bold text-sm text-white">Applied & Verified</h3>
            </div>
            <span className="text-xs bg-[#007BA7]/10 text-[#007BA7] font-bold px-2 py-0.5 rounded-full border border-[#007BA7]/30">
              {appliedApps.length}
            </span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-[600px] pr-1">
            {appliedApps.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-8">No applications submitted yet.</p>
            ) : (
              appliedApps.map(app => (
                <div key={app.id} className="p-4 rounded-xl bg-[#121216] border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-[#007BA7]/30 transition-all">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-slate-200 text-sm">{app.title}</h4>
                      <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-semibold flex items-center gap-1">
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
                      <span className="text-[#FF2D95] font-semibold">Match: {app.match_score ?? 85}%</span>
                    </div>

                    {app.evidence && (
                      <div className="mt-2 text-[11px] text-slate-400 bg-[#0A0A0A] px-2.5 py-1 rounded border border-white/10 inline-block">
                        Confirmation: <code className="text-[#007BA7] font-mono font-medium">{app.evidence.confirmation_code || 'VERIFIED'}</code>
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
