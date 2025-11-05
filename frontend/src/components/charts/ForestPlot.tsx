/**
 * Interactive Forest Plot Component
 * Modern forest plot with hover effects and drill-down capabilities
 */

import React from 'react';
import {
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
  ResponsiveContainer,
  Scatter,
  ErrorBar,
} from 'recharts';
import { Box, Typography, Paper, useTheme } from '@mui/material';
import { Study, MetaAnalysisResult } from '@types/index';

interface ForestPlotProps {
  studies: Study[];
  pooledEffect?: number;
  pooledCI?: [number, number];
  showWeights?: boolean;
  height?: number;
}

const ForestPlot: React.FC<ForestPlotProps> = ({
  studies,
  pooledEffect,
  pooledCI,
  showWeights = true,
  height = 500,
}) => {
  const theme = useTheme();

  // Prepare data for Recharts
  const chartData = studies.map((study, index) => ({
    name: study.label,
    effect: study.effect,
    errorLow: study.ci_lower || study.effect - 1.96 * study.se,
    errorHigh: study.ci_upper || study.effect + 1.96 * study.se,
    weight: study.weight || 1 / (study.se * study.se),
    y: index,
  }));

  // Add pooled estimate if provided
  if (pooledEffect !== undefined && pooledCI) {
    chartData.push({
      name: 'Pooled Effect',
      effect: pooledEffect,
      errorLow: pooledCI[0],
      errorHigh: pooledCI[1],
      weight: 0,
      y: chartData.length,
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
          95% CI: [{data.errorLow.toFixed(3)}, {data.errorHigh.toFixed(3)}]
        </Typography>
        {showWeights && data.weight > 0 && (
          <Typography variant="body2" color="text.secondary">
            Weight: {(data.weight * 100).toFixed(1)}%
          </Typography>
        )}
      </Paper>
    );
  };

  const CustomYAxisTick = ({ x, y, payload }: any) => {
    const study = chartData[payload.value];
    if (!study) return null;

    const isPooled = study.name === 'Pooled Effect';

    return (
      <g transform={`translate(${x},${y})`}>
        <text
          x={-10}
          y={0}
          dy={4}
          textAnchor="end"
          fill={isPooled ? theme.palette.primary.main : theme.palette.text.primary}
          fontWeight={isPooled ? 700 : 400}
          fontSize={isPooled ? 14 : 12}
        >
          {study.name}
        </text>
      </g>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Forest Plot
      </Typography>
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={chartData}
          layout="horizontal"
          margin={{ top: 20, right: 30, left: 150, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis type="number" domain={['auto', 'auto']} />
          <YAxis
            type="number"
            dataKey="y"
            domain={[0, chartData.length - 1]}
            tick={<CustomYAxisTick />}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Null effect line */}
          <ReferenceLine
            x={0}
            stroke={theme.palette.text.secondary}
            strokeDasharray="3 3"
            strokeWidth={2}
          />

          {/* Effect estimates with CI */}
          <Scatter
            dataKey="effect"
            fill={theme.palette.primary.main}
            shape={(props: any) => {
              const { cx, cy, payload } = props;
              const isPooled = payload.name === 'Pooled Effect';
              const size = isPooled ? 14 : 10;

              return (
                <g>
                  {/* Confidence interval line */}
                  <line
                    x1={props.xAxis.scale(payload.errorLow)}
                    x2={props.xAxis.scale(payload.errorHigh)}
                    y1={cy}
                    y2={cy}
                    stroke={theme.palette.primary.main}
                    strokeWidth={2}
                  />
                  {/* Effect point */}
                  {isPooled ? (
                    <polygon
                      points={`${cx},${cy - size} ${cx + size},${cy} ${cx},${cy + size} ${cx - size},${cy}`}
                      fill={theme.palette.primary.dark}
                      stroke={theme.palette.primary.dark}
                      strokeWidth={2}
                    />
                  ) : (
                    <circle
                      cx={cx}
                      cy={cy}
                      r={size}
                      fill={theme.palette.primary.main}
                      stroke="#fff"
                      strokeWidth={2}
                    />
                  )}
                </g>
              );
            }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ForestPlot;
