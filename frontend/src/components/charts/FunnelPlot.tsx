/**
 * Interactive Funnel Plot Component
 * For publication bias assessment
 */

import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from 'recharts';
import { Box, Typography, Paper, useTheme, Chip } from '@mui/material';
import { Study } from '@types/index';

interface FunnelPlotProps {
  studies: Study[];
  pooledEffect?: number;
  showContours?: boolean;
  height?: number;
}

const FunnelPlot: React.FC<FunnelPlotProps> = ({
  studies,
  pooledEffect,
  showContours = true,
  height = 500,
}) => {
  const theme = useTheme();

  // Prepare data
  const chartData = studies.map((study) => ({
    effect: study.effect,
    se: study.se,
    precision: 1 / study.se,
    name: study.label,
  }));

  const pooled = pooledEffect !== undefined ? pooledEffect : 0;

  // Calculate 95% CI contour
  const maxSE = Math.max(...chartData.map(d => d.se));
  const contourData = [];
  for (let se = 0; se <= maxSE * 1.2; se += maxSE / 50) {
    contourData.push({
      se,
      ciLower: pooled - 1.96 * se,
      ciUpper: pooled + 1.96 * se,
    });
  }

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
          Effect: {data.effect.toFixed(3)}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          SE: {data.se.toFixed(3)}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Precision: {data.precision.toFixed(2)}
        </Typography>
      </Paper>
    );
  };

  // Check for asymmetry
  const leftCount = chartData.filter(d => d.effect < pooled).length;
  const rightCount = chartData.filter(d => d.effect > pooled).length;
  const asymmetry = Math.abs(leftCount - rightCount) / chartData.length > 0.3;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Typography variant="h6">
          Funnel Plot
        </Typography>
        {asymmetry && (
          <Chip
            label="Asymmetry Detected"
            color="warning"
            size="small"
            variant="outlined"
          />
        )}
      </Box>

      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          margin={{ top: 20, right: 30, left: 30, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            type="number"
            dataKey="effect"
            domain={['auto', 'auto']}
            label={{ value: 'Effect Size', position: 'insideBottom', offset: -10 }}
          />
          <YAxis
            type="number"
            dataKey="se"
            domain={[0, 'auto']}
            reversed
            label={{ value: 'Standard Error', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* 95% CI contour */}
          {showContours && (
            <>
              <Area
                data={contourData.map(d => ({ ...d, effect: d.ciLower }))}
                type="monotone"
                dataKey="se"
                stroke="none"
                fill={theme.palette.primary.light}
                fillOpacity={0.2}
              />
              <Area
                data={contourData.map(d => ({ ...d, effect: d.ciUpper }))}
                type="monotone"
                dataKey="se"
                stroke="none"
                fill={theme.palette.primary.light}
                fillOpacity={0.2}
              />
            </>
          )}

          {/* Pooled effect line */}
          <ReferenceLine
            x={pooled}
            stroke={theme.palette.primary.main}
            strokeDasharray="3 3"
            strokeWidth={2}
          />

          {/* Studies */}
          <Scatter
            data={chartData}
            fill={theme.palette.primary.main}
            fillOpacity={0.7}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default FunnelPlot;
