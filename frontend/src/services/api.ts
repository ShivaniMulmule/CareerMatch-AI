import axios from 'axios';
import {
  User,
  AuthResponse,
  Resume,
  Job,
  AnalysisRecord,
  SystemHealth
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach bearer token from localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('careermatch_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Auth Endpoints
export const authApi = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/api/auth/login', { email, password });
    return res.data;
  },
  register: async (data: { email: string; password: string; full_name: string; target_role?: string; experience_level?: string }): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/api/auth/register', data);
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/api/auth/me');
    return res.data;
  }
};

// Resumes Endpoints
export const resumeApi = {
  upload: async (formData: FormData): Promise<Resume> => {
    const res = await apiClient.post<Resume>('/api/resumes', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  list: async (): Promise<{ resumes: Resume[]; total_count: number }> => {
    const res = await apiClient.get<{ resumes: Resume[]; total_count: number }>('/api/resumes');
    return res.data;
  },
  get: async (id: string): Promise<Resume> => {
    const res = await apiClient.get<Resume>(`/api/resumes/${id}`);
    return res.data;
  },
  delete: async (id: string): Promise<{ message: string }> => {
    const res = await apiClient.delete<{ message: string }>(`/api/resumes/${id}`);
    return res.data;
  }
};

// Jobs Endpoints
export const jobApi = {
  create: async (data: { title: string; company: string; location?: string; job_description: string; required_experience_years?: number; status?: string }): Promise<Job> => {
    const res = await apiClient.post<Job>('/api/jobs', data);
    return res.data;
  },
  list: async (): Promise<{ jobs: Job[]; total_count: number }> => {
    const res = await apiClient.get<{ jobs: Job[]; total_count: number }>('/api/jobs');
    return res.data;
  },
  get: async (id: string): Promise<Job> => {
    const res = await apiClient.get<Job>(`/api/jobs/${id}`);
    return res.data;
  },
  update: async (id: string, data: Partial<Job>): Promise<Job> => {
    const res = await apiClient.put<Job>(`/api/jobs/${id}`, data);
    return res.data;
  },
  delete: async (id: string): Promise<{ message: string }> => {
    const res = await apiClient.delete<{ message: string }>(`/api/jobs/${id}`);
    return res.data;
  }
};

// Analysis Endpoints
export const analysisApi = {
  analyze: async (data: { resume_id?: string; resume_text?: string; job_id?: string; job_title?: string; company?: string; job_description?: string }): Promise<AnalysisRecord> => {
    const res = await apiClient.post<AnalysisRecord>('/api/analyses', data);
    return res.data;
  },
  list: async (): Promise<{ analyses: AnalysisRecord[]; total_count: number }> => {
    const res = await apiClient.get<{ analyses: AnalysisRecord[]; total_count: number }>('/api/analyses');
    return res.data;
  },
  get: async (id: string): Promise<AnalysisRecord> => {
    const res = await apiClient.get<AnalysisRecord>(`/api/analyses/${id}`);
    return res.data;
  },
  delete: async (id: string): Promise<{ message: string }> => {
    const res = await apiClient.delete<{ message: string }>(`/api/analyses/${id}`);
    return res.data;
  },
  getReportUrl: (analysisId: string) => `/api/reports/${analysisId}`
};

// Recommendations & Catalog
export const recommendationApi = {
  getCatalog: async (): Promise<any> => {
    const res = await apiClient.get('/api/recommendations/catalog');
    return res.data;
  }
};

// Profile Endpoints
export const profileApi = {
  getProfile: async (): Promise<User> => {
    const res = await apiClient.get<User>('/api/profile');
    return res.data;
  },
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const res = await apiClient.put<User>('/api/profile', data);
    return res.data;
  }
};

// System Diagnostics
export const healthApi = {
  check: async (): Promise<SystemHealth> => {
    const res = await apiClient.get<SystemHealth>('/api/health');
    return res.data;
  }
};
