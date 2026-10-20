import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, HeartHandshake, Cpu, Terminal } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-[#E4DDEA] mt-20 pt-12 pb-8 text-sm text-[#555555]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <span className="font-bold text-base text-[#111111]">CareerMatch AI</span>
              <span className="text-[11px] bg-[#EDE5F8] text-[#7657B8] px-2 py-0.5 rounded-full font-semibold">
                SaaS v1.0
              </span>
            </div>
            <p className="text-xs text-[#555555] max-w-md leading-relaxed mb-4">
              "Know Your Job Fit. Before You Apply." Semantic resume-to-job alignment,
              evidence-based skill gap detection, and model interpretability powered by
              Sentence-BERT, XGBoost, and SHAP.
            </p>
            <div className="p-3 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA] text-[11px] text-[#555555] flex items-start gap-2 max-w-lg">
              <ShieldCheck className="w-4 h-4 text-[#7657B8] shrink-0 mt-0.5" />
              <span>
                <strong>Responsible AI Notice:</strong> CareerMatch AI provides informational alignment insights.
                It does not make automated employment decisions and does not guarantee job offers.
              </span>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-xs uppercase tracking-wider text-[#111111] mb-3">Platform</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/analyze" className="hover:text-[#7657B8] transition-colors">Analyze Resume Fit</Link></li>
              <li><Link to="/resumes" className="hover:text-[#7657B8] transition-colors">Resume Versioning</Link></li>
              <li><Link to="/jobs" className="hover:text-[#7657B8] transition-colors">Job Tracker Board</Link></li>
              <li><Link to="/recommendations" className="hover:text-[#7657B8] transition-colors">Upskill Recommendations</Link></li>
              <li><Link to="/skills" className="hover:text-[#7657B8] transition-colors">Skill Analytics</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-xs uppercase tracking-wider text-[#111111] mb-3">Research & Ethics</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/about" className="hover:text-[#7657B8] transition-colors">AI System Architecture</Link></li>
              <li><Link to="/privacy" className="hover:text-[#7657B8] transition-colors">Responsible AI Disclosure</Link></li>
              <li><a href="/docs" target="_blank" rel="noreferrer" className="hover:text-[#7657B8] transition-colors flex items-center gap-1"><Terminal className="w-3 h-3" /> FastAPI Documentation</a></li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-[#F0EDF5] flex flex-col sm:flex-row justify-between items-center text-xs text-[#777777] gap-3">
          <p>© {new Date().getFullYear()} CareerMatch AI — B.Tech Capstone Project in Artificial Intelligence & Data Science.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-[#7657B8]" /> S-BERT + XGBoost + SHAP</span>
            <span>Zero Keyword Matching</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
