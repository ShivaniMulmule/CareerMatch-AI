import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeApi, jobApi, analysisApi } from '../services/api';
import { Resume, Job } from '../types';
import {
  Sparkles,
  Upload,
  FileText,
  Briefcase,
  AlertCircle,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight
} from 'lucide-react';

const ANALYSIS_STEPS = [
  "Parsing candidate resume sections & qualifications...",
  "Generating Sentence-BERT dense vector embeddings (all-MiniLM-L6-v2)...",
  "Engineering 14 multi-dimensional semantic alignment features...",
  "Evaluating profile with trained XGBoost Regressor model...",
  "Computing SHAP TreeExplainer local feature attributions...",
  "Synthesizing evidence-based skill gaps & tailored upskill roadmap..."
];

export const Analyze: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [savedJobs, setSavedJobs] = useState<Job[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('');
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  
  // Custom job fields
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [jobDescription, setJobDescription] = useState('');

  // Upload new resume on the fly
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    const loadPrerequisites = async () => {
      try {
        const [rRes, jRes] = await Promise.all([
          resumeApi.list(),
          jobApi.list()
        ]);
        setResumes(rRes.resumes);
        if (rRes.resumes.length > 0) {
          setSelectedResumeId(rRes.resumes[0].id);
        }
        setSavedJobs(jRes.jobs);
      } catch (err) {
        console.error('Failed to load resumes/jobs:', err);
      }
    };
    loadPrerequisites();
  }, []);

  // When user selects an existing saved job
  const handleSelectJob = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const jId = e.target.value;
    setSelectedJobId(jId);
    if (jId) {
      const found = savedJobs.find(j => j.id === jId);
      if (found) {
        setJobTitle(found.title);
        setCompany(found.company);
        setJobDescription(found.job_description);
      }
    }
  };

  const handleRunAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    let effectiveResumeId = selectedResumeId;

    // If user uploaded a new file directly in the form
    if (uploadFile) {
      try {
        const formData = new FormData();
        formData.append('file', uploadFile);
        const newResume = await resumeApi.upload(formData);
        effectiveResumeId = newResume.id;
        setResumes(prev => [newResume, ...prev]);
        setSelectedResumeId(newResume.id);
        setUploadFile(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to upload new resume PDF.');
        return;
      }
    }

    if (!effectiveResumeId && !uploadFile) {
      setError('Please select or upload a candidate resume PDF.');
      return;
    }

    if (!jobDescription.trim() || jobDescription.trim().length < 30) {
      setError('Please enter a detailed job description with responsibilities and requirements.');
      return;
    }

    setLoading(true);
    setActiveStepIndex(0);

    // Progressive step simulation for UX
    const interval = setInterval(() => {
      setActiveStepIndex((prev) => (prev < ANALYSIS_STEPS.length - 1 ? prev + 1 : prev));
    }, 600);

    try {
      const result = await analysisApi.analyze({
        resume_id: effectiveResumeId,
        job_id: selectedJobId || undefined,
        job_title: jobTitle || 'Target Role',
        company: company || 'Target Employer',
        job_description: jobDescription
      });
      clearInterval(interval);
      navigate(`/results/${result.id}`);
    } catch (err: any) {
      clearInterval(interval);
      setLoading(false);
      setError(err.response?.data?.detail || 'Analysis execution failed. Please try again.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="text-center mb-8">
        <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Semantic Matching Studio</span>
        <h1 className="text-3xl font-extrabold text-[#111111] mt-1">Analyze Resume-to-Job Fit</h1>
        <p className="text-xs sm:text-sm text-[#555555] max-w-lg mx-auto mt-1">
          Dense embeddings evaluate conceptual alignment between your resume and the target role with zero keyword counting.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-[#F8ECE7] border border-[#F1D0C5] text-xs text-[#C04828] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="bg-white p-8 rounded-2xl border border-[#E4DDEA] shadow-xs text-center space-y-6">
          <div className="w-12 h-12 rounded-2xl bg-[#EDE5F8] text-[#7657B8] flex items-center justify-center mx-auto">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#111111]">Running Explainable AI Pipeline</h3>
            <p className="text-xs text-[#555555] mt-1">Evaluating multi-dimensional representations with S-BERT, XGBoost, and SHAP</p>
          </div>

          <div className="space-y-3 max-w-md mx-auto text-left">
            {ANALYSIS_STEPS.map((step, idx) => (
              <div key={idx} className="flex items-center gap-3 text-xs">
                {idx < activeStepIndex ? (
                  <CheckCircle2 className="w-4 h-4 text-[#137333] shrink-0" />
                ) : idx === activeStepIndex ? (
                  <div className="w-4 h-4 border-2 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin shrink-0"></div>
                ) : (
                  <div className="w-4 h-4 rounded-full border border-[#E4DDEA] shrink-0"></div>
                )}
                <span className={idx === activeStepIndex ? "font-semibold text-[#7657B8]" : (idx < activeStepIndex ? "text-[#111111]" : "text-[#888888]")}>
                  {step}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <form onSubmit={handleRunAnalysis} className="space-y-6">
          {/* 1. Resume Selection Card */}
          <div className="bg-white p-6 rounded-2xl border border-[#E4DDEA] shadow-xs space-y-4">
            <h2 className="text-sm font-bold text-[#111111] flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#7657B8]" />
              Step 1: Select Candidate Resume
            </h2>

            {resumes.length > 0 && (
              <div>
                <label className="block text-xs font-semibold text-[#555555] mb-1">Choose from uploaded resumes</label>
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8]"
                >
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.original_filename} ({r.detected_role || 'Candidate'}) — {r.created_at.slice(0, 10)}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="pt-2">
              <label className="block text-xs font-semibold text-[#555555] mb-1">
                {resumes.length > 0 ? "Or upload a new PDF version:" : "Upload your resume PDF:"}
              </label>
              <div className="border-2 border-dashed border-[#E4DDEA] hover:border-[#7657B8] rounded-xl p-4 text-center cursor-pointer bg-[#FAF9FC] transition-colors">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                  className="hidden"
                  id="resume-upload"
                />
                <label htmlFor="resume-upload" className="cursor-pointer block space-y-1">
                  <Upload className="w-5 h-5 text-[#7657B8] mx-auto" />
                  <span className="text-xs font-semibold text-[#111111] block">
                    {uploadFile ? uploadFile.name : "Click to browse and upload PDF"}
                  </span>
                  <span className="text-[10px] text-[#555555] block">Supported format: PDF up to 10MB</span>
                </label>
              </div>
            </div>
          </div>

          {/* 2. Job Description Selection Card */}
          <div className="bg-white p-6 rounded-2xl border border-[#E4DDEA] shadow-xs space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-sm font-bold text-[#111111] flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-[#7657B8]" />
                Step 2: Target Job Description
              </h2>

              {savedJobs.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#555555]">Autofill from saved:</span>
                  <select
                    value={selectedJobId}
                    onChange={handleSelectJob}
                    className="px-2.5 py-1 rounded-lg border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC]"
                  >
                    <option value="">-- Choose Job --</option>
                    {savedJobs.map(j => (
                      <option key={j.id} value={j.id}>{j.title} at {j.company}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#111111] mb-1">Target Position Title</label>
                <input
                  type="text"
                  required
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g. Machine Learning Engineer"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#111111] mb-1">Target Company</label>
                <input
                  type="text"
                  required
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="e.g. NovaTech Labs"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#111111] mb-1">Full Job Description Text</label>
              <textarea
                required
                rows={7}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the complete job description including overview, responsibilities, required qualifications, and technical competencies..."
                className="w-full p-3.5 rounded-xl border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] leading-relaxed"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-4 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white font-bold text-sm shadow-md shadow-[#7657B8]/20 transition-all flex items-center justify-center gap-2 hover:scale-101 cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            Execute Semantic Alignment Analysis
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      )}
    </div>
  );
};
