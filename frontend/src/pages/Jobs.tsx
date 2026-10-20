import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobApi } from '../services/api';
import { Job } from '../types';
import {
  Briefcase,
  Plus,
  Trash2,
  Edit2,
  Sparkles,
  MapPin,
  Clock,
  AlertCircle,
  CheckCircle2,
  X
} from 'lucide-react';

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  Saved: { bg: '#EDE5F8', text: '#7657B8' },
  Applied: { bg: '#E7F1FA', text: '#1A73E8' },
  Interview: { bg: '#E3F6F1', text: '#137333' },
  Offer: { bg: '#D1F2E8', text: '#0D652D' },
  Rejected: { bg: '#F8ECE7', text: '#C04828' }
};

export const Jobs: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);

  // Form State
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [location, setLocation] = useState('Remote');
  const [jobDescription, setJobDescription] = useState('');
  const [requiredExp, setRequiredExp] = useState(2.0);
  const [status, setStatus] = useState<Job['status']>('Saved');

  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchJobs = async () => {
    try {
      const res = await jobApi.list();
      setJobs(res.jobs);
    } catch (err) {
      setError('Failed to load saved jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const openCreateModal = () => {
    setEditingJob(null);
    setTitle('');
    setCompany('');
    setLocation('Remote');
    setJobDescription('');
    setRequiredExp(2.0);
    setStatus('Saved');
    setIsModalOpen(true);
  };

  const openEditModal = (job: Job) => {
    setEditingJob(job);
    setTitle(job.title);
    setCompany(job.company);
    setLocation(job.location);
    setJobDescription(job.job_description);
    setRequiredExp(job.required_experience_years);
    setStatus(job.status);
    setIsModalOpen(true);
  };

  const handleSaveJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (editingJob) {
        const updated = await jobApi.update(editingJob.id, {
          title, company, location, job_description: jobDescription, required_experience_years: requiredExp, status
        });
        setJobs(prev => prev.map(j => j.id === updated.id ? updated : j));
      } else {
        const created = await jobApi.create({
          title, company, location, job_description: jobDescription, required_experience_years: requiredExp, status
        });
        setJobs(prev => [created, ...prev]);
      }
      setIsModalOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save job details.');
    }
  };

  const handleDeleteJob = async (id: string) => {
    if (!window.confirm('Delete this job posting?')) return;
    try {
      await jobApi.delete(id);
      setJobs(prev => prev.filter(j => j.id !== id));
    } catch (err) {
      setError('Failed to delete job.');
    }
  };

  const handleStatusChange = async (job: Job, newStatus: Job['status']) => {
    try {
      const updated = await jobApi.update(job.id, { status: newStatus });
      setJobs(prev => prev.map(j => j.id === updated.id ? updated : j));
    } catch (err) {
      setError('Failed to update status.');
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Opportunity Board</span>
          <h1 className="text-2xl font-bold text-[#111111] mt-0.5">Tracked Jobs & Pipeline</h1>
          <p className="text-xs text-[#555555]">Track target positions, update interview pipelines, and run instant semantic evaluations.</p>
        </div>

        <button
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white font-semibold text-xs shadow-sm shadow-[#7657B8]/20 transition-all hover:scale-102"
        >
          <Plus className="w-3.5 h-3.5" />
          Add Target Job
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#F8ECE7] border border-[#F1D0C5] text-xs text-[#C04828] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
        </div>
      ) : jobs.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white border border-[#E4DDEA] text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-[#EDE5F8] text-[#7657B8] flex items-center justify-center mx-auto">
            <Briefcase className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-base text-[#111111]">No jobs tracked yet</h3>
          <p className="text-xs text-[#555555] max-w-sm mx-auto">
            Add a target role and paste its job description to monitor your application status and run semantic matching.
          </p>
          <button
            onClick={openCreateModal}
            className="px-4 py-2 rounded-xl bg-[#7657B8] text-white font-semibold text-xs"
          >
            Create First Job Post
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => {
            const badgeStyle = STATUS_COLORS[job.status] || STATUS_COLORS.Saved;
            return (
              <div
                key={job.id}
                className="bg-white p-5 rounded-2xl border border-[#E4DDEA] hover:border-[#7657B8] transition-colors shadow-xs flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <span
                      className="px-2.5 py-1 rounded-full text-[11px] font-bold"
                      style={{ backgroundColor: badgeStyle.bg, color: badgeStyle.text }}
                    >
                      {job.status}
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => openEditModal(job)}
                        className="p-1.5 rounded-lg text-[#888888] hover:text-[#7657B8] hover:bg-[#FAF9FC]"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteJob(job.id)}
                        className="p-1.5 rounded-lg text-[#888888] hover:text-[#C04828] hover:bg-[#F8ECE7]"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-bold text-sm text-[#111111]">{job.title}</h3>
                    <p className="text-xs text-[#555555]">{job.company}</p>
                  </div>

                  <div className="space-y-1 text-xs text-[#777777] pt-2 border-t border-[#F0EDF5]">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5" />
                      <span>{job.location}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Req: {job.required_experience_years} yrs</span>
                    </div>
                  </div>

                  {/* Status Dropdown */}
                  <div className="pt-2">
                    <label className="text-[10px] font-semibold text-[#888888] block mb-1">Application Status:</label>
                    <select
                      value={job.status}
                      onChange={(e) => handleStatusChange(job, e.target.value as Job['status'])}
                      className="w-full text-xs p-1.5 rounded-lg border border-[#E4DDEA] bg-[#FAF9FC]"
                    >
                      <option value="Saved">Saved</option>
                      <option value="Applied">Applied</option>
                      <option value="Interview">Interview</option>
                      <option value="Offer">Offer</option>
                      <option value="Rejected">Rejected</option>
                    </select>
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-[#F0EDF5]">
                  <button
                    onClick={() => navigate('/analyze')}
                    className="w-full py-2 rounded-xl bg-[#EDE5F8] hover:bg-[#7657B8] hover:text-white text-[#7657B8] font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    Evaluate Resume Fit
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-lg rounded-3xl p-6 border border-[#E4DDEA] shadow-2xl space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-[#F0EDF5]">
              <h3 className="font-bold text-base text-[#111111]">
                {editingJob ? 'Edit Job Posting' : 'Add Target Job'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="p-1.5 rounded-lg text-[#555555]">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveJob} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-[#111111] mb-1">Job Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Data Scientist"
                  className="w-full p-2.5 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-[#111111] mb-1">Company</label>
                  <input
                    type="text"
                    required
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="e.g. OpenAI"
                    className="w-full p-2.5 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC]"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-[#111111] mb-1">Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Remote / Bangalore"
                    className="w-full p-2.5 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-[#111111] mb-1">Required Exp (Years)</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={requiredExp}
                    onChange={(e) => setRequiredExp(parseFloat(e.target.value))}
                    className="w-full p-2.5 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC]"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-[#111111] mb-1">Pipeline Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value as Job['status'])}
                    className="w-full p-2.5 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC]"
                  >
                    <option value="Saved">Saved</option>
                    <option value="Applied">Applied</option>
                    <option value="Interview">Interview</option>
                    <option value="Offer">Offer</option>
                    <option value="Rejected">Rejected</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-[#111111] mb-1">Job Description</label>
                <textarea
                  required
                  rows={5}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste responsibilities and requirements..."
                  className="w-full p-2.5 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC]"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white font-semibold text-xs shadow-xs"
              >
                {editingJob ? 'Save Changes' : 'Add Job Post'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
