import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { analysisApi } from '../services/api';
import { AnalysisRecord } from '../types';
import {
  Sparkles,
  Download,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ArrowLeft,
  Quote,
  Layers,
  Award,
  Filter
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ReferenceLine
} from 'recharts';

export const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<AnalysisRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skillFilter, setSkillFilter] = useState<'all' | 'explicit' | 'related' | 'gaps'>('all');

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!id) return;
      try {
        const data = await analysisApi.get(id);
        setAnalysis(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Could not find analysis record.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 flex justify-center">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
          <p className="text-xs text-[#555555]">Compiling explainable analysis report...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-[#F8ECE7] text-[#C04828] flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-[#111111]">Report Not Found</h2>
        <p className="text-xs text-[#555555]">{error || 'Unable to retrieve analysis dossier.'}</p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#7657B8] text-white text-xs font-semibold"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Return to Dashboard
        </Link>
      </div>
    );
  }

  const {
    match_score,
    fit_category,
    fit_description,
    executive_reasoning,
    badge_color,
    dimension_scores,
    shap_explanation,
    nlp_extractions,
    recommendations
  } = analysis;

  const evals = nlp_extractions?.skill_gap_results?.requirement_evaluations || [];
  const expComp = nlp_extractions?.experience_compatibility;

  // Filter skills
  const filteredEvals = evals.filter(item => {
    const isExplicit = item.status === 'EXPLICIT MATCH' || item.is_explicit;
    const isRelated = item.status === 'RELATED MATCH' || item.is_related;
    const isGap = item.status === 'TRUE GAP' || (!isExplicit && !isRelated);

    if (skillFilter === 'explicit') return isExplicit;
    if (skillFilter === 'related') return isRelated;
    if (skillFilter === 'gaps') return isGap;
    return true;
  });

  const explicitCount = evals.filter(i => i.status === 'EXPLICIT MATCH' || i.is_explicit).length;
  const relatedCount = evals.filter(i => i.status === 'RELATED MATCH' || i.is_related).length;
  const gapCount = evals.filter(i => i.status === 'TRUE GAP' || (!i.is_explicit && !i.is_related)).length;

  // Prepare SHAP chart data
  const shapChartData = (shap_explanation?.feature_impacts || []).slice(0, 8).map(imp => ({
    name: imp.display_name,
    impact: imp.shap_impact,
    value: imp.feature_value,
    explanation: imp.explanation_text
  }));

  const reportDownloadUrl = analysisApi.getReportUrl(analysis.id);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className="p-2 rounded-xl bg-white border border-[#E4DDEA] text-[#555555] hover:text-[#111111] hover:border-[#7657B8] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="text-xs text-[#555555] flex items-center gap-1.5">
              <span>{analysis.company}</span>
              <span>•</span>
              <span>{analysis.resume_filename}</span>
            </div>
            <h1 className="text-xl font-bold text-[#111111]">{analysis.job_title}</h1>
          </div>
        </div>

        <a
          href={reportDownloadUrl}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white hover:bg-[#F8F7FA] border border-[#E4DDEA] text-[#111111] font-semibold text-xs shadow-xs transition-colors"
        >
          <Download className="w-3.5 h-3.5 text-[#7657B8]" />
          Download Official PDF Report
        </a>
      </div>

      {/* 1. Overall Match Score Card */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="space-y-3 text-center md:text-left flex-1">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8]">
            XGBoost Machine Learning Prediction
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-[#111111]">Job Match Assessment</h2>
          <p className="text-xs sm:text-sm text-[#555555] max-w-xl leading-relaxed">{fit_description}</p>
          <div className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-[#EDE5F8] text-[#7657B8]">
            Fit Classification: {fit_category}
          </div>

          {/* Executive Reasoning Narrative */}
          {executive_reasoning && (
            <div className="mt-3 p-4 rounded-2xl bg-[#F8F6FC] border border-[#E4DDEA] space-y-1 text-left">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                Executive AI Fit Synthesis
              </span>
              <p className="text-xs text-[#333333] leading-relaxed">{executive_reasoning}</p>
            </div>
          )}
        </div>

        <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] w-full md:w-56 text-center shrink-0">
          <div className="text-5xl font-black text-[#111111] tracking-tight">
            {match_score.toFixed(1)}<span className="text-2xl text-[#7657B8]">%</span>
          </div>
          <span className="text-[11px] font-semibold text-[#555555] mt-1">Predicted Alignment</span>
          <div className="w-full bg-[#EDE5F8] h-2 rounded-full mt-3 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000"
              style={{ width: `${match_score}%`, backgroundColor: badge_color || '#7657B8' }}
            ></div>
          </div>
          <span className="text-[10px] text-[#777777] mt-2 block">Model: {analysis.model_version}</span>
        </div>
      </div>

      {/* 2. Multi-Dimensional Alignment Breakdown */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8]">Multi-Dimensional Alignment</span>
          <h3 className="text-lg font-bold text-[#111111] mt-0.5">Where Your Profile Stands</h3>
          <p className="text-xs text-[#555555]">Derived from dense Sentence-BERT vector representations and structural parsing.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
            <span className="text-xs text-[#555555] font-semibold block">Semantic Fit</span>
            <div className="text-xl font-bold text-[#111111] mt-1">{dimension_scores?.semantic_alignment}%</div>
            <div className="w-full h-1.5 bg-[#EDE5F8] rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-[#7657B8] rounded-full" style={{ width: `${dimension_scores?.semantic_alignment}%` }}></div>
            </div>
            <span className="text-[10px] text-[#777777] block mt-2">Dense S-BERT text similarity</span>
          </div>

          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
            <span className="text-xs text-[#555555] font-semibold block">Skill Ontology</span>
            <div className="text-xl font-bold text-[#111111] mt-1">{dimension_scores?.capability_alignment}%</div>
            <div className="w-full h-1.5 bg-[#EDE5F8] rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-[#7657B8] rounded-full" style={{ width: `${dimension_scores?.capability_alignment}%` }}></div>
            </div>
            <span className="text-[10px] text-[#777777] block mt-2">Explicit & related coverage</span>
          </div>

          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
            <span className="text-xs text-[#555555] font-semibold block">Experience Fit</span>
            <div className="text-xl font-bold text-[#111111] mt-1">{dimension_scores?.experience_alignment}%</div>
            <div className="w-full h-1.5 bg-[#EDE5F8] rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-[#7657B8] rounded-full" style={{ width: `${dimension_scores?.experience_alignment}%` }}></div>
            </div>
            <span className="text-[10px] text-[#777777] block mt-2">Fair tenure compatibility</span>
          </div>

          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
            <span className="text-xs text-[#555555] font-semibold block">Education Tier</span>
            <div className="text-xl font-bold text-[#111111] mt-1">{dimension_scores?.education_alignment}%</div>
            <div className="w-full h-1.5 bg-[#EDE5F8] rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-[#7657B8] rounded-full" style={{ width: `${dimension_scores?.education_alignment}%` }}></div>
            </div>
            <span className="text-[10px] text-[#777777] block mt-2">Degree level match</span>
          </div>

          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
            <span className="text-xs text-[#555555] font-semibold block">Project Alignment</span>
            <div className="text-xl font-bold text-[#111111] mt-1">{dimension_scores?.project_alignment}%</div>
            <div className="w-full h-1.5 bg-[#EDE5F8] rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-[#7657B8] rounded-full" style={{ width: `${dimension_scores?.project_alignment}%` }}></div>
            </div>
            <span className="text-[10px] text-[#777777] block mt-2">Duty overlap in projects</span>
          </div>
        </div>
      </div>

      {/* 3. Fair Experience Compatibility Block */}
      {expComp && (
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8]">Fair Seniority Compatibility</span>
              <h3 className="text-lg font-bold text-[#111111] mt-0.5">Experience Alignment Assessment</h3>
            </div>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold ${
              ['MATCH', 'STRONG MATCH', 'EXCEEDS PREFERRED RANGE'].includes(expComp.status)
                ? 'text-[#137333] bg-[#E3F6F1]'
                : 'text-[#C04828] bg-[#F8ECE7]'
            }`}>
              <CheckCircle2 className="w-4 h-4" />
              {expComp.status}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
              <span className="text-[11px] text-[#555555] block">Candidate Experience</span>
              <span className="text-base font-bold text-[#111111]">{expComp.candidate_years.toFixed(1)} years</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
              <span className="text-[11px] text-[#555555] block">Stated Requirement</span>
              <span className="text-base font-bold text-[#111111]">
                {expComp.jd_min_years === 0 ? 'No prior experience required' : `${expComp.jd_min_years.toFixed(1)}+ years`}
              </span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA]">
              <span className="text-[11px] text-[#555555] block">Seniority Protection</span>
              <span className="text-xs font-semibold text-[#137333]">Zero Negative Penalty for Exceeding</span>
            </div>
          </div>

          <p className="text-xs text-[#555555] leading-relaxed bg-[#FAF9FC] p-3.5 rounded-xl border border-[#E4DDEA]">
            {expComp.reason}
          </p>
        </div>
      )}

      {/* 4. 3-Tier Skill Gap & Ontology Matrix */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8]">Granular Evidence Verification</span>
            <h3 className="text-lg font-bold text-[#111111] mt-0.5">3-Tier Skill Gap & Ontology Intelligence</h3>
            <p className="text-xs text-[#555555]">
              Separates explicit skills, related/transferable competencies, and true gaps with verified resume quotes.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 p-1 bg-[#FAF9FC] border border-[#E4DDEA] rounded-xl self-start sm:self-auto text-xs">
            <button
              onClick={() => setSkillFilter('all')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${skillFilter === 'all' ? 'bg-[#7657B8] text-white' : 'text-[#555555] hover:text-[#111111]'}`}
            >
              All ({evals.length})
            </button>
            <button
              onClick={() => setSkillFilter('explicit')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${skillFilter === 'explicit' ? 'bg-[#137333] text-white' : 'text-[#555555] hover:text-[#137333]'}`}
            >
              Explicit ({explicitCount})
            </button>
            <button
              onClick={() => setSkillFilter('related')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${skillFilter === 'related' ? 'bg-[#1A73E8] text-white' : 'text-[#555555] hover:text-[#1A73E8]'}`}
            >
              Related ({relatedCount})
            </button>
            <button
              onClick={() => setSkillFilter('gaps')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${skillFilter === 'gaps' ? 'bg-[#C04828] text-white' : 'text-[#555555] hover:text-[#C04828]'}`}
            >
              True Gaps ({gapCount})
            </button>
          </div>
        </div>

        <div className="divide-y divide-[#F0EDF5] border border-[#E4DDEA] rounded-2xl overflow-hidden">
          {filteredEvals.map((item, idx) => {
            const isExplicit = item.status === 'EXPLICIT MATCH' || item.is_explicit;
            const isRelated = item.status === 'RELATED MATCH' || item.is_related;
            
            const badgeClass = isExplicit
              ? 'text-[#137333] bg-[#E3F6F1]'
              : (isRelated ? 'text-[#1A73E8] bg-[#E7F1FA]' : 'text-[#C04828] bg-[#F8ECE7]');
            
            const IconComponent = isExplicit
              ? CheckCircle2
              : (isRelated ? Sparkles : XCircle);

            const displayCategory = isExplicit
              ? 'EXPLICIT MATCH'
              : (isRelated ? 'RELATED / INFERRED MATCH' : 'TRUE GAP');

            return (
              <div key={idx} className="p-5 space-y-2.5 hover:bg-[#FAF9FC] transition-colors">
                <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                  <span className="text-xs font-bold text-[#111111] flex items-center gap-2">
                    <span className="text-[#7657B8]">Requirement #{idx + 1}:</span>
                    {item.requirement}
                  </span>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold ${badgeClass}`}>
                      <IconComponent className="w-3.5 h-3.5" />
                      {displayCategory}
                    </span>
                    <span className="text-[10px] text-[#777777]">
                      ({(item.similarity_score * 100).toFixed(0)}% sim)
                    </span>
                  </div>
                </div>

                {/* Ontology & Transferability Reason */}
                {item.reason && (
                  <div className="p-2.5 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA] text-xs text-[#333333]">
                    <span className="font-semibold text-[#111111] text-[11px] block">Relationship Reasoning:</span>
                    <p className="mt-0.5 leading-relaxed text-[11px]">{item.reason}</p>
                  </div>
                )}

                {/* Evidence Quote */}
                <div className="flex items-start gap-2 bg-white p-3 rounded-xl border border-[#E4DDEA] text-xs text-[#555555]">
                  <Quote className="w-3.5 h-3.5 text-[#7657B8] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#111111] text-[11px] block">Verified Resume Evidence:</span>
                    <p className="italic text-[11px] mt-0.5 leading-relaxed">
                      "{item.best_evidence}"
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. SHAP Explainability Section */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8]">Transparent Machine Learning</span>
          <h3 className="text-lg font-bold text-[#111111] mt-0.5">Why This Score? (SHAP Feature Attributions)</h3>
          <p className="text-xs text-[#555555]">
            True local Shapley additive values from the XGBoost model. Shows exact point adjustments made to the model's base expectation.
          </p>
        </div>

        {/* SHAP Chart */}
        <div className="h-72 w-full bg-[#FAF9FC] p-4 rounded-2xl border border-[#E4DDEA]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={shapChartData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 140, bottom: 5 }}
            >
              <XAxis type="number" tick={{ fontSize: 10, fill: '#555555' }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#111111' }} width={130} />
              <Tooltip
                formatter={(value: any) => [`${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)} pts`, 'SHAP Impact']}
                contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E4DDEA', borderRadius: '8px', fontSize: '12px' }}
              />
              <ReferenceLine x={0} stroke="#888888" strokeWidth={1} />
              <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                {shapChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.impact >= 0 ? '#137333' : '#C04828'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* SHAP Drivers List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-[#E3F6F1]/40 border border-[#C6EFE4] space-y-2">
            <h4 className="text-xs font-bold text-[#137333] flex items-center gap-1.5 uppercase tracking-wider">
              <CheckCircle2 className="w-4 h-4" />
              Top Positive Drivers
            </h4>
            <ul className="text-xs space-y-1.5 text-[#555555]">
              {(shap_explanation?.top_positive_drivers || []).slice(0, 3).map((d, i) => (
                <li key={i} className="flex justify-between items-start">
                  <span>• {d.display_name}</span>
                  <span className="font-bold text-[#137333] shrink-0">+{d.shap_impact.toFixed(2)} pts</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 rounded-2xl bg-[#F8ECE7]/40 border border-[#F1D0C5] space-y-2">
            <h4 className="text-xs font-bold text-[#C04828] flex items-center gap-1.5 uppercase tracking-wider">
              <AlertTriangle className="w-4 h-4" />
              Top Score Detractors
            </h4>
            <ul className="text-xs space-y-1.5 text-[#555555]">
              {(shap_explanation?.top_negative_detractors || []).slice(0, 3).map((d, i) => (
                <li key={i} className="flex justify-between items-start">
                  <span>• {d.display_name}</span>
                  <span className="font-bold text-[#C04828] shrink-0">{d.shap_impact.toFixed(2)} pts</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* 6. Actionable Recommendations */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8]">Actionable Upskill Plan</span>
          <h3 className="text-lg font-bold text-[#111111] mt-0.5">Recommended Actions to Close Gaps</h3>
          <p className="text-xs text-[#555555]">{recommendations?.summary}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Projects */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-[#111111] uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-[#7657B8]" />
              Priority Portfolio Projects
            </h4>
            <div className="space-y-3">
              {(recommendations?.recommended_projects || []).map((proj, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] space-y-1.5">
                  <span className="font-bold text-xs text-[#111111] block">{proj.title}</span>
                  <p className="text-xs text-[#555555] leading-relaxed">{proj.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Courses */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-[#111111] uppercase tracking-wider flex items-center gap-1.5">
              <Award className="w-4 h-4 text-[#7657B8]" />
              Targeted Bridge Learning
            </h4>
            <div className="space-y-3">
              {(recommendations?.recommended_courses || []).map((c, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] flex justify-between items-center">
                  <div>
                    <span className="font-bold text-xs text-[#111111] block">{c.title}</span>
                    <span className="text-[11px] text-[#555555]">{c.provider} • {c.level}</span>
                  </div>
                  {c.url && (
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-1.5 rounded-xl bg-white border border-[#E4DDEA] hover:border-[#7657B8] text-xs font-medium text-[#7657B8] shrink-0"
                    >
                      View Course
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
