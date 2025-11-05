/**
 * Home Page Component
 * Landing page with overview and quick actions
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Card,
  CardContent,
  CardActions,
  useTheme,
  Chip,
  Stack,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  BarChart as BarChartIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Science as ScienceIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';

const HomePage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  const features = [
    {
      title: 'Meta-Analysis',
      description: 'Run comprehensive meta-analyses with multiple methods (Random, Fixed, REML, Bayesian)',
      icon: <AnalyticsIcon sx={{ fontSize: 40 }} />,
      path: '/meta-analysis',
      color: theme.palette.primary.main,
    },
    {
      title: 'Visualizations',
      description: 'Create interactive forest plots, funnel plots, and advanced visualizations',
      icon: <BarChartIcon sx={{ fontSize: 40 }} />,
      path: '/visualization',
      color: theme.palette.secondary.main,
    },
    {
      title: 'ML Predictions',
      description: 'AI-powered heterogeneity prediction and publication bias detection',
      icon: <PsychologyIcon sx={{ fontSize: 40 }} />,
      path: '/ml-prediction',
      color: theme.palette.success.main,
    },
    {
      title: 'Dashboard',
      description: 'Real-time analytics dashboard with Grafana integration',
      icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
      path: '/dashboard',
      color: theme.palette.warning.main,
    },
  ];

  const stats = [
    { label: 'Statistical Methods', value: '50+', icon: <TrendingUpIcon /> },
    { label: 'Visualization Types', value: '20+', icon: <BarChartIcon /> },
    { label: 'ML Models', value: '10+', icon: <PsychologyIcon /> },
    { label: 'R Integration', value: '100%', icon: <ScienceIcon /> },
  ];

  const highlights = [
    { text: 'World-first transportability analysis', icon: <SpeedIcon /> },
    { text: 'Component-based meta-analysis (CBAMM)', icon: <ScienceIcon /> },
    { text: 'INLA Bayesian inference', icon: <SecurityIcon /> },
    { text: 'Real-time collaboration', icon: <AnalyticsIcon /> },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          borderRadius: 3,
          p: 6,
          mb: 4,
          color: 'white',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Typography variant="h2" fontWeight={700} gutterBottom>
            MetaPython
          </Typography>
          <Typography variant="h5" sx={{ mb: 3, opacity: 0.9 }}>
            Advanced Meta-Analysis Platform with AI/ML Integration
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, maxWidth: 800, opacity: 0.9 }}>
            Comprehensive meta-analysis toolkit with cutting-edge statistical methods,
            machine learning predictions, real-time collaboration, and professional reporting.
          </Typography>

          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              size="large"
              sx={{
                backgroundColor: 'white',
                color: theme.palette.primary.main,
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.9)' },
              }}
              onClick={() => navigate('/meta-analysis')}
            >
              Start Analysis
            </Button>
            <Button
              variant="outlined"
              size="large"
              sx={{
                borderColor: 'white',
                color: 'white',
                '&:hover': { borderColor: 'white', backgroundColor: 'rgba(255,255,255,0.1)' },
              }}
              onClick={() => navigate('/dashboard')}
            >
              View Dashboard
            </Button>
          </Stack>
        </Box>

        {/* Decorative background */}
        <Box
          sx={{
            position: 'absolute',
            top: -100,
            right: -100,
            width: 400,
            height: 400,
            borderRadius: '50%',
            backgroundColor: 'rgba(255,255,255,0.1)',
          }}
        />
      </Box>

      {/* Stats Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              sx={{
                p: 3,
                textAlign: 'center',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' },
              }}
            >
              {React.cloneElement(stat.icon, {
                sx: { fontSize: 40, color: theme.palette.primary.main, mb: 1 },
              })}
              <Typography variant="h3" fontWeight={700}>
                {stat.value}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {stat.label}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Features Section */}
      <Typography variant="h4" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
        Key Features
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[8],
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    mb: 2,
                  }}
                >
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      backgroundColor: `${feature.color}15`,
                      color: feature.color,
                      display: 'flex',
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h5" fontWeight={600}>
                    {feature.title}
                  </Typography>
                </Box>
                <Typography variant="body1" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="large"
                  onClick={() => navigate(feature.path)}
                  sx={{ ml: 1 }}
                >
                  Explore →
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Highlights Section */}
      <Paper
        sx={{
          p: 4,
          background: `linear-gradient(135deg, ${theme.palette.grey[50]} 0%, ${theme.palette.grey[100]} 100%)`,
        }}
      >
        <Typography variant="h4" fontWeight={600} gutterBottom>
          🌟 World-Class Innovations
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          MetaPython includes cutting-edge features not available in any other meta-analysis platform
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {highlights.map((highlight, index) => (
            <Chip
              key={index}
              icon={React.cloneElement(highlight.icon, { sx: { fontSize: 18 } })}
              label={highlight.text}
              sx={{
                px: 1,
                py: 2.5,
                fontSize: '0.95rem',
                fontWeight: 500,
              }}
            />
          ))}
        </Stack>
      </Paper>
    </Box>
  );
};

export default HomePage;
