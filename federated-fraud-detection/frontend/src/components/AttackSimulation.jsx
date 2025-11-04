/**
 * Attack Simulation - Test privacy defenses
 */
import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  LinearProgress,
} from '@mui/material';
import { Security, Warning, CheckCircle } from '@mui/icons-material';
import { runAttackTest } from '../api/api';

const AttackSimulation = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleRunAttacks = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await runAttackTest();
      setResults(res.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run attack simulation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Privacy Attack Simulation
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Test the robustness of privacy mechanisms against common attacks
        </Typography>
      </Box>

      {/* Attack Description */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: '#fff3e0' }}>
        <Typography variant="h6" gutterBottom>
          About Privacy Attacks
        </Typography>
        <Typography variant="body2" paragraph>
          This simulation tests two common privacy attacks:
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box display="flex" gap={2}>
              <Warning color="warning" />
              <Box>
                <Typography variant="body2" fontWeight="bold">
                  Membership Inference Attack
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Attempts to determine if a specific data point was used in training
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box display="flex" gap={2}>
              <Warning color="warning" />
              <Box>
                <Typography variant="body2" fontWeight="bold">
                  Model Inversion Attack
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Attempts to reconstruct training data from model outputs
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Run Attack Button */}
      <Box display="flex" justifyContent="center" mb={4}>
        <Button
          variant="contained"
          size="large"
          onClick={handleRunAttacks}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <Security />}
        >
          {loading ? 'Running Attack Simulation...' : 'Run Privacy Attack Test'}
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {results && (
        <>
          {/* Overall Defense Rate */}
          <Paper sx={{ p: 3, mb: 3, bgcolor: '#e8f5e9' }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={2}>
                <CheckCircle sx={{ fontSize: 48, color: '#4caf50' }} />
                <Box>
                  <Typography variant="h6" fontWeight="bold">
                    Overall Defense Success Rate
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Privacy mechanisms successfully defended against attacks
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h2" fontWeight="bold" color="success.main">
                {(results.overall_defense_rate * 100).toFixed(1)}%
              </Typography>
            </Box>
          </Paper>

          {/* Attack Details */}
          <Grid container spacing={3}>
            {/* Membership Inference */}
            <Grid item xs={12} md={6}>
              <AttackResultCard
                title="Membership Inference Attack"
                results={results.membership_inference}
                type="membership"
              />
            </Grid>

            {/* Model Inversion */}
            <Grid item xs={12} md={6}>
              <AttackResultCard
                title="Model Inversion Attack"
                results={results.model_inversion}
                type="inversion"
              />
            </Grid>
          </Grid>

          {/* Interpretation */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Results Interpretation
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Defense Success Rate:</strong> Higher is better. Indicates how well the privacy
              mechanisms protect against attacks.
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Attack Success Rate:</strong> Lower is better. Shows how effective the attack was in
              compromising privacy.
            </Typography>
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="body2">
                The federated learning system with Differential Privacy and Secure Aggregation successfully
                defended against {(results.overall_defense_rate * 100).toFixed(1)}% of privacy attacks,
                demonstrating strong privacy preservation.
              </Typography>
            </Alert>
          </Paper>
        </>
      )}
    </Container>
  );
};

// Attack Result Card
const AttackResultCard = ({ title, results, type }) => {
  const defenseRate =
    type === 'membership' ? results.defense_success_rate : results.defense_score;
  const attackRate = 1 - defenseRate;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>

        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Defense Success Rate</Typography>
            <Typography variant="body2" fontWeight="bold" color="success.main">
              {(defenseRate * 100).toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={defenseRate * 100}
            color="success"
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Attack Success Rate</Typography>
            <Typography variant="body2" fontWeight="bold" color="error">
              {(attackRate * 100).toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={attackRate * 100}
            color="error"
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Additional Metrics */}
        <Box sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
            Additional Metrics
          </Typography>
          {type === 'membership' ? (
            <>
              <Box display="flex" justifyContent="space-between" mb={0.5}>
                <Typography variant="caption">Train Confidence</Typography>
                <Typography variant="caption" fontWeight="bold">
                  {results.train_confidence?.toFixed(4)}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="caption">Test Confidence</Typography>
                <Typography variant="caption" fontWeight="bold">
                  {results.test_confidence?.toFixed(4)}
                </Typography>
              </Box>
            </>
          ) : (
            <>
              <Box display="flex" justifyContent="space-between" mb={0.5}>
                <Typography variant="caption">Reconstruction Error</Typography>
                <Typography variant="caption" fontWeight="bold">
                  {results.reconstruction_error?.toFixed(4)}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="caption">Prediction Difference</Typography>
                <Typography variant="caption" fontWeight="bold">
                  {results.prediction_difference?.toFixed(4)}
                </Typography>
              </Box>
            </>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default AttackSimulation;
