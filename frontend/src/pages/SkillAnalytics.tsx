import React, { useState, useEffect } from 'react';
import { analysisApi } from '../services/api';
import { AnalysisRecord } from '../types';
import {
  Layers,
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  Sparkles
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

export const SkillAnalytics: React.FC = () => {
  const [analyses, setAnalyses] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        const res = await analysisApi.list();
        setAnalyses(res.analyses);
      } catch (err) {
        console.error('Failed to load analyses:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalyses();
  }, []);

  // Aggregate demonstrated vs gap frequencies
  const gapStats: Record<string, { count: number; category: string }> = {};
  const strongStats: Record<string, { count: number }> = {};

  analyses.forEach((a) => {
    const evals = a.nlp_extractions?.skill_gap_results?.requirement_evaluations || [];
    evals.forEach((e) => {
      const label = e.requirement.slice(0, 35) + '...';
      if (e.is_gap) {
        if (!gapStats[label]) gapStats[label] = { count: 0, category: e.coverage_status };
        gapStats[label].count += 1;
      } else {
        if (!strongStats[label]) strongStats[label] = { count: 0 };
        strongStats[label].count += 1;
      }
    });
  });

  const chartData = Object.entries(gapStats).slice(0, 6).map(([label, info]) => ({
    name: label,
    occurrences: info.count
  }));

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Candidate Competency Matrix</span>
        <h1 className="text-2xl font-bold text-[#111111] mt-0.5">Skill Gap & Strength Analytics</h1>
        <p className="text-xs text-[#555555]">
          Aggregated across all {analyses.length} job analyses to identify your recurring competitive strengths and market gaps.
        </p>
      </div>

      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
        </div>
      ) : analyses.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white border border-[#E4DDEA] text-center space-y-3">
          <Layers className="w-8 h-8 text-[#888888] mx-auto" />
          <h3 className="font-bold text-sm text-[#111111]">No evaluation data to analyze</h3>
          <p className="text-xs text-[#555555]">Run at least one job analysis to view aggregated competency distributions.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Chart Card */}
          <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-[#111111] flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-[#7657B8]" />
              Most Frequent Market Gaps Across Your Target Roles
            </h3>
            <p className="text-xs text-[#555555]">Number of times each capability gap appeared across evaluated job descriptions.</p>

            <div className="h-64 w-full bg-[#FAF9FC] p-4 rounded-2xl border border-[#E4DDEA]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 20, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E4DDEA" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#555555' }} angle={-15} textAnchor="end" />
                  <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: '#555555' }} />
                  <Tooltip contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E4DDEA', borderRadius: '8px', fontSize: '12px' }} />
                  <Bar dataKey="occurrences" fill="#C04828" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Strengths vs Gaps Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="bg-white p-6 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-4">
              <h4 className="text-xs font-bold text-[#137333] flex items-center gap-1.5 uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" />
                Verified Demonstrated Competencies
              </h4>
              <ul className="divide-y divide-[#F0EDF5] text-xs">
                {Object.entries(strongStats).slice(0, 5).map(([skill, info], idx) => (
                  <li key={idx} className="py-2.5 flex justify-between items-center text-[#555555]">
                    <span className="truncate pr-2">{skill}</span>
                    <span className="text-[10px] font-bold bg-[#E3F6F1] text-[#137333] px-2 py-0.5 rounded-full shrink-0">
                      {info.count} verified
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Gaps */}
            <div className="bg-white p-6 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-4">
              <h4 className="text-xs font-bold text-[#C04828] flex items-center gap-1.5 uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4" />
                Priority Unverified Capabilities
              </h4>
              <ul className="divide-y divide-[#F0EDF5] text-xs">
                {Object.entries(gapStats).slice(0, 5).map(([skill, info], idx) => (
                  <li key={idx} className="py-2.5 flex justify-between items-center text-[#555555]">
                    <span className="truncate pr-2">{skill}</span>
                    <span className="text-[10px] font-bold bg-[#F8ECE7] text-[#C04828] px-2 py-0.5 rounded-full shrink-0">
                      {info.count} missing
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
