"""
Federated learning trainer
"""
import numpy as np
import json
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.fraud_model import FraudDetectionModel
from models.secure_aggregation import SecureAggregator, FederatedAveraging
from app.privacy import DifferentialPrivacyManager, PrivacyAttackSimulator
from data.load_data import FederatedDataLoader

class FederatedTrainer:
    """
    Orchestrates federated learning training across multiple clients
    """
    
    def __init__(self, n_clients=5, n_rounds=10, local_epochs=5, batch_size=32,
                 use_dp=True, use_secure_agg=True):
        self.n_clients = n_clients
        self.n_rounds = n_rounds
        self.local_epochs = local_epochs
        self.batch_size = batch_size
        self.use_dp = use_dp
        self.use_secure_agg = use_secure_agg
        
        # Initialize components
        self.data_loader = FederatedDataLoader(n_clients=n_clients)
        self.global_model = FraudDetectionModel(input_dim=29)
        self.global_model.build_model()
        
        self.secure_aggregator = SecureAggregator(n_clients) if use_secure_agg else None
        self.fed_avg = FederatedAveraging(n_clients)
        self.dp_manager = DifferentialPrivacyManager(
            l2_norm_clip=1.0,
            noise_multiplier=1.1,
            num_microbatches=32
        ) if use_dp else None
        
        # Training history
        self.history = {
            'rounds': [],
            'global_metrics': [],
            'client_metrics': [],
            'privacy_metrics': [],
            'communication_costs': []
        }
        
        self.client_data = None
        self.test_data = None
        
    def load_data(self, filepath=None):
        """Load and partition data for federated learning"""
        print("Loading federated data...")
        self.client_data, self.test_data = self.data_loader.create_federated_data(filepath)
        print(f"Data loaded: {self.n_clients} clients, {len(self.test_data[1])} test samples")
        
    def train_local_model(self, client_id, X_train, y_train):
        """Train a local model for one client"""
        # Create local model with same architecture
        local_model = FraudDetectionModel(input_dim=29)
        local_model.build_model()
        
        # Initialize with global weights
        local_model.set_weights(self.global_model.get_weights())
        
        # Train locally
        local_model.train(
            X_train, y_train,
            epochs=self.local_epochs,
            batch_size=self.batch_size,
            verbose=0
        )
        
        # Get updated weights
        updated_weights = local_model.get_weights()
        
        # Apply differential privacy if enabled
        if self.use_dp:
            updated_weights = self.dp_manager.add_noise_to_weights(updated_weights)
        
        return updated_weights
    
    def federated_round(self, round_num):
        """Execute one round of federated learning"""
        print(f"\n--- Round {round_num + 1}/{self.n_rounds} ---")
        
        client_weights_list = []
        client_sample_sizes = []
        
        # Train on each client
        for client_id, (X_client, y_client) in enumerate(self.client_data):
            print(f"Training client {client_id + 1}/{self.n_clients}...", end=' ')
            
            # Train local model
            weights = self.train_local_model(client_id, X_client, y_client)
            client_weights_list.append(weights)
            client_sample_sizes.append(len(y_client))
            
            print("✓")
        
        # Aggregate weights
        print("Aggregating models...", end=' ')
        if self.use_secure_agg:
            aggregated_weights = self.secure_aggregator.aggregate_with_secure_protocol(
                client_weights_list
            )
        else:
            aggregated_weights = self.fed_avg.aggregate(
                client_weights_list,
                client_sample_sizes
            )
        print("✓")
        
        # Update global model
        self.global_model.set_weights(aggregated_weights)
        
        # Evaluate global model
        metrics = self.evaluate_global_model()
        
        # Calculate communication cost
        comm_cost = self.secure_aggregator.compute_communication_cost(aggregated_weights) if self.secure_aggregator else 0
        
        # Store history
        self.history['rounds'].append(round_num + 1)
        self.history['global_metrics'].append(metrics)
        self.history['communication_costs'].append(comm_cost)
        
        print(f"Global Model - AUC: {metrics['auc']:.4f}, F1: {metrics['f1_score']:.4f}, Accuracy: {metrics['accuracy']:.4f}")
        
        return metrics
    
    def train(self):
        """Run complete federated training"""
        print("\n" + "="*60)
        print("FEDERATED LEARNING TRAINING")
        print("="*60)
        print(f"Clients: {self.n_clients}")
        print(f"Rounds: {self.n_rounds}")
        print(f"Local Epochs: {self.local_epochs}")
        print(f"Differential Privacy: {self.use_dp}")
        print(f"Secure Aggregation: {self.use_secure_agg}")
        print("="*60)
        
        # Load data if not already loaded
        if self.client_data is None:
            self.load_data()
        
        # Training rounds
        for round_num in range(self.n_rounds):
            self.federated_round(round_num)
        
        # Compute privacy budget
        if self.use_dp:
            avg_samples = np.mean([len(y) for _, y in self.client_data])
            epsilon, delta = self.dp_manager.compute_privacy_budget(
                n_samples=int(avg_samples),
                batch_size=self.batch_size,
                epochs=self.local_epochs * self.n_rounds
            )
            self.history['privacy_metrics'] = {
                'epsilon': epsilon,
                'delta': delta,
                'noise_multiplier': self.dp_manager.noise_multiplier,
                'l2_norm_clip': self.dp_manager.l2_norm_clip
            }
            print(f"\nPrivacy Budget: ε = {epsilon:.2f}, δ = {delta:.2e}")
        
        print("\n" + "="*60)
        print("TRAINING COMPLETED")
        print("="*60)
        
        return self.history
    
    def evaluate_global_model(self):
        """Evaluate the global model on test set"""
        X_test, y_test = self.test_data
        metrics = self.global_model.evaluate(X_test, y_test)
        return metrics
    
    def train_local_baseline(self):
        """Train local models (non-federated) for comparison"""
        print("\n" + "="*60)
        print("TRAINING LOCAL BASELINE MODELS")
        print("="*60)
        
        local_results = []
        
        for client_id, (X_client, y_client) in enumerate(self.client_data):
            print(f"\nTraining local model for client {client_id + 1}...")
            
            # Create and train local model
            local_model = FraudDetectionModel(input_dim=29)
            local_model.build_model()
            local_model.train(X_client, y_client, epochs=self.local_epochs * self.n_rounds, batch_size=self.batch_size, verbose=0)
            
            # Evaluate on global test set
            metrics = local_model.evaluate(self.test_data[0], self.test_data[1])
            local_results.append(metrics)
            
            print(f"Client {client_id + 1} - AUC: {metrics['auc']:.4f}, F1: {metrics['f1_score']:.4f}")
        
        # Average metrics
        avg_metrics = {
            'accuracy': np.mean([m['accuracy'] for m in local_results]),
            'auc': np.mean([m['auc'] for m in local_results]),
            'precision': np.mean([m['precision'] for m in local_results]),
            'recall': np.mean([m['recall'] for m in local_results]),
            'f1_score': np.mean([m['f1_score'] for m in local_results])
        }
        
        print(f"\nAverage Local Model Performance:")
        print(f"AUC: {avg_metrics['auc']:.4f}, F1: {avg_metrics['f1_score']:.4f}, Accuracy: {avg_metrics['accuracy']:.4f}")
        
        return avg_metrics, local_results
    
    def run_privacy_attacks(self):
        """Run privacy attack simulations"""
        print("\n" + "="*60)
        print("RUNNING PRIVACY ATTACK SIMULATIONS")
        print("="*60)
        
        # Use first client's data for attack simulation
        X_train, y_train = self.client_data[0]
        X_test, y_test = self.test_data
        
        attack_simulator = PrivacyAttackSimulator(self.global_model.model)
        results = attack_simulator.run_all_attacks(X_train, X_test, y_train, y_test)
        
        return results
    
    def save_results(self, filepath='backend/results/performance.json'):
        """Save training results to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Get final metrics
        final_metrics = self.history['global_metrics'][-1] if self.history['global_metrics'] else {}
        
        # Train local baseline for comparison
        local_metrics, _ = self.train_local_baseline()
        
        # Run privacy attacks
        attack_results = self.run_privacy_attacks()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'n_clients': self.n_clients,
                'n_rounds': self.n_rounds,
                'local_epochs': self.local_epochs,
                'batch_size': self.batch_size,
                'use_dp': self.use_dp,
                'use_secure_agg': self.use_secure_agg
            },
            'federated_model': final_metrics,
            'local_baseline': local_metrics,
            'privacy_metrics': self.history.get('privacy_metrics', {}),
            'privacy_attacks': attack_results,
            'communication_cost_mb': float(np.mean(self.history['communication_costs'])) if self.history['communication_costs'] else 0,
            'training_history': {
                'rounds': self.history['rounds'],
                'metrics': self.history['global_metrics']
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {filepath}")
        
        return results
    
    def get_model(self):
        """Get the trained global model"""
        return self.global_model


if __name__ == "__main__":
    # Test federated training
    trainer = FederatedTrainer(
        n_clients=5,
        n_rounds=5,
        local_epochs=3,
        use_dp=True,
        use_secure_agg=True
    )
    
    trainer.load_data()
    trainer.train()
    results = trainer.save_results()
    
    print("\nFinal Results:")
    print(json.dumps(results, indent=2))
