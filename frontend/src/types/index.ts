/**
 * MetaPython TypeScript Type Definitions
 * Comprehensive types for meta-analysis operations
 */

export interface Study {
  id: string;
  label: string;
  effect: number;
  se: number;
  n: number;
  year?: number;
  author?: string;
  weight?: number;
  ci_lower?: number;
  ci_upper?: number;
}

export interface MetaAnalysisResult {
  pooled_effect: number;
  pooled_se: number;
  ci_lower: number;
  ci_upper: number;
  p_value: number;
  z_score: number;
  heterogeneity: HeterogeneityMetrics;
  method: string;
  n_studies: number;
  studies: Study[];
}

export interface HeterogeneityMetrics {
  Q: number;
  Q_p: number;
  I2: number;
  tau2: number;
  tau: number;
  H2?: number;
}

export interface PublicationBiasResult {
  egger_test: {
    intercept: number;
    p_value: number;
    significant: boolean;
  };
  begg_test: {
    statistic: number;
    p_value: number;
    significant: boolean;
  };
  trim_fill?: {
    n_imputed: number;
    adjusted_effect: number;
    imputed_studies: Study[];
  };
  funnel_asymmetry?: number;
}

export interface SensitivityAnalysisResult {
  leave_one_out: {
    excluded_study: string;
    effect: number;
    ci_lower: number;
    ci_upper: number;
    impact: number;
  }[];
  influential_studies: string[];
  cumulative_meta: {
    year: number;
    effect: number;
    ci_lower: number;
    ci_upper: number;
  }[];
}

export interface MLPrediction {
  prediction_type: 'heterogeneity' | 'bias' | 'effect_size';
  predicted_value: number;
  confidence: number;
  feature_importance: { feature: string; importance: number }[];
  model_type: string;
  accuracy?: number;
}

export interface NetworkMetaAnalysis {
  treatments: string[];
  comparisons: { treatment_a: string; treatment_b: string; effect: number; se: number }[];
  network_plot_data: any;
  league_table: number[][];
  sucra_scores: { treatment: string; sucra: number }[];
  inconsistency: {
    global_test_p: number;
    local_inconsistency: any[];
  };
}

export interface BayesianResult {
  posterior_mean: number;
  posterior_sd: number;
  credible_interval_95: [number, number];
  posterior_samples?: number[];
  trace_plot_data?: any;
  convergence_diagnostics: {
    rhat: number;
    ess: number;
  };
}

export interface VisualizationConfig {
  type: 'forest' | 'funnel' | 'radial' | 'network' | 'cumulative' | 'baujat' | 'gosh';
  title?: string;
  show_ci?: boolean;
  show_weights?: boolean;
  show_prediction_interval?: boolean;
  color_scheme?: string;
  interactive?: boolean;
}

export interface DashboardMetrics {
  total_studies: number;
  total_participants: number;
  pooled_effect: number;
  heterogeneity_i2: number;
  publication_bias_detected: boolean;
  last_updated: string;
}

export interface CollaborationSession {
  session_id: string;
  users: {
    user_id: string;
    name: string;
    color: string;
    cursor_position?: { x: number; y: number };
  }[];
  current_analysis: MetaAnalysisResult | null;
  chat_messages: {
    user: string;
    message: string;
    timestamp: string;
  }[];
}

export interface UploadedDataset {
  id: string;
  name: string;
  n_studies: number;
  uploaded_at: string;
  format: 'csv' | 'xlsx' | 'json';
  columns: string[];
  preview: any[];
}

export interface AnalysisJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  result?: MetaAnalysisResult;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface ExportOptions {
  format: 'pdf' | 'word' | 'html' | 'json';
  include_plots: boolean;
  include_tables: boolean;
  include_prisma: boolean;
  template?: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  default_method: string;
  auto_save: boolean;
  show_tooltips: boolean;
  plot_preferences: {
    default_width: number;
    default_height: number;
    color_palette: string;
  };
}

export interface APIError {
  message: string;
  code: string;
  details?: any;
}
