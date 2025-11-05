/**
 * Dashboard Page Component
 * Real-time analytics dashboard with advanced metrics
 */

import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  useTheme,
  Chip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useDashboardMetrics } from '@hooks/useMetaAnalysis';
import { useAnalysisStore } from '@stores/analysisStore';
import ForestPlot from '@components/charts/ForestPlot';
import HeterogeneityChart from '@components/charts/HeterogeneityChart';

const DashboardPage: React.FC = () => {
  const theme = useTheme();
  const { data: metrics, isLoading, error } = useDashboardMetrics();
  const { currentResult, studies } = useAnalysisStore();

  // Mock time-series data for demonstration
  const timeSeriesData = [
    { time: '00:00', studies: 5, effect: 0.45 },
    { time: '04:00', studies: 8, effect: 0.52 },
    { time: '08:00', studies: 12, effect: 0.48 },
    { time: '12:00', studies: 15, effect: 0.51 },
    { time: '16:00', studies: 18, effect: 0.49 },
    { time: '20:00', studies: 20, effect: 0.50 },
  ];

  const pieData = [
    { name: 'Completed', value: 65, color: theme.palette.success.main },
    { name: 'Running', value: 20, color: theme.palette.warning.main },
    { name: 'Failed', value: 10, color: theme.palette.error.main },
    { name: 'Pending', value: 5, color: theme.palette.grey[400] },
  ];

  const MetricCard = ({
    title,
    value,
    icon,
    color,
    trend,
  }: {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    trend?: string;
  }) => (
    <Card
      sx={{
        height: '100%',
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h3" fontWeight={700}>
              {value}
            </Typography>
            {trend && (
              <Chip
                label={trend}
                size="small"
                color="success"
                sx={{ mt: 1 }}
              />
            )}
          </Box>
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: `${color}20`,
              color,
              display: 'flex',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load dashboard metrics. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Analytics Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Real-time meta-analysis metrics and insights
      </Typography>

      {/* Metric Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Studies"
            value={metrics?.total_studies || studies.length || 0}
            icon={<AssessmentIcon sx={{ fontSize: 40 }} />}
            color={theme.palette.primary.main}
            trend="+12% this week"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Participants"
            value={metrics?.total_participants?.toLocaleString() || 'N/A'}
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color={theme.palette.secondary.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Pooled Effect"
            value={metrics?.pooled_effect?.toFixed(3) || currentResult?.pooled_effect.toFixed(3) || 'N/A'}
            icon={<TrendingUpIcon sx={{ fontSize: 40 }} />}
            color={theme.palette.success.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="I² Statistic"
            value={
              metrics?.heterogeneity_i2 !== undefined
                ? `${metrics.heterogeneity_i2.toFixed(1)}%`
                : currentResult?.heterogeneity.I2 !== undefined
                ? `${currentResult.heterogeneity.I2.toFixed(1)}%`
                : 'N/A'
            }
            icon={<WarningIcon sx={{ fontSize: 40 }} />}
            color={
              (metrics?.heterogeneity_i2 || currentResult?.heterogeneity.I2 || 0) > 75
                ? theme.palette.error.main
                : theme.palette.warning.main
            }
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Time Series Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Analysis Trends
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <AreaChart data={timeSeriesData}>
                <defs>
                  <linearGradient id="colorStudies" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.8} />
                    <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="studies"
                  stroke={theme.palette.primary.main}
                  fillOpacity={1}
                  fill="url(#colorStudies)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Analysis Status Pie Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Analysis Status
            </Typography>
            <ResponsiveContainer width="100%" height="80%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Current Analysis Results */}
        {currentResult && (
          <>
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <ForestPlot
                  studies={studies}
                  pooledEffect={currentResult.pooled_effect}
                  pooledCI={[currentResult.ci_lower, currentResult.ci_upper]}
                  height={400}
                />
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <HeterogeneityChart heterogeneity={currentResult.heterogeneity} />
              </Paper>
            </Grid>
          </>
        )}

        {!currentResult && (
          <Grid item xs={12}>
            <Alert severity="info">
              No analysis results yet. Run a meta-analysis to see detailed visualizations.
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default DashboardPage;
