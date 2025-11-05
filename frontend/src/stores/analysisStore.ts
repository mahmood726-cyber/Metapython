/**
 * Analysis State Store (Zustand)
 * Manages meta-analysis state across the application
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  Study,
  MetaAnalysisResult,
  PublicationBiasResult,
  SensitivityAnalysisResult,
  MLPrediction,
} from '@types/index';

interface AnalysisState {
  // Current data
  studies: Study[];
  currentResult: MetaAnalysisResult | null;
  publicationBias: PublicationBiasResult | null;
  sensitivity: SensitivityAnalysisResult | null;
  mlPredictions: MLPrediction[];

  // UI state
  isLoading: boolean;
  error: string | null;
  selectedMethod: 'random' | 'fixed' | 'reml' | 'ml' | 'eb';

  // Actions
  setStudies: (studies: Study[]) => void;
  addStudy: (study: Study) => void;
  updateStudy: (id: string, updates: Partial<Study>) => void;
  removeStudy: (id: string) => void;
  clearStudies: () => void;

  setCurrentResult: (result: MetaAnalysisResult | null) => void;
  setPublicationBias: (bias: PublicationBiasResult | null) => void;
  setSensitivity: (sensitivity: SensitivityAnalysisResult | null) => void;
  addMLPrediction: (prediction: MLPrediction) => void;

  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedMethod: (method: 'random' | 'fixed' | 'reml' | 'ml' | 'eb') => void;

  reset: () => void;
}

const initialState = {
  studies: [],
  currentResult: null,
  publicationBias: null,
  sensitivity: null,
  mlPredictions: [],
  isLoading: false,
  error: null,
  selectedMethod: 'random' as const,
};

export const useAnalysisStore = create<AnalysisState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        setStudies: (studies) => set({ studies }),

        addStudy: (study) =>
          set((state) => ({
            studies: [...state.studies, study],
          })),

        updateStudy: (id, updates) =>
          set((state) => ({
            studies: state.studies.map((s) =>
              s.id === id ? { ...s, ...updates } : s
            ),
          })),

        removeStudy: (id) =>
          set((state) => ({
            studies: state.studies.filter((s) => s.id !== id),
          })),

        clearStudies: () => set({ studies: [] }),

        setCurrentResult: (result) => set({ currentResult: result }),
        setPublicationBias: (bias) => set({ publicationBias: bias }),
        setSensitivity: (sensitivity) => set({ sensitivity }),
        addMLPrediction: (prediction) =>
          set((state) => ({
            mlPredictions: [...state.mlPredictions, prediction],
          })),

        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setSelectedMethod: (method) => set({ selectedMethod: method }),

        reset: () => set(initialState),
      }),
      {
        name: 'metapython-analysis-storage',
        partialize: (state) => ({
          studies: state.studies,
          selectedMethod: state.selectedMethod,
        }),
      }
    ),
    { name: 'AnalysisStore' }
  )
);
