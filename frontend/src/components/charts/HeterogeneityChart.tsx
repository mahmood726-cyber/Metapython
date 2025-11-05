/**
 * Heterogeneity Visualization Component
 * Displays I², τ², and Q statistics with visual indicators
 */

import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  LinearProgress,
  Chip,
  useTheme,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
} from '@mui/icons-material';
import { HeterogeneityMetrics } from '@types/index';

interface HeterogeneityChartProps {
  heterogeneity: HeterogeneityMetrics;
  showDetails?: boolean;
}

const HeterogeneityChart: React.FC<HeterogeneityChartProps> = ({
  heterogeneity,
  showDetails = true,
}) => {
  const theme = useTheme();

  const { I2, tau2, tau, Q, Q_p, H2 } = heterogeneity;

  // Interpret I²
  const getI2Interpretation = (i2: number) => {
    if (i2 < 25) return { level: 'Low', color: 'success', icon: <TrendingDownIcon /> };
    if (i2 < 50) return { level: 'Moderate', color: 'warning', icon: <TrendingFlatIcon /> };
    if (i2 < 75) return { level: 'Substantial', color: 'warning', icon: <TrendingUpIcon /> };
    return { level: 'Considerable', color: 'error', icon: <TrendingUpIcon /> };
  };

  const i2Interp = getI2Interpretation(I2);

  // Data for bar chart
  const chartData = [
    { name: 'I² (%)', value: I2, max: 100 },
    { name: 'τ²', value: tau2 * 100, max: Math.max(tau2 * 120, 1) },
  ];

  // Colors based on I² levels
  const getBarColor = (value: number, name: string) => {
    if (name === 'I² (%)') {
      if (value < 25) return theme.palette.success.main;
      if (value < 50) return theme.palette.warning.light;
      if (value < 75) return theme.palette.warning.main;
      return theme.palette.error.main;
    }
    return theme.palette.primary.main;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || payload.length === 0) return null;

    const data = payload[0].payload;
    return (
      <Paper
        sx={{
          p: 1.5,
          backgroundColor: 'rgba(255,255,255,0.95)',
          border: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Typography variant="body2" fontWeight={600}>
          {data.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Value: {data.name === 'I² (%)' ? data.value.toFixed(1) : (data.value / 100).toFixed(3)}
        </Typography>
      </Paper>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Heterogeneity Assessment
      </Typography>

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                I² Statistic
              </Typography>
              <Chip
                label={i2Interp.level}
                color={i2Interp.color as any}
                size="small"
                icon={i2Interp.icon}
              />
            </Box>
            <Typography variant="h4" fontWeight={700}>
              {I2.toFixed(1)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={I2}
              sx={{
                mt: 1,
                height: 8,
                borderRadius: 4,
                backgroundColor: theme.palette.grey[200],
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getBarColor(I2, 'I² (%)'),
                },
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Between-study variability
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              τ² (Tau-squared)
            </Typography>
            <Typography variant="h4" fontWeight={700}>
              {tau2.toFixed(3)}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
              τ = {tau.toFixed(3)}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Between-study variance
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Cochran's Q
            </Typography>
            <Typography variant="h4" fontWeight={700}>
              {Q.toFixed(2)}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
              p = {Q_p.toFixed(4)}
            </Typography>
            <Chip
              label={Q_p < 0.05 ? 'Significant' : 'Not Significant'}
              color={Q_p < 0.05 ? 'error' : 'success'}
              size="small"
              sx={{ mt: 1 }}
            />
          </Paper>
        </Grid>

        {/* Bar Chart */}
        {showDetails && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getBarColor(entry.value, entry.name)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Interpretation Guide */}
        {showDetails && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2, backgroundColor: theme.palette.grey[50] }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Interpretation Guide:
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2">
                    <strong>I² = 0-25%:</strong> Low heterogeneity
                  </Typography>
                  <Typography variant="body2">
                    <strong>I² = 25-50%:</strong> Moderate heterogeneity
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2">
                    <strong>I² = 50-75%:</strong> Substantial heterogeneity
                  </Typography>
                  <Typography variant="body2">
                    <strong>I² = 75-100%:</strong> Considerable heterogeneity
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default HeterogeneityChart;
