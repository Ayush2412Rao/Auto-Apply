'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Clock, 
  CheckCircle2, 
  Building, 
  ShieldCheck,
  Calendar,
  Mail,
  RefreshCw,
  AlertCircle,
  Sparkles,
  ChevronRight,
  Send,
  Award
} from 'lucide-react';
import { 
  fetchApplications, 
  approveApplication, 
  rejectApplication, 
  scanRecruiterEmails,
  JobApplicationItem 
} from '@/lib/api';

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<JobApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [filterActiveTab, setFilterActiveTab] = useState<'all' | 'active' | 'archived'>('active');

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
      setActionFeedback(`Application #${id} approved & queued`);
      loadData();
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await rejectApplication(id);
      setActionFeedback(`Application #${id} archived`);
      loadData();
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleScanInbox = async () => {
    setScanning(true);
    setScanMessage(null);
    try {
      const res = await scanRecruiterEmails();
      setScanMessage(res.message || 'Inbox scan complete.');
      await loadData();
    } catch (err: any) {
      setScanMessage('Failed to scan inbox. Verify SMTP/IMAP settings in .env.');
    } finally {
      setScanning(false);
      setTimeout(() => setScanMessage(null), 6000);
    }
  };

  // Group applications across Kanban stages
  const pendingApps = applications.filter(a => a.status === 'pending_approval' || a.status === 'manual_required');
  const appliedApps = applications.filter(a => a.status === 'applied');
  const reviewApps = applications.filter(a => a.status === 'under_review');
  const interviewApps = applications.filter(a => ['interview_scheduled', 'assessment_received', 'offer'].includes(a.status));
  const archivedApps = applications.filter(a => ['rejected', 'rejected_by_user'].includes(a.status));

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-12 py-8">
      {/* Top Header & Sync Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <span className="text-[11px] font-bold tracking-wider uppercase text-[#007BA7]">
            PIPELINE KANBAN
          </span>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1">
            Application Pipeline
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time status tracking from Playwright submission to recruiter email updates.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleScanInbox}
            disabled={scanning}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/[0.04] hover:bg-white/[0.08] text-slate-200 border border-white/[0.1] transition-all cursor-pointer shadow-sm hover:border-[#007BA7]/40 disabled:opacity-60"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#007BA7] ${scanning ? 'animate-spin' : ''}`} />
            {scanning ? 'Scanning Inbox...' : 'Sync Recruiter Emails'}
          </button>
        </div>
      </div>

      {/* Notifications / Feedback */}
      {scanMessage && (
        <div className="mb-5 p-3 rounded-xl bg-[#007BA7]/10 border border-[#007BA7]/30 text-sky-300 text-xs font-medium flex items-center gap-2">
          <Mail className="w-4 h-4 text-[#007BA7] shrink-0" />
          <span>{scanMessage}</span>
        </div>
      )}

      {actionFeedback && (
        <div className="mb-5 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{actionFeedback}</span>
        </div>
      )}

      {/* View Filter Toggles */}
      <div className="flex items-center justify-between mb-6 pb-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterActiveTab('active')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
              filterActiveTab === 'active'
                ? 'bg-[#007BA7] text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            Active Pipeline ({applications.length - archivedApps.length})
          </button>
          <button
            onClick={() => setFilterActiveTab('archived')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
              filterActiveTab === 'archived'
                ? 'bg-[#007BA7] text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            Archived / Rejected ({archivedApps.length})
          </button>
        </div>

        <span className="text-xs text-slate-500">
          Total Applications: {applications.length}
        </span>
      </div>

      {filterActiveTab === 'active' ? (
        /* 4-Stage Kanban Pipeline Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Column 1: Pending Approval */}
          <div className="glass-panel p-4 rounded-2xl border border-white/[0.08] flex flex-col bg-slate-900/40">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-3">
              <div className="flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-amber-400" />
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-200">Pending Review</h3>
              </div>
              <span className="text-[11px] bg-amber-500/10 text-amber-400 font-semibold px-2 py-0.5 rounded-full border border-amber-500/20">
                {pendingApps.length}
              </span>
            </div>

            <div className="space-y-3 flex-1 overflow-y-auto max-h-[640px] pr-1">
              {pendingApps.length === 0 ? (
                <div className="text-center py-10">
                  <p className="text-xs text-slate-500">No applications pending review.</p>
                </div>
              ) : (
                pendingApps.map(app => (
                  <div key={app.id} className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-amber-400/30 transition-all">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-semibold text-slate-200 text-xs leading-snug">{app.title}</h4>
                        <p className="text-[11px] text-slate-400 flex items-center gap-1 mt-1">
                          <Building className="w-3 h-3 text-slate-500" />
                          {app.company}
                        </p>
                      </div>
                      <span className="text-[11px] font-bold text-emerald-400 shrink-0">
                        {app.match_score ?? 85}%
                      </span>
                    </div>

                    {app.status === 'manual_required' && (
                      <div className="mt-2 text-[10px] text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> CAPTCHA / Review Needed
                      </div>
                    )}

                    <div className="flex items-center gap-2 mt-3 pt-2.5 border-t border-white/[0.04]">
                      <button
                        onClick={() => handleApprove(app.id)}
                        className="flex-1 text-[11px] bg-[#007BA7] hover:bg-[#006e96] text-white font-medium py-1.5 rounded-lg transition-all cursor-pointer shadow-sm text-center"
                      >
                        Submit
                      </button>
                      <button
                        onClick={() => handleReject(app.id)}
                        className="text-[11px] bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 hover:text-slate-200 font-medium px-2.5 py-1.5 rounded-lg border border-white/[0.08] transition-colors cursor-pointer"
                      >
                        Skip
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Column 2: Applied / Submitted */}
          <div className="glass-panel p-4 rounded-2xl border border-white/[0.08] flex flex-col bg-slate-900/40">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-3">
              <div className="flex items-center gap-2">
                <Send className="w-3.5 h-3.5 text-sky-400" />
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-200">Applied</h3>
              </div>
              <span className="text-[11px] bg-sky-500/10 text-sky-400 font-semibold px-2 py-0.5 rounded-full border border-sky-500/20">
                {appliedApps.length}
              </span>
            </div>

            <div className="space-y-3 flex-1 overflow-y-auto max-h-[640px] pr-1">
              {appliedApps.length === 0 ? (
                <div className="text-center py-10">
                  <p className="text-xs text-slate-500">No recent submissions.</p>
                </div>
              ) : (
                appliedApps.map(app => (
                  <div key={app.id} className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-sky-500/30 transition-all">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-semibold text-slate-200 text-xs leading-snug">{app.title}</h4>
                        <p className="text-[11px] text-slate-400 flex items-center gap-1 mt-1">
                          <Building className="w-3 h-3 text-slate-500" />
                          {app.company}
                        </p>
                      </div>
                      <span className="text-[11px] font-bold text-sky-400 shrink-0">
                        {app.match_score ?? 85}%
                      </span>
                    </div>

                    <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-400">
                      <span className="flex items-center gap-1 text-slate-400">
                        <Calendar className="w-3 h-3" />
                        {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : 'Today'}
                      </span>
                      {app.evidence?.confirmation_code && (
                        <span className="font-mono text-slate-300 bg-white/[0.04] px-1.5 py-0.5 rounded border border-white/[0.04]">
                          {app.evidence.confirmation_code}
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Column 3: Under Review */}
          <div className="glass-panel p-4 rounded-2xl border border-white/[0.08] flex flex-col bg-slate-900/40">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-200">Under Review</h3>
              </div>
              <span className="text-[11px] bg-indigo-500/10 text-indigo-400 font-semibold px-2 py-0.5 rounded-full border border-indigo-500/20">
                {reviewApps.length}
              </span>
            </div>

            <div className="space-y-3 flex-1 overflow-y-auto max-h-[640px] pr-1">
              {reviewApps.length === 0 ? (
                <div className="text-center py-10">
                  <p className="text-xs text-slate-500">Recruiter confirmations will appear here.</p>
                </div>
              ) : (
                reviewApps.map(app => (
                  <div key={app.id} className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-indigo-500/30 transition-all">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-semibold text-slate-200 text-xs leading-snug">{app.title}</h4>
                        <p className="text-[11px] text-slate-400 flex items-center gap-1 mt-1">
                          <Building className="w-3 h-3 text-slate-500" />
                          {app.company}
                        </p>
                      </div>
                      <span className="text-[11px] font-bold text-indigo-400 shrink-0">
                        {app.match_score ?? 85}%
                      </span>
                    </div>

                    <div className="mt-2 text-[10px] text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 flex items-center gap-1">
                      <Mail className="w-3 h-3" /> Application Acknowledged
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Column 4: Interview & Assessments */}
          <div className="glass-panel p-4 rounded-2xl border border-white/[0.08] flex flex-col bg-slate-900/40">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-200">Interview / Tests</h3>
              </div>
              <span className="text-[11px] bg-purple-500/10 text-purple-400 font-semibold px-2 py-0.5 rounded-full border border-purple-500/20">
                {interviewApps.length}
              </span>
            </div>

            <div className="space-y-3 flex-1 overflow-y-auto max-h-[640px] pr-1">
              {interviewApps.length === 0 ? (
                <div className="text-center py-10">
                  <p className="text-xs text-slate-500">Sync inbox to track interview invitations.</p>
                </div>
              ) : (
                interviewApps.map(app => {
                  const isOffer = app.status === 'offer';
                  const isInterview = app.status === 'interview_scheduled';
                  const isAssessment = app.status === 'assessment_received';

                  return (
                    <div 
                      key={app.id} 
                      className={`p-3.5 rounded-xl bg-white/[0.02] border transition-all ${
                        isOffer 
                          ? 'border-emerald-500/40 bg-emerald-950/10' 
                          : isInterview 
                            ? 'border-purple-500/40 bg-purple-950/10' 
                            : 'border-amber-500/40 bg-amber-950/10'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h4 className="font-semibold text-slate-200 text-xs leading-snug">{app.title}</h4>
                          <p className="text-[11px] text-slate-400 flex items-center gap-1 mt-1">
                            <Building className="w-3 h-3 text-slate-500" />
                            {app.company}
                          </p>
                        </div>
                        <span className="text-[11px] font-bold text-purple-300 shrink-0">
                          {app.match_score ?? 85}%
                        </span>
                      </div>

                      <div className="mt-2.5">
                        {isOffer && (
                          <span className="text-[10px] bg-emerald-500/15 text-emerald-300 font-semibold px-2 py-0.5 rounded border border-emerald-500/30 flex items-center gap-1">
                            <Award className="w-3 h-3" /> Offer Received!
                          </span>
                        )}
                        {isInterview && (
                          <span className="text-[10px] bg-purple-500/15 text-purple-300 font-semibold px-2 py-0.5 rounded border border-purple-500/30 flex items-center gap-1">
                            <Sparkles className="w-3 h-3" /> Interview Round Invited
                          </span>
                        )}
                        {isAssessment && (
                          <span className="text-[10px] bg-amber-500/15 text-amber-300 font-semibold px-2 py-0.5 rounded border border-amber-500/30 flex items-center gap-1">
                            <Clock className="w-3 h-3" /> Technical Assessment Link
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      ) : (
        /* Archived / Rejected View */
        <div className="glass-panel p-5 rounded-2xl border border-white/[0.08] bg-slate-900/40">
          <h3 className="font-semibold text-sm text-slate-300 mb-4">
            Archived & Decision Updates ({archivedApps.length})
          </h3>
          {archivedApps.length === 0 ? (
            <p className="text-xs text-slate-500 py-6 text-center">No archived applications.</p>
          ) : (
            <div className="space-y-3">
              {archivedApps.map(app => (
                <div key={app.id} className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] flex items-center justify-between text-xs text-slate-400">
                  <div>
                    <h4 className="font-medium text-slate-300">{app.title}</h4>
                    <p className="text-[11px] text-slate-500">{app.company} • {app.location}</p>
                  </div>
                  <span className="text-[10px] bg-rose-500/10 text-rose-400 px-2.5 py-1 rounded-full border border-rose-500/20 font-medium">
                    {app.status === 'rejected_by_user' ? 'Declined by User' : 'Role Closed'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
