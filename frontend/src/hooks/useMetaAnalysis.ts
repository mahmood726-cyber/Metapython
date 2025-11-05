/**
 * Custom React Hooks for Meta-Analysis Operations
 * Uses React Query for data fetching and caching
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { apiClient } from '@api/client';
import { useAnalysisStore } from '@stores/analysisStore';
import {
  MetaAnalysisResult,
  PublicationBiasResult,
  SensitivityAnalysisResult,
  BayesianResult,
  NetworkMetaAnalysis,
  MLPrediction,
} from '@types/index';

export const useRunMetaAnalysis = () => {
  const queryClient = useQueryClient();
  const { setCurrentResult, setLoading, setError, studies, selectedMethod } =
    useAnalysisStore();

  return useMutation({
    mutationFn: () =>
      apiClient.runMetaAnalysis({
        studies,
        method: selectedMethod,
      }),
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (data: MetaAnalysisResult) => {
      setCurrentResult(data);
      setLoading(false);
      toast.success('Meta-analysis completed successfully!');
      queryClient.invalidateQueries({ queryKey: ['dashboard-metrics'] });
    },
    onError: (error: any) => {
      setError(error.message || 'Analysis failed');
      setLoading(false);
      toast.error(`Error: ${error.message || 'Analysis failed'}`);
    },
  });
};

export const usePublicationBias = () => {
  const { setPublicationBias, studies } = useAnalysisStore();

  return useMutation({
    mutationFn: () => apiClient.getPublicationBias({ studies }),
    onSuccess: (data: PublicationBiasResult) => {
      setPublicationBias(data);
      toast.success('Publication bias analysis completed!');
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message || 'Bias analysis failed'}`);
    },
  });
};

export const useSensitivityAnalysis = () => {
  const { setSensitivity, studies, selectedMethod } = useAnalysisStore();

  return useMutation({
    mutationFn: () =>
      apiClient.getSensitivityAnalysis({
        studies,
        method: selectedMethod,
      }),
    onSuccess: (data: SensitivityAnalysisResult) => {
      setSensitivity(data);
      toast.success('Sensitivity analysis completed!');
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message || 'Sensitivity analysis failed'}`);
    },
  });
};

export const useBayesianAnalysis = () => {
  return useMutation({
    mutationFn: (params: {
      prior_mean?: number;
      prior_sd?: number;
      method?: 'inla' | 'mcmc';
    }) => {
      const studies = useAnalysisStore.getState().studies;
      return apiClient.runBayesianAnalysis({ studies, ...params });
    },
    onSuccess: (data: BayesianResult) => {
      toast.success('Bayesian analysis completed!');
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message || 'Bayesian analysis failed'}`);
    },
  });
};

export const useNetworkMetaAnalysis = () => {
  return useMutation({
    mutationFn: (data: {
      studies: Array<{
        treatment_a: string;
        treatment_b: string;
        effect: number;
        se: number;
      }>;
      reference_treatment?: string;
    }) => apiClient.runNetworkMetaAnalysis(data),
    onSuccess: (data: NetworkMetaAnalysis) => {
      toast.success('Network meta-analysis completed!');
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message || 'Network analysis failed'}`);
    },
  });
};

export const useMLPrediction = () => {
  const { addMLPrediction, studies } = useAnalysisStore();

  return useMutation({
    mutationFn: (type: 'heterogeneity' | 'bias') => {
      if (type === 'heterogeneity') {
        return apiClient.predictHeterogeneity({ studies });
      } else {
        return apiClient.detectPublicationBias({ studies });
      }
    },
    onSuccess: (data: MLPrediction) => {
      addMLPrediction(data);
      toast.success('ML prediction completed!');
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message || 'ML prediction failed'}`);
    },
  });
};

export const useDataUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => apiClient.uploadDataset(file),
    onSuccess: () => {
      toast.success('Dataset uploaded successfully!');
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
    },
    onError: (error: any) => {
      toast.error(`Upload failed: ${error.message}`);
    },
  });
};

export const useDatasets = () => {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: () => apiClient.getDatasets(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useDashboardMetrics = () => {
  return useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => apiClient.getDashboardMetrics(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

export const useGenerateReport = () => {
  return useMutation({
    mutationFn: (data: {
      format: 'pdf' | 'word' | 'html';
      include_prisma?: boolean;
    }) => {
      const currentResult = useAnalysisStore.getState().currentResult;
      if (!currentResult) {
        throw new Error('No analysis results available');
      }
      return apiClient.generateReport({
        analysis_results: currentResult,
        ...data,
      });
    },
    onSuccess: (blob, variables) => {
      // Download the generated report
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `meta-analysis-report.${variables.format}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Report generated successfully!');
    },
    onError: (error: any) => {
      toast.error(`Report generation failed: ${error.message}`);
    },
  });
};

export const useRExecution = () => {
  return useMutation({
    mutationFn: (data: { code: string; data?: any }) =>
      apiClient.executeRCode(data),
    onSuccess: () => {
      toast.success('R code executed successfully!');
    },
    onError: (error: any) => {
      toast.error(`R execution failed: ${error.message}`);
    },
  });
};
