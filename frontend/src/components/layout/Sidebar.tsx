/**
 * Sidebar Navigation Component
 * Modern collapsible sidebar with icons and tooltips
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Divider,
  Typography,
  Avatar,
  useTheme,
} from '@mui/material';
import {
  Home as HomeIcon,
  Analytics as AnalyticsIcon,
  BarChart as BarChartIcon,
  Psychology as PsychologyIcon,
  Code as CodeIcon,
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon,
  Insights as InsightsIcon,
  People as PeopleIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';
import { useUIStore } from '@stores/uiStore';

interface SidebarProps {
  width: number;
  collapsedWidth: number;
}

const menuItems = [
  { id: 'home', label: 'Home', icon: HomeIcon, path: '/' },
  { id: 'meta-analysis', label: 'Meta-Analysis', icon: AnalyticsIcon, path: '/meta-analysis' },
  { id: 'visualization', label: 'Visualizations', icon: BarChartIcon, path: '/visualization' },
  { id: 'ml-prediction', label: 'ML Predictions', icon: PsychologyIcon, path: '/ml-prediction' },
  { id: 'r-integration', label: 'R Integration', icon: CodeIcon, path: '/r-integration' },
  { id: 'reporting', label: 'Reporting', icon: AssessmentIcon, path: '/reporting' },
  { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon, path: '/dashboard' },
  { id: 'grafana', label: 'Grafana', icon: InsightsIcon, path: '/grafana' },
  { id: 'collaboration', label: 'Collaboration', icon: PeopleIcon, path: '/collaboration' },
];

const Sidebar: React.FC<SidebarProps> = ({ width, collapsedWidth }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const drawerWidth = sidebarOpen ? width : collapsedWidth;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          overflowX: 'hidden',
          backgroundColor: theme.palette.mode === 'light' ? '#1a1a2e' : '#0f0f1e',
          color: '#ffffff',
          borderRight: 'none',
        },
      }}
    >
      {/* Logo/Title Area */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: sidebarOpen ? 'space-between' : 'center',
          p: 2,
          minHeight: 64,
        }}
      >
        {sidebarOpen && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Avatar
              sx={{
                bgcolor: theme.palette.primary.main,
                width: 40,
                height: 40,
              }}
            >
              <ScienceIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={700} color="inherit">
              MetaPython
            </Typography>
          </Box>
        )}

        <IconButton
          onClick={toggleSidebar}
          sx={{
            color: 'inherit',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.1)',
            },
          }}
        >
          {sidebarOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.12)' }} />

      {/* Navigation Menu */}
      <List sx={{ mt: 2, px: 1 }}>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          const button = (
            <ListItemButton
              key={item.id}
              onClick={() => handleNavigation(item.path)}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                backgroundColor: isActive
                  ? 'rgba(255,255,255,0.15)'
                  : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
                justifyContent: sidebarOpen ? 'initial' : 'center',
                px: sidebarOpen ? 2.5 : 1.5,
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: sidebarOpen ? 40 : 'auto',
                  color: isActive ? theme.palette.primary.light : '#ffffff',
                  justifyContent: 'center',
                }}
              >
                <Icon />
              </ListItemIcon>
              {sidebarOpen && (
                <ListItemText
                  primary={item.label}
                  sx={{
                    '& .MuiTypography-root': {
                      fontWeight: isActive ? 600 : 400,
                    },
                  }}
                />
              )}
            </ListItemButton>
          );

          if (!sidebarOpen) {
            return (
              <Tooltip key={item.id} title={item.label} placement="right">
                {button}
              </Tooltip>
            );
          }

          return button;
        })}
      </List>

      {/* Footer Info */}
      {sidebarOpen && (
        <Box
          sx={{
            mt: 'auto',
            p: 2,
            borderTop: '1px solid rgba(255,255,255,0.12)',
          }}
        >
          <Typography variant="caption" color="rgba(255,255,255,0.7)">
            MetaPython v1.0.0
          </Typography>
          <Typography variant="caption" display="block" color="rgba(255,255,255,0.5)">
            Advanced Meta-Analysis Platform
          </Typography>
        </Box>
      )}
    </Drawer>
  );
};

export default Sidebar;
