#!/usr/bin/env python3
"""
System validation script
Tests all components before running the full application
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow {tf.__version__}")
    except ImportError as e:
        print(f"✗ TensorFlow import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✓ Pandas {pd.__version__}")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        from sklearn import __version__ as sklearn_version
        print(f"✓ Scikit-learn {sklearn_version}")
    except ImportError as e:
        print(f"✗ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_data_generation():
    """Test synthetic data generation"""
    print("\nTesting data generation...")
    
    try:
        from data.synthetic_generator import SyntheticFraudDataGenerator
        
        generator = SyntheticFraudDataGenerator(n_samples=1000, fraud_ratio=0.02)
        data = generator.generate()
        
        assert len(data) == 1000, "Data size mismatch"
        assert 'Class' in data.columns, "Missing Class column"
        assert data['Class'].sum() > 0, "No fraud samples generated"
        
        print(f"✓ Generated {len(data)} samples with {data['Class'].sum()} fraudulent")
        return True
    except Exception as e:
        print(f"✗ Data generation failed: {e}")
        return False

def test_model_creation():
    """Test model architecture"""
    print("\nTesting model creation...")
    
    try:
        from models.fraud_model import FraudDetectionModel
        
        model_builder = FraudDetectionModel(input_dim=29)
        model = model_builder.build_model()
        
        assert model is not None, "Model is None"
        assert len(model.layers) > 0, "Model has no layers"
        
        print(f"✓ Model created with {len(model.layers)} layers")
        return True
    except Exception as e:
        print(f"✗ Model creation failed: {e}")
        return False

def test_federated_data_loading():
    """Test federated data partitioning"""
    print("\nTesting federated data loading...")
    
    try:
        from data.load_data import FederatedDataLoader
        
        loader = FederatedDataLoader(n_clients=3)
        client_data, test_data = loader.create_federated_data()
        
        assert len(client_data) == 3, "Wrong number of clients"
        assert test_data is not None, "Test data is None"
        
        print(f"✓ Data partitioned into {len(client_data)} clients")
        for i, (X, y) in enumerate(client_data):
            print(f"  Client {i+1}: {len(y)} samples")
        
        return True
    except Exception as e:
        print(f"✗ Federated data loading failed: {e}")
        return False

def test_privacy_manager():
    """Test differential privacy manager"""
    print("\nTesting privacy manager...")
    
    try:
        from app.privacy import DifferentialPrivacyManager
        
        dp_manager = DifferentialPrivacyManager(
            l2_norm_clip=1.0,
            noise_multiplier=1.1,
            num_microbatches=32
        )
        
        epsilon, delta = dp_manager.compute_privacy_budget(
            n_samples=10000,
            batch_size=32,
            epochs=5
        )
        
        assert epsilon > 0, "Invalid epsilon"
        assert delta > 0, "Invalid delta"
        
        print(f"✓ Privacy budget computed: ε={epsilon:.2f}, δ={delta:.2e}")
        return True
    except Exception as e:
        print(f"✗ Privacy manager failed: {e}")
        return False

def test_secure_aggregation():
    """Test secure aggregation"""
    print("\nTesting secure aggregation...")
    
    try:
        import numpy as np
        from models.secure_aggregation import SecureAggregator
        
        n_clients = 3
        aggregator = SecureAggregator(n_clients)
        
        # Create dummy weights
        dummy_weights = [
            [np.random.randn(10, 5), np.random.randn(5)]
            for _ in range(n_clients)
        ]
        
        aggregated = aggregator.aggregate_with_secure_protocol(dummy_weights)
        
        assert len(aggregated) == 2, "Wrong number of layers"
        
        print(f"✓ Secure aggregation successful")
        return True
    except Exception as e:
        print(f"✗ Secure aggregation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("FEDERATED FRAUD DETECTION - SYSTEM VALIDATION")
    print("="*60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Data Generation", test_data_generation),
        ("Model Creation", test_model_creation),
        ("Federated Data Loading", test_federated_data_loading),
        ("Privacy Manager", test_privacy_manager),
        ("Secure Aggregation", test_secure_aggregation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to run.")
        print("\nNext steps:")
        print("1. Start backend: ./start_backend.sh")
        print("2. Start frontend: ./start_frontend.sh")
        print("3. Open http://localhost:5173")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
