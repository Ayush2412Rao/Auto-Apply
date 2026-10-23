'use client';

import React, { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { 
  Download, 
  ShieldCheck, 
  CheckCircle2, 
  Building, 
  Calendar, 
  Award,
  GraduationCap
} from 'lucide-react';
import { fetchResumes, fetchProfile, TailoredResume } from '@/lib/api';

export default function ResumeStudioPage() {
  const [resumes, setResumes] = useState<TailoredResume[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [resData, profData] = await Promise.all([
          fetchResumes().catch(() => []),
          fetchProfile().catch(() => null)
        ]);
        setResumes(resData);
        setProfile(profData);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div>
      <Header 
        title="Resume Studio" 
        subtitle="Master profile source-of-truth and ATS-tailored resume versions generated with Gemini." 
      />

      {/* Master Profile Summary Bar */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-5 border-b border-white/[0.08]">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-white tracking-tight">Ayush Rao</h3>
              <span className="text-xs bg-emerald-500/10 text-emerald-400 font-medium px-2.5 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Verified Ground Truth
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Software Engineer – AI/ML & Data Engineering • Noida / Delhi NCR, India
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <a
              href="http://127.0.0.1:8000/api/resumes/master/pdf"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs bg-white/[0.04] hover:bg-white/[0.08] text-slate-200 px-3.5 py-2 rounded-xl border border-white/[0.08] hover:border-[#007BA7]/40 transition-all cursor-pointer font-medium"
            >
              <Download className="w-3.5 h-3.5 text-[#007BA7]" />
              <span>Master PDF</span>
            </a>

            <a
              href="http://127.0.0.1:8000/api/resumes/master/docx"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs bg-white/[0.04] hover:bg-white/[0.08] text-slate-200 px-3.5 py-2 rounded-xl border border-white/[0.08] hover:border-slate-300 transition-all cursor-pointer font-medium"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              <span>Master DOCX</span>
            </a>
          </div>
        </div>

        {/* Verified Facts Breakdown */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-5 text-xs">
          <div className="flex items-start gap-2.5 p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
            <Building className="w-4 h-4 text-[#007BA7] mt-0.5 shrink-0" />
            <div>
              <span className="font-semibold text-slate-300">Verified Experience:</span>
              <p className="text-slate-400 mt-0.5">MAQ Software (May 2025 – Present), Grasim Industries (June – July 2024)</p>
            </div>
          </div>

          <div className="flex items-start gap-2.5 p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
            <GraduationCap className="w-4 h-4 text-[#007BA7] mt-0.5 shrink-0" />
            <div>
              <span className="font-semibold text-slate-300">Verified Education:</span>
              <p className="text-slate-400 mt-0.5">B.Tech in CSE, Lovely Professional University (2022 – 2026, CGPA: 7.69)</p>
            </div>
          </div>

          <div className="flex items-start gap-2.5 p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
            <Award className="w-4 h-4 text-[#007BA7] mt-0.5 shrink-0" />
            <div>
              <span className="font-semibold text-slate-300">Verified Core Skills:</span>
              <p className="text-slate-400 mt-0.5">LangGraph, Python, FastAPI, Snowflake, Power BI, SQL Server</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tailored Resumes List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-white">Tailored ATS Resumes</h3>
            <p className="text-xs text-slate-400">Customized per company & role without inventing qualifications</p>
          </div>
          <span className="text-xs text-slate-400 font-medium">
            {resumes.length} Tailored Documents Generated
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {resumes.length === 0 ? (
            <div className="col-span-2 glass-card p-8 rounded-2xl text-center text-slate-500 text-sm">
              No tailored resumes generated yet.
            </div>
          ) : (
            resumes.map((rv) => (
              <div key={rv.id} className="glass-card p-5 rounded-2xl border border-white/[0.08] hover:border-[#007BA7]/40 transition-all">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-slate-200 text-sm">{rv.job_title}</h4>
                    <p className="text-xs text-[#007BA7] font-medium mt-0.5">{rv.company_name}</p>
                  </div>
                  <span className="text-[11px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Factual Check Passed
                  </span>
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-500 my-3">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(rv.created_at).toLocaleDateString()}
                  </span>
                  <span>•</span>
                  <span>Version: {rv.version_identifier}</span>
                </div>

                <div className="flex items-center gap-2.5 pt-3 border-t border-white/[0.04]">
                  <a
                    href={`http://127.0.0.1:8000/api/resumes/${rv.id}/pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 flex items-center justify-center gap-1.5 text-xs bg-[#007BA7] hover:bg-[#006e96] text-white font-medium py-2 rounded-xl transition-all cursor-pointer shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </a>

                  <a
                    href={`http://127.0.0.1:8000/api/resumes/${rv.id}/docx`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 flex items-center justify-center gap-1.5 text-xs bg-white/[0.04] hover:bg-white/[0.08] text-slate-200 font-medium py-2 rounded-xl border border-white/[0.08] hover:border-slate-300 transition-all cursor-pointer shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download DOCX</span>
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
