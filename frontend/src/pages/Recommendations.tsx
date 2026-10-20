import React, { useState, useEffect } from 'react';
import { recommendationApi } from '../services/api';
import {
  Award,
  Sparkles,
  BookOpen,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Code
} from 'lucide-react';

export const Recommendations: React.FC = () => {
  const [catalog, setCatalog] = useState<any>({ resources: [], general_advice: [] });
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState<string>('All');

  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const data = await recommendationApi.getCatalog();
        setCatalog(data);
      } catch (err) {
        console.error('Failed to load catalog:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCatalog();
  }, []);

  const resources = catalog.resources || [];
  const skillList = ['All', ...resources.map((r: any) => r.skill)];

  const displayedResources = selectedSkill === 'All'
    ? resources
    : resources.filter((r: any) => r.skill === selectedSkill);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Skill Intelligence</span>
        <h1 className="text-2xl font-bold text-[#111111] mt-0.5">Upskill & Portfolio Blueprints</h1>
        <p className="text-xs text-[#555555]">
          Curated hands-on architectures, bridge specializations, and industry credentials tailored to close semantic gaps.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 pt-2">
        {skillList.map((skill: string) => (
          <button
            key={skill}
            onClick={() => setSelectedSkill(skill)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-colors ${
              selectedSkill === skill
                ? 'bg-[#7657B8] text-white'
                : 'bg-white text-[#555555] border border-[#E4DDEA] hover:border-[#7657B8]'
            }`}
          >
            {skill}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {displayedResources.map((item: any, idx: number) => (
            <div key={idx} className="bg-white p-6 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-6">
              <div className="flex justify-between items-center pb-4 border-b border-[#F0EDF5]">
                <div>
                  <h3 className="text-base font-bold text-[#111111]">{item.skill}</h3>
                  <p className="text-xs text-[#555555] mt-0.5">{item.resume_advice}</p>
                </div>
                <span className="px-3 py-1 rounded-full text-[11px] font-semibold bg-[#EDE5F8] text-[#7657B8]">
                  Curated Blueprint
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Recommended Projects */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-[#111111] uppercase tracking-wider flex items-center gap-1.5">
                    <Code className="w-4 h-4 text-[#7657B8]" />
                    Target Portfolio Project
                  </h4>
                  {(item.recommended_projects || []).map((proj: any, pIdx: number) => (
                    <div key={pIdx} className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] space-y-1.5">
                      <span className="font-bold text-xs text-[#111111] block">{proj.title}</span>
                      <p className="text-[11px] text-[#555555] leading-relaxed">{proj.description}</p>
                    </div>
                  ))}
                </div>

                {/* Courses & Certs */}
                <div className="space-y-4">
                  <div>
                    <h4 className="text-xs font-bold text-[#111111] uppercase tracking-wider flex items-center gap-1.5 mb-2">
                      <BookOpen className="w-4 h-4 text-[#1A73E8]" />
                      Bridge Course Specializations
                    </h4>
                    <div className="space-y-2">
                      {(item.courses || []).map((c: any, cIdx: number) => (
                        <a
                          key={cIdx}
                          href={c.url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-3 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA] hover:border-[#1A73E8] flex justify-between items-center text-xs group block transition-colors"
                        >
                          <div>
                            <span className="font-semibold text-[#111111] group-hover:text-[#1A73E8] block">{c.title}</span>
                            <span className="text-[10px] text-[#777777]">{c.provider} • {c.level}</span>
                          </div>
                          <ExternalLink className="w-3.5 h-3.5 text-[#888888] group-hover:text-[#1A73E8]" />
                        </a>
                      ))}
                    </div>
                  </div>

                  {item.certifications && item.certifications.length > 0 && (
                    <div>
                      <h5 className="text-[11px] font-bold text-[#555555] uppercase tracking-wider mb-1.5">
                        Recognized Certifications
                      </h5>
                      <div className="flex flex-wrap gap-1.5">
                        {item.certifications.map((cert: string, certIdx: number) => (
                          <span key={certIdx} className="text-[10px] bg-[#E7F1FA] text-[#1A73E8] font-semibold px-2.5 py-1 rounded-md">
                            {cert}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
