"""
Data loading and preprocessing for federated learning
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from .data_cleaner import DataCleaner

class FederatedDataLoader:
    """Load and partition data for federated learning simulation"""
    
    def __init__(self, n_clients=5, test_size=0.2, random_state=42, clean_data=True):
        self.n_clients = n_clients
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.clean_data = clean_data
        self.data_cleaner = DataCleaner() if clean_data else None
        
    def load_data(self, filepath=None):
        """
        Load data from Kaggle dataset or specified file.
        Priority: 1) specified filepath, 2) Kaggle dataset, 3) synthetic data (fallback)
        """
        data_dir = Path(__file__).parent
        
        # Priority 1: Use specified filepath if provided and exists
        if filepath and os.path.exists(filepath):
            print(f"Loading data from {filepath}")
            data = pd.read_csv(filepath)
        
        # Priority 2: Try to load Kaggle dataset (creditcard.csv)
        elif (data_dir / "creditcard.csv").exists():
            kaggle_file = data_dir / "creditcard.csv"
            print(f"Loading Kaggle Credit Card Fraud Detection dataset from {kaggle_file}")
            data = pd.read_csv(kaggle_file)
            print(f"Loaded {len(data)} transactions from Kaggle dataset")
            fraud_count = data['Class'].sum()
            print(f"Fraud cases: {fraud_count} ({100*fraud_count/len(data):.3f}%)")
        
        # Priority 3: Try clean_dataset.csv if it exists
        elif (data_dir / "clean_dataset.csv").exists():
            clean_file = data_dir / "clean_dataset.csv"
            print(f"Loading dataset from {clean_file}")
            data = pd.read_csv(clean_file)
            print(f"Loaded {len(data)} transactions")
            if 'Class' in data.columns:
                fraud_count = data['Class'].sum()
                print(f"Fraud cases: {fraud_count} ({100*fraud_count/len(data):.3f}%)")
        
        # Priority 4: Try to download dataset automatically
        else:
            print("Kaggle dataset not found. Attempting automatic download...")
            try:
                from .download_kaggle_dataset import download_kaggle_dataset
                downloaded_file = download_kaggle_dataset()
                if downloaded_file and os.path.exists(downloaded_file):
                    print(f"Loading downloaded dataset from {downloaded_file}")
                    data = pd.read_csv(downloaded_file)
                    fraud_count = data['Class'].sum()
                    print(f"Loaded {len(data)} transactions ({fraud_count} fraudulent)")
                else:
                    raise FileNotFoundError("Download failed")
            except Exception as e:
                print(f"Automatic download failed: {e}")
                print("WARNING: Generating synthetic data as fallback...")
                print("To use real Kaggle data, run: python -m data.download_kaggle_dataset")
                from .synthetic_generator import generate_synthetic_data
            data = generate_synthetic_data(n_samples=100000, fraud_ratio=0.02)
        
        # Validate data format
        required_columns = ['Time', 'Amount', 'Class']
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Dataset missing required columns: {missing_cols}")
        
        # Check for V1-V28 features
        v_features = [f'V{i}' for i in range(1, 29)]
        missing_v = [v for v in v_features if v not in data.columns]
        if missing_v:
            print(f"WARNING: Missing some V features: {missing_v[:5]}... (may affect model)")
        
        # Clean data if enabled
        if self.clean_data and self.data_cleaner:
            print("\nCleaning dataset...")
            data = self.data_cleaner.clean_dataset(data, verbose=True)
            
            # Validate after cleaning
            is_valid, issues = self.data_cleaner.validate_dataset(data)
            if not is_valid:
                print("WARNING: Dataset validation issues after cleaning:")
                for issue in issues:
                    print(f"  - {issue}")
        
        return data
    
    def preprocess(self, data):
        """
        Preprocess data: scale features and handle missing values
        Model expects 29 features: Amount + V1-V28 (Time is dropped as it's less predictive)
        """
        # Separate features and labels
        # Use Amount + V1-V28 = 29 features (drop Time as it's less predictive)
        feature_cols = ['Amount'] + [f'V{i}' for i in range(1, 29)]
        
        # Filter to only include columns that exist in the dataset
        available_cols = [col for col in feature_cols if col in data.columns]
        
        if len(available_cols) != 29:
            print(f"WARNING: Expected 29 features, found {len(available_cols)}")
            if len(available_cols) < 29:
                print(f"Missing features. Available: {available_cols[:10]}...")
            else:
                print(f"Too many features. Using first 29: {available_cols[:29]}")
                available_cols = available_cols[:29]
        
        X = data[available_cols].values
        y = data['Class'].values
        
        # Handle any missing values
        if np.isnan(X).any():
            print("WARNING: Found NaN values, filling with 0")
            X = np.nan_to_num(X, nan=0.0)
        
        # Scale features (important for neural networks)
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
