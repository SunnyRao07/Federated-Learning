/**
 * Main App Component
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance,
  TrendingUp,
  Security,
  BugReport,
  Settings,
} from '@mui/icons-material';

import Dashboard from './components/Dashboard';
import InstitutionSimulator from './components/InstitutionSimulator';
import PerformanceCharts from './components/PerformanceCharts';
import PrivacyVisualizer from './components/PrivacyVisualizer';
import AttackSimulation from './components/AttackSimulation';
import TrainingControl from './components/TrainingControl';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#ff9800',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Training Control', icon: <Settings />, path: '/training' },
  { text: 'Institutions', icon: <AccountBalance />, path: '/institutions' },
  { text: 'Performance', icon: <TrendingUp />, path: '/performance' },
  { text: 'Privacy', icon: <Security />, path: '/privacy' },
  { text: 'Attack Simulation', icon: <BugReport />, path: '/attacks' },
];

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />

          {/* App Bar */}
          <AppBar
            position="fixed"
            sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
          >
            <Toolbar>
              <Security sx={{ mr: 2 }} />
              <Typography variant="h6" noWrap component="div">
                Federated Fraud Detection System
              </Typography>
            </Toolbar>
          </AppBar>

          {/* Sidebar */}
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: drawerWidth,
                boxSizing: 'border-box',
              },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                {menuItems.map((item) => (
                  <ListItem
                    button
                    key={item.text}
                    component={Link}
                    to={item.path}
                    sx={{
                      '&:hover': {
                        backgroundColor: 'rgba(33, 150, 243, 0.08)',
                      },
                    }}
                  >
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>

          {/* Main Content */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              bgcolor: 'background.default',
              p: 3,
              minHeight: '100vh',
            }}
          >
            <Toolbar />
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/training" element={<TrainingControl />} />
              <Route path="/institutions" element={<InstitutionSimulator />} />
              <Route path="/performance" element={<PerformanceCharts />} />
              <Route path="/privacy" element={<PrivacyVisualizer />} />
              <Route path="/attacks" element={<AttackSimulation />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
