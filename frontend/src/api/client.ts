/**
 * MetaPython API Client
 * Centralized API communication with the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  MetaAnalysisResult,
  PublicationBiasResult,
  SensitivityAnalysisResult,
  MLPrediction,
  NetworkMetaAnalysis,
  BayesianResult,
  UploadedDataset,
  AnalysisJob,
  DashboardMetrics,
  Study,
  APIError,
} from '@types/index';

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 300000, // 5 minutes for long-running analyses
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<APIError>) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error.response?.data || error.message);
      }
    );
  }

  // ============================================================================
  // META-ANALYSIS ENDPOINTS
  // ============================================================================

  async runMetaAnalysis(data: {
    studies: Study[];
    method: 'random' | 'fixed' | 'reml' | 'ml' | 'eb';
    measure?: string;
  }): Promise<MetaAnalysisResult> {
    const response = await this.client.post<MetaAnalysisResult>(
      '/api/meta-analysis/run',
      data
    );
    return response.data;
  }

  async getPublicationBias(data: {
    studies: Study[];
  }): Promise<PublicationBiasResult> {
    const response = await this.client.post<PublicationBiasResult>(
      '/api/meta-analysis/publication-bias',
      data
    );
    return response.data;
  }

  async getSensitivityAnalysis(data: {
    studies: Study[];
    method: string;
  }): Promise<SensitivityAnalysisResult> {
    const response = await this.client.post<SensitivityAnalysisResult>(
      '/api/meta-analysis/sensitivity',
      data
    );
    return response.data;
  }

  async runBayesianAnalysis(data: {
    studies: Study[];
    prior_mean?: number;
    prior_sd?: number;
    method?: 'inla' | 'mcmc';
  }): Promise<BayesianResult> {
    const response = await this.client.post<BayesianResult>(
      '/api/meta-analysis/bayesian',
      data
    );
    return response.data;
  }

  async runNetworkMetaAnalysis(data: {
    studies: Array<{
      treatment_a: string;
      treatment_b: string;
      effect: number;
      se: number;
    }>;
    reference_treatment?: string;
  }): Promise<NetworkMetaAnalysis> {
    const response = await this.client.post<NetworkMetaAnalysis>(
      '/api/meta-analysis/network',
      data
    );
    return response.data;
  }

  // ============================================================================
  // ML PREDICTION ENDPOINTS
  // ============================================================================

  async predictHeterogeneity(data: {
    studies: Study[];
    features?: any;
  }): Promise<MLPrediction> {
    const response = await this.client.post<MLPrediction>(
      '/api/ml/predict-heterogeneity',
      data
    );
    return response.data;
  }

  async detectPublicationBias(data: {
    studies: Study[];
  }): Promise<MLPrediction> {
    const response = await this.client.post<MLPrediction>(
      '/api/ml/detect-bias',
      data
    );
    return response.data;
  }

  async trainCustomModel(data: {
    training_data: any[];
    model_type: string;
    hyperparameters?: any;
  }): Promise<{ model_id: string; metrics: any }> {
    const response = await this.client.post('/api/ml/train', data);
    return response.data;
  }

  // ============================================================================
  // DATA MANAGEMENT
  // ============================================================================

  async uploadDataset(file: File): Promise<UploadedDataset> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<UploadedDataset>(
      '/api/data/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getDatasets(): Promise<UploadedDataset[]> {
    const response = await this.client.get<UploadedDataset[]>('/api/data/datasets');
    return response.data;
  }

  async getDataset(id: string): Promise<UploadedDataset> {
    const response = await this.client.get<UploadedDataset>(`/api/data/datasets/${id}`);
    return response.data;
  }

  async deleteDataset(id: string): Promise<void> {
    await this.client.delete(`/api/data/datasets/${id}`);
  }

  // ============================================================================
  // VISUALIZATION
  // ============================================================================

  async generatePlot(data: {
    plot_type: string;
    studies: Study[];
    config?: any;
  }): Promise<{ plot_data: any; plot_html?: string }> {
    const response = await this.client.post('/api/visualization/generate', data);
    return response.data;
  }

  async exportPlot(data: {
    plot_data: any;
    format: 'png' | 'svg' | 'pdf';
  }): Promise<Blob> {
    const response = await this.client.post('/api/visualization/export', data, {
      responseType: 'blob',
    });
    return response.data;
  }

  // ============================================================================
  // REPORTING
  // ============================================================================

  async generateReport(data: {
    analysis_results: MetaAnalysisResult;
    format: 'pdf' | 'word' | 'html';
    include_prisma?: boolean;
    template?: string;
  }): Promise<Blob> {
    const response = await this.client.post('/api/reporting/generate', data, {
      responseType: 'blob',
    });
    return response.data;
  }

  async generatePrismaFlowchart(data: {
    identification: number;
    screening: number;
    eligibility: number;
    included: number;
    reasons?: any;
  }): Promise<{ svg: string }> {
    const response = await this.client.post('/api/reporting/prisma', data);
    return response.data;
  }

  // ============================================================================
  // R INTEGRATION
  // ============================================================================

  async executeRCode(data: {
    code: string;
    data?: any;
  }): Promise<{ result: any; plots?: string[]; warnings?: string[] }> {
    const response = await this.client.post('/api/r/execute', data);
    return response.data;
  }

  async callMetaforFunction(data: {
    function_name: string;
    parameters: any;
  }): Promise<any> {
    const response = await this.client.post('/api/r/metafor', data);
    return response.data;
  }

  // ============================================================================
  // JOBS & ASYNC OPERATIONS
  // ============================================================================

  async getJobStatus(jobId: string): Promise<AnalysisJob> {
    const response = await this.client.get<AnalysisJob>(`/api/jobs/${jobId}`);
    return response.data;
  }

  async cancelJob(jobId: string): Promise<void> {
    await this.client.post(`/api/jobs/${jobId}/cancel`);
  }

  // ============================================================================
  // DASHBOARD & METRICS
  // ============================================================================

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await this.client.get<DashboardMetrics>('/api/dashboard/metrics');
    return response.data;
  }

  async getAnalysisHistory(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{ analyses: any[]; total: number }> {
    const response = await this.client.get('/api/dashboard/history', { params });
    return response.data;
  }

  // ============================================================================
  // GRAFANA INTEGRATION
  // ============================================================================

  async getGrafanaDashboardConfig(): Promise<any> {
    const response = await this.client.get('/api/grafana/dashboard-config');
    return response.data;
  }

  async exportPrometheusMetrics(): Promise<string> {
    const response = await this.client.get('/metrics', {
      responseType: 'text',
    });
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
