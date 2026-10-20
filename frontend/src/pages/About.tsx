import React, { useState, useEffect } from 'react';
import { healthApi } from '../services/api';
import { SystemHealth } from '../types';
import {
  BrainCircuit,
  Cpu,
  Database,
  BarChart3,
  Layers,
  Sparkles,
  HelpCircle,
  CheckCircle2,
  Terminal,
  FileCode
} from 'lucide-react';

export const About: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    healthApi.check().then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header */}
      <div>
        <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Technical Architecture & Viva Guide</span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#111111] mt-1">
          How CareerMatch AI Works
        </h1>
        <p className="text-xs sm:text-sm text-[#555555] max-w-2xl mt-2 leading-relaxed">
          Comprehensive explanation of the end-to-end Explainable AI pipeline: from synthetic dataset generation
          and Sentence-BERT embeddings to XGBoost regression and game-theoretic SHAP attributions.
        </p>
      </div>

      {/* Live Health Card */}
      {health && (
        <div className="bg-white p-6 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[#111111] flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-[#7657B8]" />
              Live System Telemetry
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#E3F6F1] text-[#137333]">
              SYSTEM HEALTHY
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA]">
              <span className="text-[10px] text-[#555555] block">Database Mode</span>
              <span className="font-bold text-[#111111] mt-0.5 block">{health.database_mode}</span>
            </div>
            <div className="p-3 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA]">
              <span className="text-[10px] text-[#555555] block">Storage Provider</span>
              <span className="font-bold text-[#111111] mt-0.5 block">{health.storage_mode}</span>
            </div>
            <div className="p-3 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA]">
              <span className="text-[10px] text-[#555555] block">Trained Model</span>
              <span className="font-bold text-[#7657B8] mt-0.5 block truncate">{health.model_version}</span>
            </div>
            <div className="p-3 rounded-xl bg-[#FAF9FC] border border-[#E4DDEA]">
              <span className="text-[10px] text-[#555555] block">Feature Dimensions</span>
              <span className="font-bold text-[#111111] mt-0.5 block">{health.features_count} Semantic Features</span>
            </div>
          </div>
        </div>
      )}

      {/* 6 Technical Subsystems */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-[#111111]">Core System Pipeline</h2>

        {/* 1. Dataset Generation */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-[#7657B8]">
            <Database className="w-4 h-4" />
            1. Automated Synthetic Dataset Generation Pipeline
          </div>
          <p className="text-xs sm:text-sm text-[#555555] leading-relaxed">
            Rather than relying on fake manual CSV rows, CareerMatch AI includes an automated generator (<code>data_generation/generate_dataset.py</code>)
            producing 6,000 realistic resume-job pairs across 13 engineering disciplines and 7 experience levels.
            The ground-truth <code>match_score</code> (0-100) is generated via a controlled multi-dimensional formula combining
            role alignment, capability alignment, experience fit, project depth, and education tier with realistic Gaussian noise.
            <strong>Zero keyword counts or target leakage are used.</strong>
          </p>
        </div>

        {/* 2. Dense Embeddings */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-[#1A73E8]">
            <BrainCircuit className="w-4 h-4" />
            2. Dense Vector Representations (Sentence-BERT all-MiniLM-L6-v2)
          </div>
          <p className="text-xs sm:text-sm text-[#555555] leading-relaxed">
            Standard ATS systems fail because they look for exact word matches (TF-IDF or token intersection).
            CareerMatch AI utilizes a pre-trained Siamese Sentence Transformer mapping resumes and job descriptions into a shared 384-dimensional
            dense metric space. Cosine similarity calculates genuine conceptual alignment, recognizing that <em>"Built predictive pipelines in Scikit-Learn"</em>
            is semantically synonymous with <em>"Experience developing machine learning models"</em>.
          </p>
        </div>

        {/* 3. Feature Engineering */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-[#7657B8]">
            <Layers className="w-4 h-4" />
            3. 14 Multi-Dimensional Semantic Features
          </div>
          <p className="text-xs sm:text-sm text-[#555555] leading-relaxed">
            The inference engine constructs 14 independent semantic and NLP features:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-[#555555] pt-1">
            <div>• <code>resume_job_semantic_similarity</code>: Global S-BERT cosine similarity</div>
            <div>• <code>section_semantic_similarity</code>: Structural section alignment</div>
            <div>• <code>technical_requirement_alignment</code>: Mean requirement evidence score</div>
            <div>• <code>experience_alignment</code>: Non-linear tenure ratio</div>
            <div>• <code>education_alignment</code>: Quantitative degree tier scoring</div>
            <div>• <code>project_alignment</code>: Project-to-responsibility similarity</div>
            <div>• <code>responsibility_alignment</code>: Experience duty similarity</div>
            <div>• <code>role_alignment</code>: Role title semantic proximity</div>
            <div>• <code>seniority_alignment</code>: Seniority expectations matching</div>
            <div>• <code>semantic_skill_coverage</code>: Thresholded capability coverage</div>
            <div>• <code>missing_requirement_semantic_gap</code>: Magnitude of largest gap</div>
            <div>• <code>resume_completeness</code>: Section depth index</div>
            <div>• <code>project_depth</code>: Technical project density</div>
            <div>• <code>internship_alignment</code>: Practical internship factor</div>
          </div>
        </div>

        {/* 4. XGBoost */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-[#137333]">
            <Cpu className="w-4 h-4" />
            4. Gradient Boosted Decision Trees (XGBoost Regressor)
          </div>
          <p className="text-xs sm:text-sm text-[#555555] leading-relaxed">
            The final prediction model is an <code>XGBRegressor</code> trained on the 14 semantic features.
            XGBoost optimizes an ensemble of decision trees minimizing mean squared error with L1/L2 shrinkage regularization:
          </p>
          <div className="p-3 bg-[#FAF9FC] rounded-xl border border-[#E4DDEA] font-mono text-xs text-[#111111]">
            Obj(θ) = ∑ L(y_i, ŷ_i) + ∑ [ γ * T_m + 0.5 * λ * ||w_m||² + α * |w_m| ]
          </div>
        </div>

        {/* 5. SHAP Explainability */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-[#7657B8]">
            <Sparkles className="w-4 h-4" />
            5. Explainable AI via SHAP (SHapley Additive exPlanations)
          </div>
          <p className="text-xs sm:text-sm text-[#555555] leading-relaxed">
            Rather than leaving the score as a black box, CareerMatch AI applies <code>shap.TreeExplainer</code>
            to compute local Shapley additive attributions based on cooperative game theory:
          </p>
          <div className="p-3 bg-[#FAF9FC] rounded-xl border border-[#E4DDEA] font-mono text-xs text-[#111111]">
            f(x) = E[f(x)] + ∑ φ_i(x)
          </div>
          <p className="text-xs text-[#555555]">
            Every feature receives a mathematically rigorous contribution value (+/- points) explaining why the predicted score was obtained.
          </p>
        </div>
      </div>

      {/* B.Tech Viva Preparation Section */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#7657B8]">Viva & Capstone Defense</span>
          <h2 className="text-xl font-bold text-[#111111] mt-0.5">Top B.Tech Viva Questions & Model Answers</h2>
        </div>

        <div className="space-y-4 text-xs sm:text-sm">
          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] space-y-1.5">
            <h4 className="font-bold text-[#111111]">Q1: Why did you not use simple keyword matching or TF-IDF?</h4>
            <p className="text-[#555555] text-xs leading-relaxed">
              <strong>Answer:</strong> Keyword matching and TF-IDF rely on lexical overlap. They fail when synonyms or paraphrased descriptions are used (e.g. "REST microservices with FastAPI" vs "backend web development"). Furthermore, keyword matching encourages unethical keyword stuffing. Dense embeddings from Sentence-BERT capture semantic context in vector space regardless of exact wording.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] space-y-1.5">
            <h4 className="font-bold text-[#111111]">Q2: Why train an XGBoost model instead of just using raw Cosine Similarity?</h4>
            <p className="text-[#555555] text-xs leading-relaxed">
              <strong>Answer:</strong> Cosine similarity measures overall textual semantic proximity, but cannot capture multi-dimensional trade-offs such as experience duration mismatch, degree requirements, or missing key responsibilities. XGBoost combines 14 heterogeneous semantic features, achieving significantly higher $R^2$ and lower MAE than single-dimension cosine similarity alone.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] space-y-1.5">
            <h4 className="font-bold text-[#111111]">Q3: How does SHAP ensure explainability?</h4>
            <p className="text-[#555555] text-xs leading-relaxed">
              <strong>Answer:</strong> SHAP uses Shapley values from cooperative game theory to allocate fair contribution shares to each feature for a given prediction. It satisfies Efficiency, Symmetry, and Additivity axioms, proving that the sum of feature attributions equals the difference between the model's prediction and the base expected score.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-[#FAF9FC] border border-[#E4DDEA] space-y-1.5">
            <h4 className="font-bold text-[#111111]">Q4: How did you avoid target data leakage in feature engineering?</h4>
            <p className="text-[#555555] text-xs leading-relaxed">
              <strong>Answer:</strong> No feature directly incorporates or derives from <code>match_score</code>. All 14 features are computed strictly from the raw input resume text and job description text via NLP parsing and Sentence-BERT vector operations before being passed to XGBoost.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
