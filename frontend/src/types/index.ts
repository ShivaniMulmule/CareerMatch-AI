export interface User {
  id: string;
  email: string;
  full_name: string;
  target_role: string;
  experience_level: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Resume {
  id: string;
  user_id: string;
  original_filename: string;
  stored_filename: string;
  file_size_bytes: number;
  char_count: number;
  word_count: number;
  detected_role?: string;
  experience_summary?: {
    total_years_num?: number;
    total_years_display?: string;
    detected_titles?: string[];
    internships?: string[];
    has_internships?: boolean;
    leadership_highlights?: string[];
    has_leadership?: boolean;
  };
  education_summary?: {
    degree?: string;
    tier?: string;
    field?: string;
    institution?: string;
    graduation_year?: string;
    education_display?: string;
  };
  extracted_text_preview: string;
  storage_provider: string;
  download_url: string;
  created_at: string;
  is_active: boolean;
}

export interface Job {
  id: string;
  user_id: string;
  title: string;
  company: string;
  location: string;
  job_description: string;
  required_experience_years: number;
  status: 'Saved' | 'Applied' | 'Interview' | 'Offer' | 'Rejected';
  created_at: string;
  updated_at: string;
}

export interface DimensionScores {
  semantic_alignment: number;
  capability_alignment: number;
  experience_alignment: number;
  education_alignment: number;
  project_alignment: number;
}

export interface FeatureImpact {
  feature_name: string;
  display_name: string;
  feature_value: number;
  shap_impact: number;
  direction: 'positive' | 'negative' | 'neutral';
  explanation_text: string;
}

export interface ShapExplanation {
  base_value: number;
  feature_impacts: FeatureImpact[];
  top_positive_drivers: FeatureImpact[];
  top_negative_detractors: FeatureImpact[];
  total_shap_adjustment: number;
}

export interface RequirementEvaluation {
  requirement: string;
  best_evidence: string;
  similarity_score: number;
  coverage_status: 'Strongly Demonstrated' | 'Partially Demonstrated' | 'Not Clearly Demonstrated' | string;
  status?: string;
  match_category?: string;
  confidence?: number;
  inferred_from?: string;
  reason?: string;
  is_explicit?: boolean;
  is_related?: boolean;
  is_gap: boolean;
}

export interface ProjectEvaluation {
  title: string;
  description_snippet: string;
  semantic_similarity: number;
  relevance_score: number;
  alignment_tier: 'High' | 'Moderate' | 'Low';
}

export interface RecommendationsData {
  summary: string;
  recommended_projects: Array<{
    title: string;
    description: string;
    target_gap?: string;
  }>;
  recommended_courses: Array<{
    title: string;
    provider: string;
    level: string;
    url: string;
    closes_gap?: string;
  }>;
  certifications: string[];
  resume_enhancements: string[];
}

export interface AnalysisRecord {
  id: string;
  user_id: string;
  resume_id?: string;
  resume_filename: string;
  job_id?: string;
  job_title: string;
  company: string;
  match_score: number;
  fit_category: string;
  fit_description: string;
  executive_reasoning?: string;
  badge_color: string;
  model_version: string;
  dimension_scores: DimensionScores;
  shap_explanation: ShapExplanation;
  nlp_extractions: {
    skill_gap_results?: {
      total_requirements: number;
      strongly_demonstrated_count: number;
      partially_demonstrated_count: number;
      not_demonstrated_count: number;
      coverage_percentage: number;
      explicit_matches?: string[];
      related_matches?: string[];
      true_gaps?: string[];
      explicit_skill_match_ratio?: number;
      related_skill_match_ratio?: number;
      true_skill_gap_ratio?: number;
      skill_ontology_coverage?: number;
      requirement_evaluations: RequirementEvaluation[];
      thresholds_used?: Record<string, string>;
    };
    experience_compatibility?: {
      status: string;
      score: number;
      reason: string;
      candidate_years: number;
      jd_min_years: number;
      jd_max_years?: number;
      exceeds: boolean;
      is_gap: boolean;
    };
    project_analysis?: {
      project_count: number;
      overall_project_relevance: number;
      project_relevance_pct: number;
      evaluated_projects: ProjectEvaluation[];
    };
    experience_details?: any;
    education_details?: any;
  };
  recommendations: RecommendationsData;
  created_at: string;
}

export interface SystemHealth {
  status: string;
  product_name: string;
  tagline: string;
  project_title: string;
  timestamp: string;
  database_mode: string;
  storage_mode: string;
  model_version: string;
  model_algorithm: string;
  features_count: number;
  zero_keyword_matching_guarantee: boolean;
  environment: string;
}
