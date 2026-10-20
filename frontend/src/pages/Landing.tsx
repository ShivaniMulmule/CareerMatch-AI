import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  CheckCircle2,
  ArrowRight,
  Cpu,
  BarChart3,
  Search,
  ShieldCheck,
  Target,
  FileCheck,
  Award
} from 'lucide-react';

export const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#FAF9FC]">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 md:pt-24 md:pb-28">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
          {/* Tag Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#EDE5F8] text-[#7657B8] text-xs font-semibold tracking-wide mb-6 border border-[#E4DDEA] shadow-xs">
            <Sparkles className="w-3.5 h-3.5" />
            Next-Gen Explainable AI Screening Platform
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-[#111111] tracking-tight leading-[1.15] mb-6">
            Know Your Job Fit. <br className="hidden sm:inline" />
            <span className="text-[#7657B8] bg-clip-text">Before You Apply.</span>
          </h1>

          <p className="text-base sm:text-lg text-[#555555] max-w-2xl mx-auto leading-relaxed mb-8">
            AI-powered resume screening, semantic job matching, transparent SHAP explainability,
            and evidence-backed skill-gap analysis. Stop guessing ATS keywords—understand true semantic alignment.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-14">
            <Link
              to="/analyze"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white font-semibold text-sm shadow-md shadow-[#7657B8]/20 flex items-center justify-center gap-2 transition-all hover:scale-102"
            >
              Analyze My Resume
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/about"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-white hover:bg-[#F8F7FA] text-[#111111] border border-[#E4DDEA] font-semibold text-sm transition-all"
            >
              See How It Works
            </Link>
          </div>

          {/* Interactive UI Mockup Card */}
          <div className="relative mx-auto max-w-4xl p-2 rounded-2xl bg-gradient-to-b from-[#E4DDEA]/60 to-transparent shadow-xl">
            <div className="bg-white rounded-xl border border-[#E4DDEA] p-6 sm:p-8 text-left shadow-sm">
              <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 pb-6 border-b border-[#F0EDF5]">
                <div>
                  <div className="text-xs font-semibold text-[#7657B8] uppercase tracking-wider">Analysis Result Preview</div>
                  <h3 className="text-xl font-bold text-[#111111] mt-0.5">Machine Learning Engineer — Apex Global</h3>
                </div>
                <div className="flex items-center gap-3">
                  <div className="px-4 py-2 rounded-xl bg-[#E3F6F1] border border-[#C6EFE4] text-center">
                    <span className="text-xs text-[#137333] font-medium block leading-none">Job Match Score</span>
                    <span className="text-2xl font-black text-[#137333] leading-tight">88.4%</span>
                  </div>
                  <span className="px-3 py-1.5 rounded-lg bg-[#EDE5F8] text-[#7657B8] font-semibold text-xs">
                    Strong Match
                  </span>
                </div>
              </div>

              {/* 3 Columns Preview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
                <div className="p-4 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA]">
                  <div className="flex items-center gap-2 text-xs font-semibold text-[#111111] mb-2">
                    <Target className="w-4 h-4 text-[#7657B8]" />
                    Semantic Fit Breakdown
                  </div>
                  <div className="space-y-2 text-xs">
                    <div>
                      <div className="flex justify-between text-[#555555] mb-0.5"><span>Core Capabilities</span><span>91%</span></div>
                      <div className="w-full h-1.5 bg-[#EDE5F8] rounded-full overflow-hidden"><div className="h-full bg-[#7657B8] rounded-full" style={{ width: '91%' }}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-[#555555] mb-0.5"><span>Project Relevance</span><span>86%</span></div>
                      <div className="w-full h-1.5 bg-[#EDE5F8] rounded-full overflow-hidden"><div className="h-full bg-[#7657B8] rounded-full" style={{ width: '86%' }}></div></div>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA]">
                  <div className="flex items-center gap-2 text-xs font-semibold text-[#111111] mb-2">
                    <FileCheck className="w-4 h-4 text-[#137333]" />
                    Verified Evidence Snippet
                  </div>
                  <p className="text-[11px] text-[#555555] italic leading-relaxed">
                    "Deployed a containerized FastAPI machine learning inference service to AWS EC2 behind an ALB with MLflow tracking."
                  </p>
                  <span className="inline-block mt-2 text-[10px] font-semibold text-[#137333] bg-[#E3F6F1] px-2 py-0.5 rounded">
                    Strongly Demonstrated (0.84 sim)
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA]">
                  <div className="flex items-center gap-2 text-xs font-semibold text-[#111111] mb-2">
                    <Cpu className="w-4 h-4 text-[#1A73E8]" />
                    SHAP Decision Drivers
                  </div>
                  <ul className="text-[11px] space-y-1 text-[#555555]">
                    <li className="flex justify-between"><span className="truncate">Core Technical Alignment</span><span className="text-[#137333] font-semibold">+4.2 pts</span></li>
                    <li className="flex justify-between"><span className="truncate">Project-to-Role Fit</span><span className="text-[#137333] font-semibold">+3.1 pts</span></li>
                    <li className="flex justify-between"><span className="truncate">Tenure Gap</span><span className="text-[#C04828] font-semibold">-1.2 pts</span></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Semantic vs Keyword Comparison Section */}
      <section className="py-16 bg-white border-y border-[#E4DDEA]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-[#7657B8]">The Technical Difference</span>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#111111] mt-1">Why Simple Keyword Overlap Fails</h2>
            <p className="text-xs sm:text-sm text-[#555555] mt-2">
              Legacy resume parsers look for exact string intersections. CareerMatch AI captures conceptual meaning and contextual execution.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* The Bad: Keyword Scanner */}
            <div className="p-6 rounded-2xl bg-[#F8ECE7]/50 border border-[#F1D0C5]">
              <div className="flex items-center gap-2 text-[#C04828] font-bold text-sm mb-4">
                <span className="w-6 h-6 rounded-full bg-[#F8ECE7] flex items-center justify-center text-xs">✕</span>
                Legacy Keyword Matching (Old ATS)
              </div>
              <ul className="space-y-3 text-xs text-[#555555]">
                <li className="flex items-start gap-2">
                  <span className="text-[#C04828] font-bold">•</span>
                  <span>Fails when candidate wrote <em>"Predictive models in Python & Scikit-learn"</em> but JD says <em>"Machine Learning modeling"</em>.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#C04828] font-bold">•</span>
                  <span>Cannot distinguish superficial keyword stuffing from real hands-on project accomplishments.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#C04828] font-bold">•</span>
                  <span>Treats skill gap analysis as simple string subtraction <code>(Job Skills - Resume Skills)</code>.</span>
                </li>
              </ul>
            </div>

            {/* The Good: Semantic S-BERT */}
            <div className="p-6 rounded-2xl bg-[#E3F6F1]/50 border border-[#C6EFE4]">
              <div className="flex items-center gap-2 text-[#137333] font-bold text-sm mb-4">
                <span className="w-6 h-6 rounded-full bg-[#E3F6F1] flex items-center justify-center text-xs">✓</span>
                CareerMatch AI Semantic Understanding
              </div>
              <ul className="space-y-3 text-xs text-[#555555]">
                <li className="flex items-start gap-2">
                  <span className="text-[#137333] font-bold">•</span>
                  <span>Uses <strong>Sentence-BERT dense vector embeddings</strong> to understand conceptual synonyms and architectural equivalence.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#137333] font-bold">•</span>
                  <span>Evaluates 14 distinct semantic features via a trained <strong>XGBoost Regressor</strong>.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#137333] font-bold">•</span>
                  <span>Provides true <strong>SHAP TreeExplainer feature attributions</strong> and cites verified resume quote evidence.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-20 max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-bold uppercase tracking-wider text-[#7657B8]">Features</span>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#111111] mt-1">Built for Candidate Clarity</h2>
          <p className="text-xs sm:text-sm text-[#555555] mt-2">Comprehensive intelligence tools to inspect and elevate your resume before applying.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-white border border-[#E4DDEA] hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#EDE5F8] text-[#7657B8] flex items-center justify-center mb-4 font-bold">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-[#111111] mb-2">Explainable AI (SHAP)</h3>
            <p className="text-xs text-[#555555] leading-relaxed">
              No black-box mystery. See exactly how each dimension—from experience tenure to project depth—influenced the XGBoost match score.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-[#E4DDEA] hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#E7F1FA] text-[#1A73E8] flex items-center justify-center mb-4 font-bold">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-[#111111] mb-2">Evidence-Based Gap Analysis</h3>
            <p className="text-xs text-[#555555] leading-relaxed">
              Requirements are classified into Strongly, Partially, or Not Demonstrated based on real semantic similarity to your actual resume sentences.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-[#E4DDEA] hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#E3F6F1] text-[#137333] flex items-center justify-center mb-4 font-bold">
              <Award className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-[#111111] mb-2">Targeted Upskill Roadmaps</h3>
            <p className="text-xs text-[#555555] leading-relaxed">
              Receive concrete portfolio project ideas, specific top-rated courses, and resume bullet restructuring advice directly matched to your gaps.
            </p>
          </div>
        </div>

        {/* CTA Banner */}
        <div className="mt-16 p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-[#EDE5F8] via-[#E7F1FA] to-[#FAF9FC] border border-[#E4DDEA] text-center">
          <h3 className="text-2xl sm:text-3xl font-bold text-[#111111] mb-3">Ready to evaluate your resume fit?</h3>
          <p className="text-xs sm:text-sm text-[#555555] max-w-md mx-auto mb-6">
            Upload your resume PDF and analyze it against any target job description in seconds.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white font-semibold text-sm shadow-md shadow-[#7657B8]/20 transition-all hover:scale-102"
          >
            Create Free Account
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
};
