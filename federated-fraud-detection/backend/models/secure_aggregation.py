"""
Secure aggregation implementation for federated learning
"""
import numpy as np
from cryptography.fernet import Fernet
import hashlib

class SecureAggregator:
    """
    Implements secure aggregation with additive masking
    Simulates secure multi-party computation for model updates
    """
    
    def __init__(self, n_clients):
        self.n_clients = n_clients
        self.client_keys = {}
        self._generate_keys()
        
    def _generate_keys(self):
        """Generate encryption keys for each client"""
        for i in range(self.n_clients):
            self.client_keys[i] = Fernet.generate_key()
    
    def add_noise_mask(self, weights, client_id, noise_scale=0.01):
        """
        Add noise mask to client weights for secure aggregation
        Each client adds random noise that cancels out during aggregation
        """
        np.random.seed(client_id)  # Deterministic noise based on client ID
        
        masked_weights = []
        for w in weights:
            # Add random noise
            noise = np.random.normal(0, noise_scale, w.shape)
            masked_w = w + noise
            masked_weights.append(masked_w)
        
        return masked_weights
    
    def remove_noise_mask(self, weights, client_id, noise_scale=0.01):
        """Remove noise mask (for simulation purposes)"""
        np.random.seed(client_id)
        
        unmasked_weights = []
        for w in weights:
            noise = np.random.normal(0, noise_scale, w.shape)
            unmasked_w = w - noise
            unmasked_weights.append(unmasked_w)
        
        return unmasked_weights
    
    def aggregate_with_secure_protocol(self, client_weights_list, noise_scale=0.01):
        """
        Securely aggregate client weights
        In real implementation, noise would cancel out mathematically
        Here we simulate the secure aggregation process
        """
        n_clients = len(client_weights_list)
        
        # Step 1: Each client adds their noise mask
        masked_weights_list = []
        for client_id, weights in enumerate(client_weights_list):
            masked = self.add_noise_mask(weights, client_id, noise_scale)
            masked_weights_list.append(masked)
        
        # Step 2: Aggregate masked weights
        aggregated_masked = self._average_weights(masked_weights_list)
        
        # Step 3: Remove noise masks (they cancel out in real protocol)
        # In actual secure aggregation, paired noise cancels automatically
        # Here we simulate by removing the average noise
        aggregated_weights = []
        for layer_idx, layer_weights in enumerate(aggregated_masked):
            # Calculate average noise that was added
            total_noise = np.zeros_like(layer_weights)
            for client_id in range(n_clients):
                np.random.seed(client_id)
                noise = np.random.normal(0, noise_scale, layer_weights.shape)
                total_noise += noise
            
            avg_noise = total_noise / n_clients
            clean_weights = layer_weights - avg_noise
            aggregated_weights.append(clean_weights)
        
        return aggregated_weights
    
    def _average_weights(self, weights_list):
        """Average weights from multiple clients"""
        n_clients = len(weights_list)
        
        # Initialize with zeros
        avg_weights = [np.zeros_like(w) for w in weights_list[0]]
        
        # Sum all weights
        for weights in weights_list:
            for i, w in enumerate(weights):
                avg_weights[i] += w
        
        # Average
        avg_weights = [w / n_clients for w in avg_weights]
        
        return avg_weights
    
    def compute_communication_cost(self, weights):
        """Calculate communication cost (size of model updates)"""
        total_bytes = 0
        for w in weights:
            total_bytes += w.nbytes
        
        # Convert to MB
        total_mb = total_bytes / (1024 * 1024)
        return total_mb
    
    def verify_integrity(self, weights):
        """Verify integrity of weights using hash"""
        # Concatenate all weights
        weights_bytes = b''.join([w.tobytes() for w in weights])
        
        # Compute hash
        hash_obj = hashlib.sha256(weights_bytes)
        return hash_obj.hexdigest()


class FederatedAveraging:
    """Standard Federated Averaging (FedAvg) algorithm"""
    
    def __init__(self, n_clients):
        self.n_clients = n_clients
    
    def aggregate(self, client_weights_list, client_sample_sizes=None):
        """
        Aggregate client weights using weighted averaging
        
        Args:
            client_weights_list: List of weight arrays from each client
            client_sample_sizes: Optional list of sample sizes for weighted averaging
        """
        if client_sample_sizes is None:
            # Simple averaging
            return self._simple_average(client_weights_list)
        else:
            # Weighted averaging based on dataset size
            return self._weighted_average(client_weights_list, client_sample_sizes)
    
    def _simple_average(self, weights_list):
        """Simple average of weights"""
        n_clients = len(weights_list)
        avg_weights = [np.zeros_like(w) for w in weights_list[0]]
        
        for weights in weights_list:
            for i, w in enumerate(weights):
                avg_weights[i] += w
        
        avg_weights = [w / n_clients for w in avg_weights]
        return avg_weights
    
    def _weighted_average(self, weights_list, sample_sizes):
        """Weighted average based on client dataset sizes"""
        total_samples = sum(sample_sizes)
        
        # Initialize
        avg_weights = [np.zeros_like(w) for w in weights_list[0]]
        
        # Weighted sum
        for weights, n_samples in zip(weights_list, sample_sizes):
            weight_factor = n_samples / total_samples
            for i, w in enumerate(weights):
                avg_weights[i] += w * weight_factor
        
        return avg_weights


if __name__ == "__main__":
    # Test secure aggregation
    n_clients = 5
    aggregator = SecureAggregator(n_clients)
    
    # Simulate client weights
    dummy_weights = [
        [np.random.randn(10, 5), np.random.randn(5)]
        for _ in range(n_clients)
    ]
    
    # Test secure aggregation
    aggregated = aggregator.aggregate_with_secure_protocol(dummy_weights)
    print(f"Aggregated {len(aggregated)} weight layers")
    print(f"Communication cost: {aggregator.compute_communication_cost(aggregated):.2f} MB")
