import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api',
  timeout: 30000,
});

export interface DashboardStats {
  jobs_discovered: number;
  high_matches: number;
  applications_submitted: number;
  pending_approval: number;
  scheduler_status: string;
  last_run_status: string;
}

export interface DiscoveredJob {
  id: number;
  title: string;
  company: string;
  location: string;
  is_remote: boolean;
  employment_type: string;
  source: string;
  application_url: string;
  description?: string;
  discovered_at: string;
  match_score?: number;
  recommendation?: string;
  reasoning?: string;
  matched_skills?: string[];
  missing_qualifications?: string[];
}

export interface TailoredResume {
  id: number;
  version_identifier: string;
  job_id: number;
  job_title: string;
  company_name: string;
  pdf_available: boolean;
  docx_available: boolean;
  validation_status: string;
  created_at: string;
}

export interface JobApplicationItem {
  id: number;
  job_id: number;
  resume_version_id: number;
  title: string;
  company: string;
  location: string;
  match_score?: number;
  status: string;
  approved: boolean;
  submitted_at?: string;
  evidence?: any;
  error?: string;
  updated_at?: string;
}

export const fetchStats = async (): Promise<DashboardStats> => {
  const res = await api.get('/agent/stats');
  return res.data;
};

export const fetchJobs = async (search?: string, minScore?: number): Promise<DiscoveredJob[]> => {
  const params: any = {};
  if (search) params.search = search;
  if (minScore) params.min_score = minScore;
  const res = await api.get('/jobs/', { params });
  return res.data;
};

export const fetchResumes = async (): Promise<TailoredResume[]> => {
  const res = await api.get('/resumes/');
  return res.data;
};

export const fetchApplications = async (status?: string): Promise<JobApplicationItem[]> => {
  const params = status ? { status } : {};
  const res = await api.get('/applications/', { params });
  return res.data;
};

export const approveApplication = async (id: number) => {
  const res = await api.post(`/applications/${id}/approve`);
  return res.data;
};

export const rejectApplication = async (id: number) => {
  const res = await api.post(`/applications/${id}/reject`);
  return res.data;
};

export const triggerAgentRun = async () => {
  const res = await api.post('/agent/run-now');
  return res.data;
};

export const fetchLatestRun = async () => {
  const res = await api.get('/agent/runs/latest');
  return res.data;
};

export const fetchPreferences = async () => {
  const res = await api.get('/preferences/');
  return res.data;
};

export const updatePreferences = async (data: any) => {
  const res = await api.post('/preferences/', data);
  return res.data;
};

export const fetchProfile = async () => {
  const res = await api.get('/profile/');
  return res.data;
};
