"""
Utility functions for the federated learning system
"""
import json
import os
import numpy as np
from datetime import datetime

class NumpyEncoder(json.JSONEncoder):
    """JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def save_json(data, filepath):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)

def load_json(filepath):
    """Load data from JSON file"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def format_metrics(metrics):
    """Format metrics for display"""
    formatted = {}
    for key, value in metrics.items():
        if isinstance(value, (float, np.floating)):
            formatted[key] = round(float(value), 4)
        else:
            formatted[key] = value
    return formatted

def calculate_improvement(federated_metric, local_metric):
    """Calculate percentage improvement"""
    if local_metric == 0:
        return 0
    improvement = ((federated_metric - local_metric) / local_metric) * 100
    return round(improvement, 2)

def get_timestamp():
    """Get current timestamp"""
    return datetime.now().isoformat()

def ensure_dir(directory):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

class TrainingStatus:
    """Track training status"""
    def __init__(self):
        self.status = "idle"  # idle, training, completed, error
        self.current_round = 0
        self.total_rounds = 0
        self.message = ""
        self.start_time = None
        self.end_time = None
    
    def start_training(self, total_rounds):
        self.status = "training"
        self.current_round = 0
        self.total_rounds = total_rounds
        self.start_time = get_timestamp()
        self.message = "Training started"
    
    def update_round(self, round_num):
        self.current_round = round_num
        self.message = f"Training round {round_num}/{self.total_rounds}"
    
    def complete(self):
        self.status = "completed"
        self.end_time = get_timestamp()
        self.message = "Training completed successfully"
    
    def error(self, error_msg):
        self.status = "error"
        self.end_time = get_timestamp()
        self.message = f"Error: {error_msg}"
    
    def to_dict(self):
        return {
            "status": self.status,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "message": self.message,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "progress_percentage": (self.current_round / self.total_rounds * 100) if self.total_rounds > 0 else 0
        }

# Global training status
training_status = TrainingStatus()
