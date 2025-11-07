"""
FastAPI endpoints for federated learning system
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.trainer import FederatedTrainer
from app.utils import training_status, format_metrics, calculate_improvement, load_json

router = APIRouter()

# Global trainer instance
trainer: Optional[FederatedTrainer] = None
training_results = None

class TrainingConfig(BaseModel):
    n_clients: int = 5
    n_rounds: int = 10
    local_epochs: int = 5
    batch_size: int = 32
    use_dp: bool = True
    use_secure_agg: bool = True

class PredictionRequest(BaseModel):
    features: List[float]

class PredictionResponse(BaseModel):
    fraud_probability: float
    is_fraud: bool
    confidence: float

@router.post("/train")
async def train_model(config: TrainingConfig):
    """
    Start federated training
    """
    global trainer, training_results
    
    try:
        # Check if already training
        if training_status.status == "training":
            raise HTTPException(status_code=400, detail="Training already in progress")
        
        # Initialize trainer
        print(f"Initializing federated trainer with config: {config.dict()}")
        trainer = FederatedTrainer(
            n_clients=config.n_clients,
            n_rounds=config.n_rounds,
            local_epochs=config.local_epochs,
            batch_size=config.batch_size,
            use_dp=config.use_dp,
            use_secure_agg=config.use_secure_agg
        )
        
        # Update status
        training_status.start_training(config.n_rounds)
        
        # Load data
        trainer.load_data()
        
        # Train
        history = trainer.train()
        
        # Save results
        training_results = trainer.save_results()
        
        # Update status
        training_status.complete()
        
        return {
            "status": "success",
            "message": "Training completed successfully",
            "results": training_results
        }
        
    except Exception as e:
        training_status.error(str(e))
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.get("/metrics")
async def get_metrics():
    """
    Get performance metrics
    """
    global training_results
    
    if training_results is None:
        # Try to load from file
        training_results = load_json('backend/results/performance.json')
    
    if training_results is None:
        raise HTTPException(status_code=404, detail="No training results available. Please train the model first.")
    
    # Format response
    federated = training_results.get('federated_model', {})
    local = training_results.get('local_baseline', {})
    privacy = training_results.get('privacy_metrics', {})
    attacks = training_results.get('privacy_attacks', {})
    
    return {
        "federated_model": format_metrics(federated),
        "local_baseline": format_metrics(local),
        "improvement": {
            "auc": calculate_improvement(federated.get('auc', 0), local.get('auc', 0)),
            "f1_score": calculate_improvement(federated.get('f1_score', 0), local.get('f1_score', 0)),
            "accuracy": calculate_improvement(federated.get('accuracy', 0), local.get('accuracy', 0))
        },
        "privacy_metrics": privacy,
        "privacy_attacks": attacks,
        "communication_cost_mb": training_results.get('communication_cost_mb', 0)
    }

@router.post("/predict")
async def predict_fraud(request: PredictionRequest):
    """
    Predict fraud for a transaction
    """
    global trainer
    
    if trainer is None or trainer.global_model is None:
        raise HTTPException(status_code=400, detail="Model not trained yet. Please train the model first.")
    
    try:
        # Convert features to numpy array
        features = np.array(request.features).reshape(1, -1)
        
        # Validate input shape
        if features.shape[1] != 29:
            raise HTTPException(status_code=400, detail=f"Expected 29 features, got {features.shape[1]}")
        
        # Make prediction
        prediction = trainer.global_model.predict(features)[0][0]
        
        # Determine fraud
        is_fraud = bool(prediction > 0.5)
        confidence = float(abs(prediction - 0.5) * 2)  # Scale to 0-1
        
        return PredictionResponse(
            fraud_probability=float(prediction),
            is_fraud=is_fraud,
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/attack-test")
async def run_attack_test():
    """
    Run privacy attack simulations
    """
    global trainer, training_results
    
    if trainer is None:
        raise HTTPException(status_code=400, detail="Model not trained yet. Please train the model first.")
    
    try:
        # Run attacks
        attack_results = trainer.run_privacy_attacks()
        
        return {
            "status": "success",
            "results": attack_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attack test failed: {str(e)}")

@router.get("/status")
async def get_status():
    """
    Get current training status
    """
    global trainer
    
    status_dict = training_status.to_dict()
    
    # Add model info if available
    if trainer is not None:
        status_dict["model_info"] = {
            "n_clients": trainer.n_clients,
            "n_rounds": trainer.n_rounds,
            "use_dp": trainer.use_dp,
            "use_secure_agg": trainer.use_secure_agg
        }
        
        if trainer.client_data is not None:
            status_dict["data_info"] = {
                "n_clients": len(trainer.client_data),
                "test_samples": len(trainer.test_data[1]) if trainer.test_data else 0,
                "client_samples": [len(y) for _, y in trainer.client_data]
            }
    
    return status_dict

@router.get("/history")
async def get_training_history():
    """
    Get training history
    """
    global training_results
    
    if training_results is None:
        training_results = load_json('backend/results/performance.json')
    
    if training_results is None:
        raise HTTPException(status_code=404, detail="No training history available")
    
    history = training_results.get('training_history', {})
    
    return {
        "rounds": history.get('rounds', []),
        "metrics": history.get('metrics', [])
    }

@router.get("/clients")
async def get_client_info():
    """
    Get information about federated clients
    """
    global trainer
    
    if trainer is None or trainer.client_data is None:
        raise HTTPException(status_code=404, detail="No client data available")
    
    clients_info = []
    for i, (X, y) in enumerate(trainer.client_data):
        fraud_count = int(np.sum(y))
        normal_count = len(y) - fraud_count
        
        clients_info.append({
            "client_id": i + 1,
            "total_samples": len(y),
            "fraud_samples": fraud_count,
            "normal_samples": normal_count,
            "fraud_ratio": float(fraud_count / len(y)) if len(y) > 0 else 0
        })
    
    return {
        "n_clients": len(clients_info),
        "clients": clients_info
    }

@router.delete("/reset")
async def reset_training():
    """
    Reset training state
    """
    global trainer, training_results
    
    trainer = None
    training_results = None
    training_status.status = "idle"
    training_status.current_round = 0
    training_status.total_rounds = 0
    training_status.message = ""
    
    return {
        "status": "success",
        "message": "Training state reset"
    }
