/**
 * Performance Charts - Visualize training metrics
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import Plot from 'react-plotly.js';
import { getHistory, getMetrics } from '../api/api';

const PerformanceCharts = () => {
  const [history, setHistory] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('auc');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [historyRes, metricsRes] = await Promise.all([
        getHistory().catch(() => null),
        getMetrics().catch(() => null),
      ]);

      if (historyRes) setHistory(historyRes.data);
      if (metricsRes) setMetrics(metricsRes.data);
    } catch (err) {
      console.error('Error fetching data:', err);
    }
  };

  const handleMetricChange = (event, newMetric) => {
    if (newMetric) setSelectedMetric(newMetric);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Performance Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Training progress and model performance metrics
        </Typography>
      </Box>

      {history && history.rounds && history.rounds.length > 0 ? (
        <>
          {/* Metric Selector */}
          <Box mb={3} display="flex" justifyContent="center">
            <ToggleButtonGroup
              value={selectedMetric}
              exclusive
              onChange={handleMetricChange}
              aria-label="metric selection"
            >
              <ToggleButton value="auc">AUC</ToggleButton>
              <ToggleButton value="accuracy">Accuracy</ToggleButton>
              <ToggleButton value="f1_score">F1 Score</ToggleButton>
              <ToggleButton value="precision">Precision</ToggleButton>
              <ToggleButton value="recall">Recall</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Training Progress Chart */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Training Progress - {selectedMetric.toUpperCase()}
            </Typography>
            <TrainingProgressChart
              rounds={history.rounds}
              metrics={history.metrics}
              selectedMetric={selectedMetric}
            />
          </Paper>

          {/* Comparison Charts */}
          {metrics && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Federated vs Local Performance
                  </Typography>
                  <ComparisonBarChart
                    federated={metrics.federated_model}
                    local={metrics.local_baseline}
                  />
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Performance Improvement
                  </Typography>
                  <ImprovementChart improvement={metrics.improvement} />
                </Paper>
              </Grid>
            </Grid>
          )}
        </>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No training history available. Please train the model first.
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

// Training Progress Chart
const TrainingProgressChart = ({ rounds, metrics, selectedMetric }) => {
  const values = metrics.map((m) => m[selectedMetric] || 0);

  const data = [
    {
      x: rounds,
      y: values,
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#2196f3', size: 8 },
      line: { color: '#2196f3', width: 3 },
      name: selectedMetric.toUpperCase(),
    },
  ];

  const layout = {
    xaxis: { title: 'Training Round', gridcolor: '#eee' },
    yaxis: { title: 'Score', gridcolor: '#eee', range: [0, 1] },
    plot_bgcolor: '#fafafa',
    paper_bgcolor: 'white',
    margin: { t: 20, r: 20, b: 50, l: 60 },
    height: 400,
  };

  return <Plot data={data} layout={layout} style={{ width: '100%' }} config={{ responsive: true }} />;
};

// Comparison Bar Chart
const ComparisonBarChart = ({ federated, local }) => {
  const metrics = ['accuracy', 'auc', 'precision', 'recall', 'f1_score'];
  const labels = ['Accuracy', 'AUC', 'Precision', 'Recall', 'F1 Score'];

  const data = [
    {
      x: labels,
      y: metrics.map((m) => local[m] || 0),
      type: 'bar',
      name: 'Local Model',
      marker: { color: '#ff9800' },
    },
    {
      x: labels,
      y: metrics.map((m) => federated[m] || 0),
      type: 'bar',
      name: 'Federated Model',
      marker: { color: '#4caf50' },
    },
  ];

  const layout = {
    barmode: 'group',
    xaxis: { title: 'Metrics' },
    yaxis: { title: 'Score', range: [0, 1], gridcolor: '#eee' },
    plot_bgcolor: '#fafafa',
    paper_bgcolor: 'white',
    margin: { t: 20, r: 20, b: 50, l: 60 },
    height: 400,
    legend: { x: 0.7, y: 1 },
  };

  return <Plot data={data} layout={layout} style={{ width: '100%' }} config={{ responsive: true }} />;
};

// Improvement Chart
const ImprovementChart = ({ improvement }) => {
  const metrics = ['accuracy', 'auc', 'f1_score', 'precision', 'recall'];
  const labels = ['Accuracy', 'AUC', 'F1 Score', 'Precision', 'Recall'];
  const values = metrics.map((m) => improvement[m] || 0);

  const colors = values.map((v) => (v > 0 ? '#4caf50' : '#f44336'));

  const data = [
    {
      x: labels,
      y: values,
      type: 'bar',
      marker: { color: colors },
      text: values.map((v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}%`),
      textposition: 'outside',
    },
  ];

  const layout = {
    xaxis: { title: 'Metrics' },
    yaxis: { title: 'Improvement (%)', gridcolor: '#eee' },
    plot_bgcolor: '#fafafa',
    paper_bgcolor: 'white',
    margin: { t: 40, r: 20, b: 50, l: 60 },
    height: 400,
    showlegend: false,
  };

  return <Plot data={data} layout={layout} style={{ width: '100%' }} config={{ responsive: true }} />;
};

export default PerformanceCharts;
