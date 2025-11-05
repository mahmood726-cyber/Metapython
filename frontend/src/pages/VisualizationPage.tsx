/**
 * Visualization Page
 * Publication-quality plots using R's metafor and meta packages
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Stack,
  useTheme,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  ScatterPlot as ScatterPlotIcon,
  BubbleChart as BubbleChartIcon,
  ShowChart as ShowChartIcon,
} from '@mui/icons-material';
import { useAnalysisStore } from '@stores/analysisStore';
import { apiClient } from '@api/client';
import RPlotDisplay from '@components/charts/RPlotDisplay';

type PlotType =
  | 'forest-metafor'
  | 'forest-meta'
  | 'funnel'
  | 'baujat'
  | 'radial'
  | 'gosh'
  | 'cumulative'
  | 'leave-one-out';

const VisualizationPage: React.FC = () => {
  const theme = useTheme();
  const { studies, selectedMethod } = useAnalysisStore();

  const [selectedPlotType, setSelectedPlotType] = useState<PlotType>('forest-metafor');
  const [plotImage, setPlotImage] = useState<string | null>(null);
  const [plotTestResults, setPlotTestResults] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Plot options
  const [forestLayout, setForestLayout] = useState<'JAMA' | 'RevMan' | 'meta'>('JAMA');
  const [showWeights, setShowWeights] = useState(true);
  const [showPredictionInterval, setShowPredictionInterval] = useState(true);
  const [showContours, setShowContours] = useState(true);
  const [trimFill, setTrimFill] = useState(true);
  const [eggerTest, setEggerTest] = useState(true);

  const plotTypes = [
    {
      id: 'forest-metafor' as PlotType,
      name: 'Forest Plot (metafor)',
      icon: <TimelineIcon />,
      description: 'Standard forest plot using metafor',
    },
    {
      id: 'forest-meta' as PlotType,
      name: 'Forest Plot (meta)',
      icon: <TimelineIcon />,
      description: 'Journal-style forest plot (JAMA/RevMan)',
    },
    {
      id: 'funnel' as PlotType,
      name: 'Funnel Plot',
      icon: <ScatterPlotIcon />,
      description: 'Publication bias assessment',
    },
    {
      id: 'baujat' as PlotType,
      name: 'Baujat Plot',
      icon: <BubbleChartIcon />,
      description: 'Outlier and influential studies',
    },
    {
      id: 'radial' as PlotType,
      name: 'Radial Plot',
      icon: <ScatterPlotIcon />,
      description: 'Galbraith plot for heterogeneity',
    },
    {
      id: 'gosh' as PlotType,
      name: 'GOSH Plot',
      icon: <BubbleChartIcon />,
      description: 'Graphical display of heterogeneity',
    },
    {
      id: 'cumulative' as PlotType,
      name: 'Cumulative Forest',
      icon: <ShowChartIcon />,
      description: 'Sequential addition of studies',
    },
    {
      id: 'leave-one-out' as PlotType,
      name: 'Leave-One-Out',
      icon: <TimelineIcon />,
      description: 'Influence diagnostics',
    },
  ];

  const generatePlot = async () => {
    if (studies.length < 2) {
      setError('Need at least 2 studies to generate plots');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setPlotTestResults(null);

    try {
      const effects = studies.map((s) => s.effect);
      const se = studies.map((s) => s.se);
      const labels = studies.map((s) => s.label);

      let result: any;

      switch (selectedPlotType) {
        case 'forest-metafor':
          result = await apiClient.generateForestPlotMetafor({
            effects,
            se,
            study_labels: labels,
            method: selectedMethod,
            show_weights: showWeights,
            show_prediction_interval: showPredictionInterval,
            title: 'Forest Plot (metafor)',
            width: 1200,
            height: 800,
          });
          setPlotImage(result.image);
          break;

        case 'forest-meta':
          result = await apiClient.generateForestPlotMeta({
            effects,
            se,
            study_labels: labels,
            method: selectedMethod,
            show_prediction_interval: showPredictionInterval,
            layout: forestLayout,
            width: 1200,
            height: 800,
          });
          setPlotImage(result.image);
          break;

        case 'funnel':
          result = await apiClient.generateFunnelPlotMetafor({
            effects,
            se,
            study_labels: labels,
            method: selectedMethod,
            show_contours: showContours,
            trim_fill: trimFill,
            egger_test: eggerTest,
            title: 'Funnel Plot',
            width: 900,
            height: 900,
          });
          setPlotImage(result.image);
          setPlotTestResults(result);
          break;

        case 'baujat':
          result = await apiClient.generateBaujatPlot({
            effects,
            se,
            study_labels: labels,
            method: selectedMethod,
            label_outliers: true,
            width: 900,
            height: 800,
          });
          setPlotImage(result.image);
          break;

        case 'radial':
          result = await apiClient.generateRadialPlot({
            effects,
            se,
            study_labels: labels,
            method: selectedMethod,
            width: 900,
            height: 900,
          });
          setPlotImage(result.image);
          break;

        case 'gosh':
          result = await apiClient.generateGOSHPlot({
            effects,
            se,
            method: selectedMethod,
            n_subsets: 1000,
            width: 900,
            height: 800,
          });
          setPlotImage(result.image);
          break;

        case 'cumulative':
          result = await apiClient.generateCumulativePlot({
            effects,
            se,
            study_labels: labels,
            method: selectedMethod,
            width: 1200,
            height: 900,
          });
          setPlotImage(result.image);
          break;

        case 'leave-one-out':
          result = await apiClient.generateLeaveOneOutPlot({
            effects,
            se,
            study_labels: labels,
            method: selectedMethod,
            width: 1200,
            height: 900,
          });
          setPlotImage(result.image);
          break;
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate plot');
    } finally {
      setIsGenerating(false);
    }
  };

  const currentPlot = plotTypes.find((p) => p.id === selectedPlotType);

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Publication-Quality Visualizations
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Generate publication-ready plots using R's metafor and meta packages
      </Typography>

      <Grid container spacing={3}>
        {/* Plot Type Selection */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Plot Type
            </Typography>

            <Stack spacing={1}>
              {plotTypes.map((plot) => (
                <Button
                  key={plot.id}
                  variant={selectedPlotType === plot.id ? 'contained' : 'outlined'}
                  onClick={() => setSelectedPlotType(plot.id)}
                  startIcon={plot.icon}
                  fullWidth
                  sx={{
                    justifyContent: 'flex-start',
                    textAlign: 'left',
                    py: 1.5,
                  }}
                >
                  <Box>
                    <Typography variant="body2" fontWeight={600}>
                      {plot.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {plot.description}
                    </Typography>
                  </Box>
                </Button>
              ))}
            </Stack>

            {/* Plot Options */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Options
              </Typography>

              {(selectedPlotType === 'forest-metafor' || selectedPlotType === 'forest-meta') && (
                <>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={showWeights}
                        onChange={(e) => setShowWeights(e.target.checked)}
                      />
                    }
                    label="Show weights"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={showPredictionInterval}
                        onChange={(e) => setShowPredictionInterval(e.target.checked)}
                      />
                    }
                    label="Prediction interval"
                  />
                </>
              )}

              {selectedPlotType === 'forest-meta' && (
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>Layout</InputLabel>
                  <Select
                    value={forestLayout}
                    label="Layout"
                    onChange={(e: any) => setForestLayout(e.target.value)}
                  >
                    <MenuItem value="JAMA">JAMA</MenuItem>
                    <MenuItem value="RevMan">RevMan</MenuItem>
                    <MenuItem value="meta">Meta</MenuItem>
                  </Select>
                </FormControl>
              )}

              {selectedPlotType === 'funnel' && (
                <>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={showContours}
                        onChange={(e) => setShowContours(e.target.checked)}
                      />
                    }
                    label="Show contours"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={trimFill}
                        onChange={(e) => setTrimFill(e.target.checked)}
                      />
                    }
                    label="Trim & Fill"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={eggerTest}
                        onChange={(e) => setEggerTest(e.target.checked)}
                      />
                    }
                    label="Egger's test"
                  />
                </>
              )}
            </Box>

            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={generatePlot}
              disabled={isGenerating || studies.length < 2}
              sx={{ mt: 3 }}
            >
              {isGenerating ? 'Generating...' : 'Generate Plot'}
            </Button>

            {studies.length < 2 && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Add at least 2 studies to generate plots
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Plot Display */}
        <Grid item xs={12} md={9}>
          {plotImage ? (
            <RPlotDisplay
              plotType={currentPlot?.name || 'R Plot'}
              imageBase64={plotImage}
              title={currentPlot?.name}
              subtitle={currentPlot?.description}
              isLoading={isGenerating}
              error={error || undefined}
              onRefresh={generatePlot}
              testResults={plotTestResults}
            />
          ) : (
            <Paper sx={{ p: 6, textAlign: 'center', minHeight: 600 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No plot generated yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Select a plot type and click "Generate Plot" to create publication-quality
                visualizations using R's metafor and meta packages
              </Typography>

              <Stack direction="row" spacing={1} justifyContent="center">
                <Chip label="Publication-ready" color="primary" variant="outlined" />
                <Chip label="metafor/meta" color="secondary" variant="outlined" />
                <Chip label="High resolution" color="success" variant="outlined" />
              </Stack>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default VisualizationPage;
