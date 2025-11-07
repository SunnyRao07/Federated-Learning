"""
Model aggregation logic for federated learning
"""
import numpy as np
from typing import List, Tuple

class ModelAggregator:
    """
    Aggregates model updates from multiple clients
    Supports various aggregation strategies
    """
    
    def __init__(self, strategy='fedavg'):
        """
        Initialize aggregator
        
        Args:
            strategy: Aggregation strategy ('fedavg', 'weighted', 'median')
        """
        self.strategy = strategy
        
    def aggregate(self, client_weights: List, client_sizes: List[int] = None):
        """
        Aggregate client model weights
        
        Args:
            client_weights: List of weight arrays from each client
            client_sizes: Optional list of dataset sizes for weighted aggregation
        
        Returns:
            Aggregated weights
        """
        if self.strategy == 'fedavg':
            return self._federated_averaging(client_weights, client_sizes)
        elif self.strategy == 'weighted':
            if client_sizes is None:
                raise ValueError("Client sizes required for weighted aggregation")
            return self._weighted_aggregation(client_weights, client_sizes)
        elif self.strategy == 'median':
            return self._median_aggregation(client_weights)
        else:
            raise ValueError(f"Unknown aggregation strategy: {self.strategy}")
    
    def _federated_averaging(self, client_weights: List, client_sizes: List[int] = None):
        """Standard FedAvg algorithm"""
        if client_sizes is not None:
            return self._weighted_aggregation(client_weights, client_sizes)
        
        # Simple averaging
        n_clients = len(client_weights)
        avg_weights = [np.zeros_like(w) for w in client_weights[0]]
        
        for weights in client_weights:
            for i, w in enumerate(weights):
                avg_weights[i] += w / n_clients
        
        return avg_weights
    
    def _weighted_aggregation(self, client_weights: List, client_sizes: List[int]):
        """Weighted aggregation based on dataset sizes"""
        total_size = sum(client_sizes)
        avg_weights = [np.zeros_like(w) for w in client_weights[0]]
        
        for weights, size in zip(client_weights, client_sizes):
            weight_factor = size / total_size
            for i, w in enumerate(weights):
                avg_weights[i] += w * weight_factor
        
        return avg_weights
    
    def _median_aggregation(self, client_weights: List):
        """
        Median aggregation (robust to outliers)
        Takes median of each weight parameter across clients
        """
        n_layers = len(client_weights[0])
        median_weights = []
        
        for layer_idx in range(n_layers):
            # Stack weights from all clients for this layer
            layer_weights = np.stack([w[layer_idx] for w in client_weights])
            
            # Take median across clients
            median_layer = np.median(layer_weights, axis=0)
            median_weights.append(median_layer)
        
        return median_weights
    
    def compute_weight_divergence(self, client_weights: List):
        """
        Compute divergence between client weights
        Useful for detecting malicious clients
        """
        n_clients = len(client_weights)
        divergences = []
        
        # Compute average weights
        avg_weights = self._federated_averaging(client_weights)
        
        # Compute divergence for each client
        for weights in client_weights:
            divergence = 0
            for w_client, w_avg in zip(weights, avg_weights):
                divergence += np.sum((w_client - w_avg) ** 2)
            divergences.append(divergence)
        
        return divergences
    
    def filter_outliers(self, client_weights: List, threshold: float = 2.0):
        """
        Filter out outlier clients based on weight divergence
        
        Args:
            client_weights: List of client weights
            threshold: Standard deviations from mean to consider outlier
        
        Returns:
            Filtered client weights
        """
        divergences = self.compute_weight_divergence(client_weights)
        
        mean_div = np.mean(divergences)
        std_div = np.std(divergences)
        
        filtered_weights = []
        for i, (weights, div) in enumerate(zip(client_weights, divergences)):
            if abs(div - mean_div) <= threshold * std_div:
                filtered_weights.append(weights)
            else:
                print(f"Warning: Client {i} filtered as outlier (divergence: {div:.2f})")
        
        return filtered_weights if filtered_weights else client_weights


class AdaptiveAggregator(ModelAggregator):
    """
    Adaptive aggregation that adjusts based on client performance
    """
    
    def __init__(self):
        super().__init__(strategy='adaptive')
        self.client_performance_history = []
    
    def aggregate_with_performance(self, client_weights: List, client_performances: List[float]):
        """
        Aggregate weights based on client performance
        Better performing clients get higher weight
        
        Args:
            client_weights: List of client weights
            client_performances: List of performance metrics (e.g., accuracy)
        """
        # Normalize performance scores
        performances = np.array(client_performances)
        if performances.sum() == 0:
            # Fallback to uniform weighting
            return self._federated_averaging(client_weights)
        
        weights_normalized = performances / performances.sum()
        
        # Weighted aggregation
        avg_weights = [np.zeros_like(w) for w in client_weights[0]]
        
        for weights, weight_factor in zip(client_weights, weights_normalized):
            for i, w in enumerate(weights):
                avg_weights[i] += w * weight_factor
        
        return avg_weights


if __name__ == "__main__":
    # Test aggregator
    aggregator = ModelAggregator(strategy='fedavg')
    
    # Simulate client weights
    n_clients = 3
    dummy_weights = [
        [np.random.randn(10, 5), np.random.randn(5)]
        for _ in range(n_clients)
    ]
    
    # Test aggregation
    aggregated = aggregator.aggregate(dummy_weights)
    print(f"Aggregated {len(aggregated)} layers")
    
    # Test divergence
    divergences = aggregator.compute_weight_divergence(dummy_weights)
    print(f"Client divergences: {divergences}")
