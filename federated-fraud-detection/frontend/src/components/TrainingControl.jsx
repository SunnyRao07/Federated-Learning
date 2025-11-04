/**
 * Training Control Panel
 */
import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import { PlayArrow, Refresh } from '@mui/icons-material';
import { trainModel, resetTraining } from '../api/api';

const TrainingControl = () => {
  const [config, setConfig] = useState({
    n_clients: 5,
    n_rounds: 10,
    local_epochs: 5,
    batch_size: 32,
    use_dp: true,
    use_secure_agg: true,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleConfigChange = (field, value) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const handleTrain = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await trainModel(config);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Training failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await resetTraining();
      setResult(null);
      setError(null);
      alert('Training state reset successfully');
    } catch (err) {
      setError('Failed to reset training');
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Training Control Panel
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure and start federated learning training
        </Typography>
      </Box>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h6" gutterBottom>
          Training Configuration
        </Typography>

        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Number of Clients (Banks)"
              type="number"
              value={config.n_clients}
              onChange={(e) => handleConfigChange('n_clients', parseInt(e.target.value))}
              inputProps={{ min: 2, max: 10 }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Training Rounds"
              type="number"
              value={config.n_rounds}
              onChange={(e) => handleConfigChange('n_rounds', parseInt(e.target.value))}
              inputProps={{ min: 1, max: 50 }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Local Epochs"
              type="number"
              value={config.local_epochs}
              onChange={(e) => handleConfigChange('local_epochs', parseInt(e.target.value))}
              inputProps={{ min: 1, max: 20 }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Batch Size"
              type="number"
              value={config.batch_size}
              onChange={(e) => handleConfigChange('batch_size', parseInt(e.target.value))}
              inputProps={{ min: 8, max: 128, step: 8 }}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Privacy Settings
        </Typography>

        <Box mb={3}>
          <FormControlLabel
            control={
              <Switch
                checked={config.use_dp}
                onChange={(e) => handleConfigChange('use_dp', e.target.checked)}
                color="primary"
              />
            }
            label="Enable Differential Privacy"
          />
          <Typography variant="caption" color="text.secondary" display="block" ml={4}>
            Adds calibrated noise to protect individual data points
          </Typography>
        </Box>

        <Box mb={3}>
          <FormControlLabel
            control={
              <Switch
                checked={config.use_secure_agg}
                onChange={(e) => handleConfigChange('use_secure_agg', e.target.checked)}
                color="primary"
              />
            }
            label="Enable Secure Aggregation"
          />
          <Typography variant="caption" color="text.secondary" display="block" ml={4}>
            Encrypts model updates before aggregation
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Action Buttons */}
        <Box display="flex" gap={2}>
          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={handleTrain}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
          >
            {loading ? 'Training...' : 'Start Training'}
          </Button>

          <Button
            variant="outlined"
            size="large"
            onClick={handleReset}
            disabled={loading}
            startIcon={<Refresh />}
          >
            Reset
          </Button>
        </Box>

        {/* Results */}
        {error && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {error}
          </Alert>
        )}

        {result && result.status === 'success' && (
          <Alert severity="success" sx={{ mt: 3 }}>
            <Typography variant="body2" fontWeight="bold">
              Training completed successfully!
            </Typography>
            <Typography variant="body2" mt={1}>
              Federated AUC: {result.results?.federated_model?.auc?.toFixed(4) || 'N/A'}
            </Typography>
            <Typography variant="body2">
              Privacy Budget (ε): {result.results?.privacy_metrics?.epsilon?.toFixed(2) || 'N/A'}
            </Typography>
          </Alert>
        )}
      </Paper>

      {/* Configuration Summary */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: '#f5f5f5' }}>
        <Typography variant="h6" gutterBottom>
          Configuration Summary
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Clients
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {config.n_clients}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Rounds
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {config.n_rounds}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Local Epochs
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {config.local_epochs}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Batch Size
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {config.batch_size}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Differential Privacy
            </Typography>
            <Typography variant="body1" fontWeight="bold" color={config.use_dp ? 'success.main' : 'error.main'}>
              {config.use_dp ? 'Enabled' : 'Disabled'}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Secure Aggregation
            </Typography>
            <Typography variant="body1" fontWeight="bold" color={config.use_secure_agg ? 'success.main' : 'error.main'}>
              {config.use_secure_agg ? 'Enabled' : 'Disabled'}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default TrainingControl;
