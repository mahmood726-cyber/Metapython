/**
 * MetaPython React Frontend
 *
 * Modern web interface for comprehensive meta-analysis with:
 * - Real-time collaboration via WebSocket
 * - Interactive visualizations
 * - ML-powered predictions
 * - R Shiny app integration
 * - Automated PRISMA reporting
 * - Grafana dashboards
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layout
import MainLayout from './components/layout/MainLayout';

// Pages
import HomePage from './pages/HomePage';
import MetaAnalysisPage from './pages/MetaAnalysisPage';
import VisualizationPage from './pages/VisualizationPage';
import RIntegrationPage from './pages/RIntegrationPage';
import MLPredictionPage from './pages/MLPredictionPage';
import ReportingPage from './pages/ReportingPage';
import DashboardPage from './pages/DashboardPage';
import GrafanaPage from './pages/GrafanaPage';
import CollaborationPage from './pages/CollaborationPage';

// Theme configuration
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

// Query client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <MainLayout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/meta-analysis" element={<MetaAnalysisPage />} />
              <Route path="/visualization" element={<VisualizationPage />} />
              <Route path="/r-integration" element={<RIntegrationPage />} />
              <Route path="/ml-prediction" element={<MLPredictionPage />} />
              <Route path="/reporting" element={<ReportingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/grafana" element={<GrafanaPage />} />
              <Route path="/collaboration" element={<CollaborationPage />} />
            </Routes>
          </MainLayout>
        </Router>
        <ToastContainer
          position="bottom-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
