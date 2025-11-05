import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  TextField,
  MenuItem,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import { PlayArrow as PlayArrowIcon, Add as AddIcon } from '@mui/icons-material';
import { useAnalysisStore } from '@stores/analysisStore';
import { useRunMetaAnalysis } from '@hooks/useMetaAnalysis';
import ForestPlot from '@components/charts/ForestPlot';
import FunnelPlot from '@components/charts/FunnelPlot';
import HeterogeneityChart from '@components/charts/HeterogeneityChart';

const MetaAnalysisPage: React.FC = () => {
  const { studies, selectedMethod, setSelectedMethod, currentResult, isLoading, error } = useAnalysisStore();
  const runAnalysis = useRunMetaAnalysis();

  const handleRunAnalysis = () => {
    if (studies.length >= 2) {
      runAnalysis.mutate();
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Meta-Analysis
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Settings
            </Typography>

            <TextField
              select
              fullWidth
              label="Method"
              value={selectedMethod}
              onChange={(e: any) => setSelectedMethod(e.target.value)}
              sx={{ mb: 2 }}
            >
              <MenuItem value="random">Random Effects</MenuItem>
              <MenuItem value="fixed">Fixed Effects</MenuItem>
              <MenuItem value="reml">REML</MenuItem>
              <MenuItem value="ml">Maximum Likelihood</MenuItem>
              <MenuItem value="eb">Empirical Bayes</MenuItem>
            </TextField>

            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={isLoading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              onClick={handleRunAnalysis}
              disabled={isLoading || studies.length < 2}
            >
              {isLoading ? 'Running...' : 'Run Analysis'}
            </Button>

            {studies.length < 2 && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Add at least 2 studies to run analysis
              </Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={9}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {currentResult ? (
            <>
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Results Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Pooled Effect
                    </Typography>
                    <Typography variant="h5" fontWeight={600}>
                      {currentResult.pooled_effect.toFixed(3)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      95% CI
                    </Typography>
                    <Typography variant="body1">
                      [{currentResult.ci_lower.toFixed(3)}, {currentResult.ci_upper.toFixed(3)}]
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      P-value
                    </Typography>
                    <Typography variant="body1">{currentResult.p_value.toFixed(4)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      I² Statistic
                    </Typography>
                    <Typography variant="body1">
                      {currentResult.heterogeneity.I2.toFixed(1)}%
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>

              <Paper sx={{ p: 3, mb: 3 }}>
                <ForestPlot
                  studies={studies}
                  pooledEffect={currentResult.pooled_effect}
                  pooledCI={[currentResult.ci_lower, currentResult.ci_upper]}
                />
              </Paper>

              <Paper sx={{ p: 3, mb: 3 }}>
                <FunnelPlot studies={studies} pooledEffect={currentResult.pooled_effect} />
              </Paper>

              <Paper sx={{ p: 3 }}>
                <HeterogeneityChart heterogeneity={currentResult.heterogeneity} />
              </Paper>
            </>
          ) : (
            <Paper sx={{ p: 6, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Run a meta-analysis to see results
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default MetaAnalysisPage;
