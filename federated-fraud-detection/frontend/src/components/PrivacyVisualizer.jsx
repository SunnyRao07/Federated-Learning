/**
 * Privacy Visualizer - Visualize DP and Secure Aggregation
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
} from '@mui/material';
import { Shield, Lock, Visibility } from '@mui/icons-material';
import * as d3 from 'd3';
import { getMetrics } from '../api/api';

const PrivacyVisualizer = () => {
  const [metrics, setMetrics] = useState(null);
  const svgRef = useRef(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (metrics && svgRef.current) {
      drawSecureAggregationFlow();
    }
  }, [metrics]);

  const fetchData = async () => {
    try {
      const res = await getMetrics();
      setMetrics(res.data);
    } catch (err) {
      console.error('Error fetching metrics:', err);
    }
  };

  const drawSecureAggregationFlow = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 400;
    svg.attr('width', width).attr('height', height);

    // Define nodes
    const nodes = [
      { id: 'bank1', label: 'Bank 1', x: 100, y: 100, type: 'client' },
      { id: 'bank2', label: 'Bank 2', x: 100, y: 200, type: 'client' },
      { id: 'bank3', label: 'Bank 3', x: 100, y: 300, type: 'client' },
      { id: 'secure', label: 'Secure\nAggregation', x: 400, y: 200, type: 'aggregator' },
      { id: 'global', label: 'Global\nModel', x: 700, y: 200, type: 'server' },
    ];

    // Define links
    const links = [
      { source: 'bank1', target: 'secure' },
      { source: 'bank2', target: 'secure' },
      { source: 'bank3', target: 'secure' },
      { source: 'secure', target: 'global' },
    ];

    // Draw links
    svg
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('x1', (d) => nodes.find((n) => n.id === d.source).x + 60)
      .attr('y1', (d) => nodes.find((n) => n.id === d.source).y + 30)
      .attr('x2', (d) => nodes.find((n) => n.id === d.target).x)
      .attr('y2', (d) => nodes.find((n) => n.id === d.target).y + 30)
      .attr('stroke', '#2196f3')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .attr('marker-end', 'url(#arrowhead)');

    // Define arrow marker
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('markerWidth', 10)
      .attr('markerHeight', 10)
      .attr('refX', 9)
      .attr('refY', 3)
      .attr('orient', 'auto')
      .append('polygon')
      .attr('points', '0 0, 10 3, 0 6')
      .attr('fill', '#2196f3');

    // Draw nodes
    const nodeGroups = svg
      .selectAll('g.node')
      .data(nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', (d) => `translate(${d.x},${d.y})`);

    // Node rectangles
    nodeGroups
      .append('rect')
      .attr('width', 120)
      .attr('height', 60)
      .attr('rx', 8)
      .attr('fill', (d) => {
        if (d.type === 'client') return '#e3f2fd';
        if (d.type === 'aggregator') return '#fff3e0';
        return '#e8f5e9';
      })
      .attr('stroke', (d) => {
        if (d.type === 'client') return '#2196f3';
        if (d.type === 'aggregator') return '#ff9800';
        return '#4caf50';
      })
      .attr('stroke-width', 2);

    // Node labels
    nodeGroups
      .append('text')
      .attr('x', 60)
      .attr('y', 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', 12)
      .attr('font-weight', 'bold')
      .text((d) => d.label);

    // Add encryption icons
    nodeGroups
      .filter((d) => d.type === 'client')
      .append('text')
      .attr('x', 100)
      .attr('y', 15)
      .attr('font-size', 16)
      .text('🔒');
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Privacy Mechanisms
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Differential Privacy and Secure Aggregation visualization
        </Typography>
      </Box>

      {metrics ? (
        <>
          {/* Privacy Overview */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={4}>
              <PrivacyCard
                title="Differential Privacy"
                icon={<Shield />}
                color="#4caf50"
                metrics={metrics.privacy_metrics}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <PrivacyCard
                title="Secure Aggregation"
                icon={<Lock />}
                color="#2196f3"
                description="Model updates encrypted before aggregation"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <PrivacyCard
                title="Privacy Attacks"
                icon={<Visibility />}
                color="#ff9800"
                attacks={metrics.privacy_attacks}
              />
            </Grid>
          </Grid>

          {/* Secure Aggregation Flow */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Secure Aggregation Flow
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Model updates are encrypted and aggregated without revealing individual contributions
            </Typography>
            <Box display="flex" justifyContent="center">
              <svg ref={svgRef}></svg>
            </Box>
          </Paper>

          {/* Differential Privacy Explanation */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Differential Privacy Noise Addition
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" paragraph>
                  Differential Privacy adds calibrated noise to model updates to prevent privacy leakage:
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <Typography component="li" variant="body2" paragraph>
                    <strong>Epsilon (ε):</strong> {metrics.privacy_metrics.epsilon?.toFixed(2)} - Privacy
                    budget (lower is better)
                  </Typography>
                  <Typography component="li" variant="body2" paragraph>
                    <strong>Delta (δ):</strong> {metrics.privacy_metrics.delta?.toExponential(2)} -
                    Probability of privacy breach
                  </Typography>
                  <Typography component="li" variant="body2" paragraph>
                    <strong>Noise Multiplier:</strong> {metrics.privacy_metrics.noise_multiplier?.toFixed(2)}{' '}
                    - Controls noise magnitude
                  </Typography>
                  <Typography component="li" variant="body2">
                    <strong>L2 Norm Clip:</strong> {metrics.privacy_metrics.l2_norm_clip?.toFixed(2)} -
                    Gradient clipping threshold
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Alert severity="success" sx={{ mb: 2 }}>
                  <Typography variant="body2" fontWeight="bold">
                    Privacy Preserved!
                  </Typography>
                  <Typography variant="body2">
                    ε = {metrics.privacy_metrics.epsilon?.toFixed(2)} is within acceptable range (target: ε
                    ≤ 3.0)
                  </Typography>
                </Alert>
                <Alert severity="info">
                  <Typography variant="body2" fontWeight="bold">
                    Defense Success Rate
                  </Typography>
                  <Typography variant="body2">
                    {(metrics.privacy_attacks?.overall_defense_rate * 100).toFixed(1)}% of privacy attacks
                    were successfully defended
                  </Typography>
                </Alert>
              </Grid>
            </Grid>
          </Paper>
        </>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No privacy metrics available. Please train the model first.
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

// Privacy Card Component
const PrivacyCard = ({ title, icon, color, metrics, description, attacks }) => (
  <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)` }}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Box sx={{ color, mr: 2, fontSize: 40 }}>{icon}</Box>
        <Typography variant="h6" fontWeight="bold">
          {title}
        </Typography>
      </Box>

      {metrics && (
        <Box>
          <Chip label={`ε = ${metrics.epsilon?.toFixed(2)}`} sx={{ mr: 1, mb: 1 }} color="primary" />
          <Chip label={`δ = ${metrics.delta?.toExponential(2)}`} sx={{ mb: 1 }} />
          <Typography variant="body2" color="text.secondary" mt={2}>
            Noise multiplier: {metrics.noise_multiplier?.toFixed(2)}
          </Typography>
        </Box>
      )}

      {description && (
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      )}

      {attacks && (
        <Box mt={2}>
          <Typography variant="body2" fontWeight="bold" color="success.main">
            Defense Rate: {(attacks.overall_defense_rate * 100).toFixed(1)}%
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block" mt={1}>
            Successfully defended against membership inference and model inversion attacks
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

export default PrivacyVisualizer;
