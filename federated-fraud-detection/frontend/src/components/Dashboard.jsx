import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Security,
  Speed,
  CheckCircle,
} from '@mui/icons-material';
import { getMetrics, getStatus } from '../api/api';

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, statusRes] = await Promise.all([
        getMetrics().catch(() => null),
        getStatus(),
      ]);

      if (metricsRes) {
        setMetrics(metricsRes.data);
      }
      setStatus(statusRes.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Federated Fraud Detection Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Privacy-preserving collaborative fraud detection across financial institutions
        </Typography>
      </Box>

      {/* Status Alert */}
      {status && (
        <Alert
          severity={
            status.status === 'completed'
              ? 'success'
              : status.status === 'training'
              ? 'info'
              : status.status === 'error'
              ? 'error'
              : 'warning'
          }
          sx={{ mb: 3 }}
        >
          {status.message} {status.status === 'training' && `(${status.progress_percentage.toFixed(0)}%)`}
        </Alert>
      )}

      {error && !metrics && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          No training data available. Please train the model first.
        </Alert>
      )}

      {metrics && (
        <>
          {/* Key Metrics Cards */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Federated AUC"
                value={metrics.federated_model.auc?.toFixed(4) || 'N/A'}
                improvement={metrics.improvement.auc}
                icon={<TrendingUp />}
                color="#4caf50"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Recall"
                value={metrics.federated_model.recall?.toFixed(4) || 'N/A'}
                improvement={metrics.improvement.recall}
                icon={<CheckCircle />}
                color="#2196f3"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Privacy Budget (ε)"
                value={metrics.privacy_metrics.epsilon?.toFixed(2) || 'N/A'}
                subtitle="Lower is better"
                icon={<Security />}
                color="#ff9800"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Communication Cost"
                value={`${metrics.communication_cost_mb?.toFixed(2) || 0} MB`}
                subtitle="Per round"
                icon={<Speed />}
                color="#9c27b0"
              />
            </Grid>
          </Grid>

          {/* Detailed Metrics */}
          <Grid container spacing={3}>
            {/* Privacy Metrics */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Privacy Protection
                </Typography>
                <PrivacyMetrics
                  privacy={metrics.privacy_metrics}
                  attacks={metrics.privacy_attacks}
                />
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
    </Container>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, improvement, subtitle, icon, color }) => (
  <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)` }}>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight="bold" color={color}>
            {value}
          </Typography>
          {improvement !== undefined && improvement > 0 && (
            <Chip
              label={`${improvement > 0 ? '+' : ''}${improvement.toFixed(1)}%`}
              size="small"
              color="success"
              sx={{ mt: 1 }}
            />
          )}
          {subtitle && (
            <Typography variant="caption" color="text.secondary" display="block" mt={1}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box sx={{ color, opacity: 0.3, fontSize: 40 }}>{icon}</Box>
      </Box>
    </CardContent>
  </Card>
);



// Privacy Metrics Component
const PrivacyMetrics = ({ privacy, attacks }) => (
  <Grid container spacing={4} alignItems="center">
    <Grid item xs={12} md={6}>
      <Typography variant="subtitle1" gutterBottom fontWeight="medium" color="text.secondary">
        Differential Privacy Parameters
      </Typography>
      <Box display="flex" gap={2} mt={2} flexWrap="wrap">
        <Chip 
          label={`ε = ${privacy.epsilon?.toFixed(2) || 'N/A'}`} 
          color="primary" 
          variant="filled"
          sx={{ fontWeight: 'bold', fontSize: '1.1rem', px: 1 }}
        />
        <Chip label={`δ = ${privacy.delta?.toExponential(2) || 'N/A'}`} variant="outlined" />
        <Chip label={`Noise: ${privacy.noise_multiplier?.toFixed(2) || 'N/A'}`} variant="outlined" />
        <Chip label={`Clip: ${privacy.l2_norm_clip?.toFixed(1) || 'N/A'}`} variant="outlined" />
      </Box>
    </Grid>

    {attacks && (
      <Grid item xs={12} md={6}>
        <Typography variant="subtitle1" gutterBottom fontWeight="medium" color="text.secondary">
          Privacy Attack Defense
        </Typography>
        <Box mt={1}>
          <Box display="flex" justifyContent="space-between" mb={1} p={1.5} bgcolor="#f8f9fa" borderRadius={2}>
            <Typography variant="body1">Overall Defense Rate</Typography>
            <Typography variant="body1" fontWeight="bold" color="success.main">
              {(attacks.overall_defense_rate * 100).toFixed(1)}%
            </Typography>
          </Box>
          <Box px={1.5}>
            <Box display="flex" justifyContent="space-between" mb={1} py={0.5} borderBottom="1px dashed #eee">
              <Typography variant="body2" color="text.secondary">Membership Inference</Typography>
              <Typography variant="body2" fontWeight="medium">
                {(attacks.membership_inference?.defense_success_rate * 100).toFixed(1)}%
              </Typography>
            </Box>
            <Box display="flex" justifyContent="space-between" py={0.5}>
              <Typography variant="body2" color="text.secondary">Model Inversion</Typography>
              <Typography variant="body2" fontWeight="medium">
                {(attacks.model_inversion?.defense_score * 100).toFixed(1)}%
              </Typography>
            </Box>
          </Box>
        </Box>
      </Grid>
    )}
  </Grid>
);

export default Dashboard;