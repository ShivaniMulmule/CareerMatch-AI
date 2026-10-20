import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analysisApi } from '../services/api';
import { AnalysisRecord } from '../types';
import {
  Clock,
  Search,
  Filter,
  Trash2,
  ChevronRight,
  Sparkles,
  Download,
  AlertCircle
} from 'lucide-react';

export const History: React.FC = () => {
  const [analyses, setAnalyses] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [scoreFilter, setScoreFilter] = useState<'all' | 'high' | 'mid' | 'low'>('all');
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyses = async () => {
    try {
      const res = await analysisApi.list();
      setAnalyses(res.analyses);
    } catch (err) {
      setError('Failed to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (!window.confirm('Delete this evaluation record?')) return;
    try {
      await analysisApi.delete(id);
      setAnalyses(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      setError('Failed to delete analysis.');
    }
  };

  const filteredAnalyses = analyses.filter((a) => {
    const matchesSearch =
      a.job_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.resume_filename.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (scoreFilter === 'high') return a.match_score >= 75;
    if (scoreFilter === 'mid') return a.match_score >= 50 && a.match_score < 75;
    if (scoreFilter === 'low') return a.match_score < 50;
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Evaluation Archive</span>
        <h1 className="text-2xl font-bold text-[#111111] mt-0.5">Historical Screening Dossiers</h1>
        <p className="text-xs text-[#555555]">Chronological timeline of your resume matches, feature contributions, and gap metrics.</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#F8ECE7] border border-[#F1D0C5] text-xs text-[#C04828] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white p-4 rounded-2xl border border-[#E4DDEA] shadow-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-[#888888] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by role, company, or resume..."
            className="w-full pl-9 pr-4 py-2 rounded-xl border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8]"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-[#555555]" />
          <span className="text-xs text-[#555555]">Filter Fit:</span>
          <select
            value={scoreFilter}
            onChange={(e) => setScoreFilter(e.target.value as any)}
            className="text-xs px-3 py-1.5 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC]"
          >
            <option value="all">All Evaluations</option>
            <option value="high">High Match (&gt;= 75%)</option>
            <option value="mid">Medium Match (50-74%)</option>
            <option value="low">Low Match (&lt; 50%)</option>
          </select>
        </div>
      </div>

      {/* Table / List */}
      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white border border-[#E4DDEA] text-center space-y-3">
          <Clock className="w-8 h-8 text-[#888888] mx-auto" />
          <h3 className="font-bold text-sm text-[#111111]">No historical evaluations found</h3>
          <p className="text-xs text-[#555555]">Try adjusting your search query or run a new resume analysis.</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-[#E4DDEA] overflow-hidden shadow-xs">
          <div className="divide-y divide-[#F0EDF5]">
            {filteredAnalyses.map((a) => (
              <div key={a.id} className="p-5 flex flex-col sm:flex-row justify-between sm:items-center gap-4 hover:bg-[#FAF9FC] transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-[#111111]">{a.job_title}</span>
                    <span className="text-xs text-[#555555]">• {a.company}</span>
                  </div>
                  <div className="text-[11px] text-[#777777] flex items-center gap-2">
                    <span>Resume: {a.resume_filename}</span>
                    <span>•</span>
                    <span>Date: {a.created_at.slice(0, 10)}</span>
                    <span>•</span>
                    <span>Model: {a.model_version}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-6">
                  <div className="text-right">
                    <div className="text-lg font-black text-[#111111]">{a.match_score.toFixed(1)}%</div>
                    <span className="text-[10px] font-semibold text-[#7657B8] bg-[#EDE5F8] px-2 py-0.5 rounded-full">
                      {a.fit_category}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <a
                      href={analysisApi.getReportUrl(a.id)}
                      target="_blank"
                      rel="noreferrer"
                      title="Download PDF"
                      className="p-2 rounded-lg text-[#555555] hover:text-[#7657B8] hover:bg-[#EDE5F8]"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                    <button
                      onClick={(e) => handleDelete(a.id, e)}
                      title="Delete record"
                      className="p-2 rounded-lg text-[#555555] hover:text-[#C04828] hover:bg-[#F8ECE7]"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <Link
                      to={`/results/${a.id}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-[#EDE5F8] text-[#7657B8] font-semibold text-xs hover:bg-[#7657B8] hover:text-white transition-colors"
                    >
                      Dossier <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
