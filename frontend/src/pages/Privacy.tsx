import React from 'react';
import { ShieldCheck, AlertCircle, Info, Scale, Cpu, Database } from 'lucide-react';

export const Privacy: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Ethics & Governance</span>
        <h1 className="text-3xl font-extrabold text-[#111111] mt-1">Responsible AI Disclosure & Privacy</h1>
        <p className="text-xs sm:text-sm text-[#555555]">
          Transparent declaration of model design, synthetic dataset methodology, limitations, and ethical guidelines.
        </p>
      </div>

      {/* Mandatory Statutory Disclaimer Banner */}
      <div className="p-6 rounded-2xl bg-[#EDE5F8] border border-[#E4DDEA] text-[#111111] space-y-2">
        <div className="flex items-center gap-2 text-sm font-bold text-[#7657B8]">
          <ShieldCheck className="w-5 h-5 text-[#7657B8]" />
          Mandatory Responsible AI Statement
        </div>
        <p className="text-xs sm:text-sm leading-relaxed font-medium">
          "CareerMatch AI provides informational resume-to-job alignment insights. It does not make hiring decisions
          and should not be interpreted as a probability of employment."
        </p>
      </div>

      <div className="space-y-6 text-xs sm:text-sm text-[#555555] leading-relaxed">
        {/* Section 1: Synthetic Dataset Transparency */}
        <div className="bg-white p-6 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <h2 className="text-base font-bold text-[#111111] flex items-center gap-2">
            <Database className="w-4 h-4 text-[#7657B8]" />
            1. Synthetic Training Dataset & Benchmark Methodology
          </h2>
          <p>
            The XGBoost model in CareerMatch AI was trained on an automated, reproducible synthetic dataset of 6,000 records
            specifically generated via controlled multi-dimensional semantic alignment logic (seed=42).
          </p>
          <p>
            <strong>Why Synthetic Data?</strong> Proprietary applicant tracking records and real hiring decisions contain
            severe historical biases (e.g., gender, ethnic, or pedigree favoritism) and violate privacy regulations (GDPR/CCPA).
            Controlled synthetic generation allows rigorous mathematical verification of multi-dimensional alignments without privacy risks.
          </p>
        </div>

        {/* Section 2: Model & Embedding Limitations */}
        <div className="bg-white p-6 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <h2 className="text-base font-bold text-[#111111] flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[#1A73E8]" />
            2. Model & Dense Vector Embedding Limitations
          </h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>
              <strong>Sentence-BERT Constraints:</strong> Dense vector representations (all-MiniLM-L6-v2) capture semantic similarity
              based on pre-trained linguistic contexts. They may occasionally overestimate alignment between superficially related technical topics.
            </li>
            <li>
              <strong>Resume Extraction Nuances:</strong> Highly unusual multi-column PDF layouts or graphical resumes may lead to imperfect text parsing. Text-searchable single-column PDFs yield the highest fidelity.
            </li>
            <li>
              <strong>No Guarantee of Recruiter Intent:</strong> Job descriptions often describe "wish-list" requirements rather than strict screening filters. The AI evaluates semantic alignment against the provided text, not undisclosed employer criteria.
            </li>
          </ul>
        </div>

        {/* Section 3: Bias Mitigation & Ethical AI */}
        <div className="bg-white p-6 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <h2 className="text-base font-bold text-[#111111] flex items-center gap-2">
            <Scale className="w-4 h-4 text-[#137333]" />
            3. Bias Mitigation & Explainability Guarantee
          </h2>
          <p>
            To prevent demographic discrimination, CareerMatch AI completely strips personal identifiers (names, contact details, gender markers)
            from the feature vector. The XGBoost model bases predictions strictly on the 14 engineered semantic features.
          </p>
          <p>
            Furthermore, every prediction is paired with <strong>SHAP TreeExplainer attributions</strong>, giving candidates complete
            transparency into which specific dimensions contributed positively or negatively to their score.
          </p>
        </div>
      </div>
    </div>
  );
};
