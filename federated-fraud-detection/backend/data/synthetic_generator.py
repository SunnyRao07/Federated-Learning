"""
Synthetic fraud transaction data generator
"""
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

class SyntheticFraudDataGenerator:
    """Generate synthetic credit card transaction data with fraud labels"""
    
    def __init__(self, n_samples=100000, fraud_ratio=0.02, random_state=42):
        self.n_samples = n_samples
        self.fraud_ratio = fraud_ratio
        self.random_state = random_state
        np.random.seed(random_state)
        random.seed(random_state)
        Faker.seed(random_state)
        
    def generate(self):
        """Generate synthetic transaction dataset"""
        print(f"Generating {self.n_samples} synthetic transactions...")
        
        n_fraud = int(self.n_samples * self.fraud_ratio)
        n_normal = self.n_samples - n_fraud
        
        # Generate normal transactions
        normal_data = self._generate_normal_transactions(n_normal)
        
        # Generate fraudulent transactions
        fraud_data = self._generate_fraud_transactions(n_fraud)
        
        # Combine and shuffle
        data = pd.concat([normal_data, fraud_data], ignore_index=True)
        data = data.sample(frac=1, random_state=self.random_state).reset_index(drop=True)
        
        print(f"Generated dataset: {len(data)} transactions ({n_fraud} fraudulent)")
        return data
    
    def _generate_normal_transactions(self, n):
        """Generate normal transaction patterns"""
        data = {
            'Time': np.random.uniform(0, 172800, n),  # 48 hours in seconds
            'Amount': np.random.lognormal(3.5, 1.2, n),  # Log-normal distribution
        }
        
        # Generate 28 PCA-like features (V1-V28)
        # Normal transactions cluster around origin
        for i in range(1, 29):
            if i <= 14:
                data[f'V{i}'] = np.random.normal(0, 1.0, n)
            else:
                data[f'V{i}'] = np.random.normal(0, 0.8, n)
        
        data['Class'] = 0
        return pd.DataFrame(data)
    
    def _generate_fraud_transactions(self, n):
        """Generate fraudulent transaction patterns"""
        data = {
            'Time': np.random.uniform(0, 172800, n),
            'Amount': np.random.lognormal(4.5, 1.5, n),  # Higher amounts
        }
        
        # Fraudulent transactions have different patterns
        for i in range(1, 29):
            if i in [1, 3, 4, 10, 12, 14, 17]:  # Key fraud indicators
                data[f'V{i}'] = np.random.normal(2.5, 1.5, n)
            elif i in [2, 5, 11]:
                data[f'V{i}'] = np.random.normal(-2.0, 1.2, n)
            else:
                data[f'V{i}'] = np.random.normal(0, 1.5, n)
        
        data['Class'] = 1
        return pd.DataFrame(data)
    
    def save(self, filepath):
        """Generate and save dataset"""
        data = self.generate()
        data.to_csv(filepath, index=False)
        print(f"Dataset saved to {filepath}")
        return data


def generate_synthetic_data(n_samples=100000, fraud_ratio=0.02):
    """Convenience function to generate synthetic data"""
    generator = SyntheticFraudDataGenerator(n_samples, fraud_ratio)
    return generator.generate()


if __name__ == "__main__":
    # Test generation
    generator = SyntheticFraudDataGenerator(n_samples=10000)
    data = generator.generate()
    print("\nDataset Info:")
    print(data.info())
    print("\nClass Distribution:")
    print(data['Class'].value_counts())
    print("\nSample Statistics:")
    print(data.describe())
