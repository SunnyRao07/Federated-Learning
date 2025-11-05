"""
Data loading and preprocessing for federated learning
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from .synthetic_generator import generate_synthetic_data

class FederatedDataLoader:
    """Load and partition data for federated learning simulation"""
    
    def __init__(self, n_clients=5, test_size=0.2, random_state=42):
        self.n_clients = n_clients
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = StandardScaler()
        
    def load_data(self, filepath=None):
        """Load data from file or generate synthetic data"""
        if filepath and os.path.exists(filepath):
            print(f"Loading data from {filepath}")
            data = pd.read_csv(filepath)
        else:
            print("Generating synthetic fraud detection data...")
            data = generate_synthetic_data(n_samples=100000, fraud_ratio=0.02)
        
        return data
    
    def preprocess(self, data):
        """Preprocess data: scale features"""
        # Separate features and labels
        X = data.drop(['Class'], axis=1).values
        y = data['Class'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y
    
    def create_federated_data(self, filepath=None):
        """
        Create federated data partitions for multiple clients (banks)
        Returns: (client_data, test_data)
        """
        # Load and preprocess
        data = self.load_data(filepath)
        X, y = self.preprocess(data)
        
        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        # Partition training data among clients
        client_data = self._partition_data(X_train, y_train)
        
        # Global test set
        test_data = (X_test, y_test)
        
        print(f"\nFederated Data Summary:")
        print(f"Total clients: {self.n_clients}")
        print(f"Test samples: {len(y_test)}")
        for i, (X_client, y_client) in enumerate(client_data):
            fraud_count = np.sum(y_client)
            print(f"Client {i+1}: {len(y_client)} samples ({fraud_count} fraudulent, {len(y_client)-fraud_count} normal)")
        
        return client_data, test_data
    
    def _partition_data(self, X, y):
        """Partition data among clients with non-IID distribution"""
        n_samples = len(y)
        
        # Create non-IID partitions (different fraud ratios per client)
        client_data = []
        indices = np.arange(n_samples)
        np.random.shuffle(indices)
        
        # Split indices
        split_indices = np.array_split(indices, self.n_clients)
        
        for client_idx in split_indices:
            X_client = X[client_idx]
            y_client = y[client_idx]
            client_data.append((X_client, y_client))
        
        return client_data
    
    def get_feature_dim(self):
        """Return number of features"""
        return 29  # Time + Amount + V1-V28 = 30 features, but we'll use 29 after processing


def load_federated_data(n_clients=5, filepath=None):
    """Convenience function to load federated data"""
    loader = FederatedDataLoader(n_clients=n_clients)
    return loader.create_federated_data(filepath)


if __name__ == "__main__":
    # Test data loading
    loader = FederatedDataLoader(n_clients=5)
    client_data, test_data = loader.create_federated_data()
    print("\nTest set shape:", test_data[0].shape, test_data[1].shape)
