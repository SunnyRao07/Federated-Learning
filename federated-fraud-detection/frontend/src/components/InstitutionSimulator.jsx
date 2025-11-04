/**
 * Institution Simulator - Visualize federated clients
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
} from '@mui/material';
import { AccountBalance, DataUsage } from '@mui/icons-material';
import { getClients, getStatus } from '../api/api';

const InstitutionSimulator = () => {
  const [clients, setClients] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [clientsRes, statusRes] = await Promise.all([
        getClients().catch(() => ({ data: { clients: [] } })),
        getStatus(),
      ]);

      setClients(clientsRes.data.clients || []);
      setStatus(statusRes.data);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Financial Institution Simulator
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Visualizing federated learning across multiple banks
        </Typography>
      </Box>

      {/* Training Status */}
      {status && status.status === 'training' && (
        <Paper sx={{ p: 3, mb: 3, bgcolor: '#e3f2fd' }}>
          <Typography variant="h6" gutterBottom>
            Training in Progress
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            <Box flexGrow={1}>
              <LinearProgress
                variant="determinate"
                value={status.progress_percentage}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
            <Typography variant="body2" fontWeight="bold">
              {status.progress_percentage.toFixed(0)}%
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" mt={1}>
            Round {status.current_round} of {status.total_rounds}
          </Typography>
        </Paper>
      )}

      {/* Clients Grid */}
      {clients.length > 0 ? (
        <Grid container spacing={3}>
          {clients.map((client) => (
            <Grid item xs={12} sm={6} md={4} key={client.client_id}>
              <ClientCard client={client} isTraining={status?.status === 'training'} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No client data available. Please train the model first.
          </Typography>
        </Paper>
      )}

      {/* Summary Statistics */}
      {clients.length > 0 && (
        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Network Summary
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary" fontWeight="bold">
                  {clients.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Institutions
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary" fontWeight="bold">
                  {clients.reduce((sum, c) => sum + c.total_samples, 0).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Transactions
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="error" fontWeight="bold">
                  {clients.reduce((sum, c) => sum + c.fraud_samples, 0).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Fraudulent Transactions
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Container>
  );
};

// Client Card Component
const ClientCard = ({ client, isTraining }) => {
  const fraudPercentage = (client.fraud_ratio * 100).toFixed(2);

  return (
    <Card
      sx={{
        height: '100%',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
        border: isTraining ? '2px solid #2196f3' : 'none',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <AccountBalance sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
          <Box>
            <Typography variant="h6" fontWeight="bold">
              Bank {client.client_id}
            </Typography>
            {isTraining && (
              <Chip label="Training" size="small" color="primary" sx={{ mt: 0.5 }} />
            )}
          </Box>
        </Box>

        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Total Samples
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {client.total_samples.toLocaleString()}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Normal
            </Typography>
            <Typography variant="body2" color="success.main" fontWeight="bold">
              {client.normal_samples.toLocaleString()}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Fraudulent
            </Typography>
            <Typography variant="body2" color="error.main" fontWeight="bold">
              {client.fraud_samples.toLocaleString()}
            </Typography>
          </Box>
        </Box>

        <Box>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="caption" color="text.secondary">
              Fraud Rate
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {fraudPercentage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={parseFloat(fraudPercentage)}
            color={parseFloat(fraudPercentage) > 5 ? 'error' : 'warning'}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>

        <Box mt={2} display="flex" alignItems="center" gap={1}>
          <DataUsage sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="caption" color="text.secondary">
            Data stays local - Privacy preserved
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default InstitutionSimulator;
