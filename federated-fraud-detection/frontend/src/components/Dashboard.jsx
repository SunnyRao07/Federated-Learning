/**
 * Main Dashboard Component
 */
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
                title="F1 Score"
                value={metrics.federated_model.f1_score?.toFixed(4) || 'N/A'}
                improvement={metrics.improvement.f1_score}
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
            {/* Federated vs Local Comparison */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Model Performance Comparison
                </Typography>
                <ComparisonTable
                  federated={metrics.federated_model}
                  local={metrics.local_baseline}
                  improvement={metrics.improvement}
                />
              </Paper>
            </Grid>

            {/* Privacy Metrics */}
            <Grid item xs={12} md={6}>
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
          {improvement !== undefined && (
            <Chip
              label={`${improvement > 0 ? '+' : ''}${improvement.toFixed(1)}%`}
              size="small"
              color={improvement > 0 ? 'success' : 'default'}
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

// Comparison Table Component
const ComparisonTable = ({ federated, local, improvement }) => (
  <Box>
    {[
      { label: 'Accuracy', key: 'accuracy' },
      { label: 'AUC', key: 'auc' },
      { label: 'Precision', key: 'precision' },
      { label: 'Recall', key: 'recall' },
      { label: 'F1 Score', key: 'f1_score' },
    ].map((metric) => (
      <Box
        key={metric.key}
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        py={1.5}
        borderBottom="1px solid #eee"
      >
        <Typography variant="body2" fontWeight="medium">
          {metric.label}
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <Typography variant="body2" color="text.secondary">
            Local: {local[metric.key]?.toFixed(4) || 'N/A'}
          </Typography>
          <Typography variant="body2" fontWeight="bold" color="primary">
            Federated: {federated[metric.key]?.toFixed(4) || 'N/A'}
          </Typography>
          <Chip
            label={`${improvement[metric.key] > 0 ? '+' : ''}${improvement[metric.key]?.toFixed(1) || 0}%`}
            size="small"
            color={improvement[metric.key] > 0 ? 'success' : 'default'}
          />
        </Box>
      </Box>
    ))}
  </Box>
);

// Privacy Metrics Component
const PrivacyMetrics = ({ privacy, attacks }) => (
  <Box>
    <Box mb={3}>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Differential Privacy Parameters
      </Typography>
      <Box display="flex" gap={2} mt={1}>
        <Chip label={`ε = ${privacy.epsilon?.toFixed(2) || 'N/A'}`} color="primary" />
        <Chip label={`δ = ${privacy.delta?.toExponential(2) || 'N/A'}`} />
        <Chip label={`Noise: ${privacy.noise_multiplier?.toFixed(2) || 'N/A'}`} />
      </Box>
    </Box>

    {attacks && (
      <Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Privacy Attack Defense
        </Typography>
        <Box mt={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Overall Defense Rate</Typography>
            <Typography variant="body2" fontWeight="bold" color="success.main">
              {(attacks.overall_defense_rate * 100).toFixed(1)}%
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Membership Inference Defense</Typography>
            <Typography variant="body2" fontWeight="bold">
              {(attacks.membership_inference?.defense_success_rate * 100).toFixed(1)}%
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2">Model Inversion Defense</Typography>
            <Typography variant="body2" fontWeight="bold">
              {(attacks.model_inversion?.defense_score * 100).toFixed(1)}%
            </Typography>
          </Box>
        </Box>
      </Box>
    )}
  </Box>
);

export default Dashboard;
