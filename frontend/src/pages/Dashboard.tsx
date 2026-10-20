import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { analysisApi, jobApi, resumeApi } from '../services/api';
import { AnalysisRecord, Job, Resume } from '../types';
import {
  Sparkles,
  BarChart3,
  Briefcase,
  FileText,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Clock,
  CheckCircle2,
  Layers,
  ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState<AnalysisRecord[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [aRes, jRes, rRes] = await Promise.all([
          analysisApi.list(),
          jobApi.list(),
          resumeApi.list()
        ]);
        setAnalyses(aRes.analyses);
        setJobs(jRes.jobs);
        setResumes(rRes.resumes);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 flex justify-center">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
          <p className="text-xs text-[#555555]">Loading dashboard metrics...</p>
        </div>
      </div>
    );
  }

  // Calculate Metrics from actual user data
  const totalAnalyses = analyses.length;
  const avgMatchScore = totalAnalyses > 0
    ? (analyses.reduce((acc, curr) => acc + curr.match_score, 0) / totalAnalyses).toFixed(1)
    : '0.0';
  const savedJobsCount = jobs.length;
  const appliedCount = jobs.filter(j => j.status !== 'Saved').length;

  // Identify most recurrent skill gap across analyses
  const gapFrequency: Record<string, number> = {};
  analyses.forEach(a => {
    const evals = a.nlp_extractions?.skill_gap_results?.requirement_evaluations || [];
    evals.forEach(e => {
      if (e.is_gap) {
        const shortName = e.requirement.slice(0, 30) + '...';
        gapFrequency[shortName] = (gapFrequency[shortName] || 0) + 1;
      }
    });
  });

  const sortedGaps = Object.entries(gapFrequency).sort((a, b) => b[1] - a[1]);
  const topSkillGap = sortedGaps.length > 0 ? sortedGaps[0][0] : 'None Detected';

  // Chart data: Dimensional Averages
  const chartData = [
    {
      dimension: 'Semantic',
      score: totalAnalyses > 0
        ? Math.round(analyses.reduce((acc, a) => acc + (a.dimension_scores?.semantic_alignment || 0), 0) / totalAnalyses)
        : 0
    },
    {
      dimension: 'Capability',
      score: totalAnalyses > 0
        ? Math.round(analyses.reduce((acc, a) => acc + (a.dimension_scores?.capability_alignment || 0), 0) / totalAnalyses)
        : 0
    },
    {
      dimension: 'Experience',
      score: totalAnalyses > 0
        ? Math.round(analyses.reduce((acc, a) => acc + (a.dimension_scores?.experience_alignment || 0), 0) / totalAnalyses)
        : 0
    },
    {
      dimension: 'Education',
      score: totalAnalyses > 0
        ? Math.round(analyses.reduce((acc, a) => acc + (a.dimension_scores?.education_alignment || 0), 0) / totalAnalyses)
        : 0
    },
    {
      dimension: 'Projects',
      score: totalAnalyses > 0
        ? Math.round(analyses.reduce((acc, a) => acc + (a.dimension_scores?.project_alignment || 0), 0) / totalAnalyses)
        : 0
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-gradient-to-r from-[#EDE5F8] via-[#E7F1FA] to-white p-6 rounded-2xl border border-[#E4DDEA]">
        <div>
          <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Candidate Workspace</span>
          <h1 className="text-2xl font-bold text-[#111111] mt-0.5">Welcome back, {user?.full_name}</h1>
          <p className="text-xs text-[#555555] mt-1">
            Targeting: <strong className="text-[#111111]">{user?.target_role}</strong> ({user?.experience_level})
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/analyze"
            className="px-4 py-2.5 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white font-semibold text-xs shadow-sm shadow-[#7657B8]/20 flex items-center gap-2 transition-all hover:scale-102"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Analyze New Job
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-[#E4DDEA] shadow-xs">
          <div className="flex items-center justify-between text-[#555555] text-xs font-semibold">
            <span>Total Analyses</span>
            <FileText className="w-4 h-4 text-[#7657B8]" />
          </div>
          <div className="text-2xl font-bold text-[#111111] mt-2">{totalAnalyses}</div>
          <span className="text-[10px] text-[#555555] block mt-0.5">Evaluated positions</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-[#E4DDEA] shadow-xs">
          <div className="flex items-center justify-between text-[#555555] text-xs font-semibold">
            <span>Avg Match Score</span>
            <TrendingUp className="w-4 h-4 text-[#137333]" />
          </div>
          <div className="text-2xl font-bold text-[#111111] mt-2">{avgMatchScore}%</div>
          <span className="text-[10px] text-[#137333] font-medium block mt-0.5">XGBoost regression</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-[#E4DDEA] shadow-xs">
          <div className="flex items-center justify-between text-[#555555] text-xs font-semibold">
            <span>Saved Jobs</span>
            <Briefcase className="w-4 h-4 text-[#1A73E8]" />
          </div>
          <div className="text-2xl font-bold text-[#111111] mt-2">{savedJobsCount}</div>
          <span className="text-[10px] text-[#555555] block mt-0.5">Tracked postings</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-[#E4DDEA] shadow-xs">
          <div className="flex items-center justify-between text-[#555555] text-xs font-semibold">
            <span>In Pipeline</span>
            <CheckCircle2 className="w-4 h-4 text-[#7657B8]" />
          </div>
          <div className="text-2xl font-bold text-[#111111] mt-2">{appliedCount}</div>
          <span className="text-[10px] text-[#555555] block mt-0.5">Applied / Interview</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-[#E4DDEA] shadow-xs">
          <div className="flex items-center justify-between text-[#555555] text-xs font-semibold">
            <span>Primary Skill Gap</span>
            <AlertTriangle className="w-4 h-4 text-[#C04828]" />
          </div>
          <div className="text-xs font-bold text-[#C04828] mt-3 truncate" title={topSkillGap}>
            {topSkillGap}
          </div>
          <span className="text-[10px] text-[#555555] block mt-0.5">Most common gap</span>
        </div>
      </div>

      {/* Main Grid: Chart + Recent Analyses */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Recent Analyses */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-base font-bold text-[#111111] flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#7657B8]" />
              Recent Evaluations
            </h2>
            {totalAnalyses > 0 && (
              <Link to="/history" className="text-xs font-semibold text-[#7657B8] hover:underline flex items-center gap-1">
                View History <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            )}
          </div>

          {totalAnalyses === 0 ? (
            <div className="p-8 rounded-2xl bg-white border border-[#E4DDEA] text-center space-y-3">
              <div className="w-10 h-10 rounded-xl bg-[#EDE5F8] text-[#7657B8] flex items-center justify-center mx-auto font-bold">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-sm text-[#111111]">No analyses yet</h3>
              <p className="text-xs text-[#555555] max-w-sm mx-auto">
                Select or upload your resume and enter a target job description to compute your explainable match score.
              </p>
              <Link
                to="/analyze"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#7657B8] text-white font-semibold text-xs shadow-xs"
              >
                Run First Analysis
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-[#E4DDEA] overflow-hidden shadow-xs">
              <div className="divide-y divide-[#F0EDF5]">
                {analyses.slice(0, 5).map((a) => (
                  <Link
                    key={a.id}
                    to={`/results/${a.id}`}
                    className="p-4 flex items-center justify-between hover:bg-[#FAF9FC] transition-colors group block"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-[#111111] group-hover:text-[#7657B8] transition-colors">
                          {a.job_title}
                        </span>
                        <span className="text-xs text-[#555555]">• {a.company}</span>
                      </div>
                      <div className="text-[11px] text-[#777777] flex items-center gap-2">
                        <span>{a.resume_filename}</span>
                        <span>•</span>
                        <span>{a.created_at ? a.created_at.slice(0, 10) : ''}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <span className="text-base font-extrabold text-[#111111]">{a.match_score.toFixed(1)}%</span>
                        <span className="block text-[10px] font-semibold text-[#7657B8]">{a.fit_category}</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-[#888888] group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Skill Gap Trends & Quick Actions */}
        <div className="space-y-6">
          <div className="bg-white p-5 rounded-2xl border border-[#E4DDEA] shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#111111] mb-4 flex items-center gap-1.5">
              <BarChart3 className="w-4 h-4 text-[#7657B8]" />
              Average Competency Scores
            </h3>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F0EDF5" />
                  <XAxis dataKey="dimension" tick={{ fontSize: 10, fill: '#555555' }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#555555' }} />
                  <Tooltip
                    formatter={(value: any) => [`${value}%`, 'Average Score']}
                    contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E4DDEA', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Bar dataKey="score" fill="#7657B8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-[11px] text-[#777777] text-center mt-2">
              Aggregated across all {totalAnalyses} evaluated analyses
            </p>
          </div>

          {/* Quick Actions Panel */}
          <div className="bg-[#FAF9FC] p-5 rounded-2xl border border-[#E4DDEA] space-y-3">
            <h4 className="text-xs font-bold text-[#111111] uppercase tracking-wider">Quick Actions</h4>
            <div className="space-y-2 text-xs">
              <Link
                to="/resumes"
                className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E4DDEA] hover:border-[#7657B8] transition-colors"
              >
                <span className="font-medium text-[#111111]">Manage Resume Versions ({resumes.length})</span>
                <ChevronRight className="w-3.5 h-3.5 text-[#555555]" />
              </Link>
              <Link
                to="/jobs"
                className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E4DDEA] hover:border-[#7657B8] transition-colors"
              >
                <span className="font-medium text-[#111111]">Manage Target Jobs ({jobs.length})</span>
                <ChevronRight className="w-3.5 h-3.5 text-[#555555]" />
              </Link>
              <Link
                to="/recommendations"
                className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E4DDEA] hover:border-[#7657B8] transition-colors"
              >
                <span className="font-medium text-[#111111]">View Upskill Recommendations</span>
                <ChevronRight className="w-3.5 h-3.5 text-[#555555]" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
