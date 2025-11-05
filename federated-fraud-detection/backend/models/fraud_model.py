"""
Fraud detection model architecture
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

class FraudDetectionModel:
    """Deep learning model for fraud detection"""
    
    def __init__(self, input_dim=29, learning_rate=0.001):
        self.input_dim = input_dim
        self.learning_rate = learning_rate
        self.model = None
        
    def build_model(self):
        """Build the fraud detection neural network"""
        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(self.input_dim,), name='dense_1'),
            layers.Dropout(0.3, name='dropout_1'),
            layers.Dense(32, activation='relu', name='dense_2'),
            layers.Dropout(0.2, name='dropout_2'),
            layers.Dense(16, activation='relu', name='dense_3'),
            layers.Dense(1, activation='sigmoid', name='output')
        ], name='fraud_detection_model')
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.AUC(name='auc'),
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall')
            ]
        )
        
        self.model = model
        return model
    
    def get_model(self):
        """Get or create model"""
        if self.model is None:
            self.build_model()
        return self.model
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=10, batch_size=32, verbose=1):
        """Train the model"""
        if self.model is None:
            self.build_model()
        
        # Handle class imbalance
        neg_count = np.sum(y_train == 0)
        pos_count = np.sum(y_train == 1)
        
        if pos_count > 0:
            weight_for_0 = (1 / neg_count) * (len(y_train) / 2.0)
            weight_for_1 = (1 / pos_count) * (len(y_train) / 2.0)
            class_weight = {0: weight_for_0, 1: weight_for_1}
        else:
            class_weight = None
        
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            class_weight=class_weight,
            verbose=verbose
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        results = self.model.evaluate(X_test, y_test, verbose=0)
        metrics = {
            'loss': results[0],
            'accuracy': results[1],
            'auc': results[2],
            'precision': results[3],
            'recall': results[4]
        }
        
        # Calculate F1 score
        if metrics['precision'] + metrics['recall'] > 0:
            metrics['f1_score'] = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall'])
        else:
            metrics['f1_score'] = 0.0
        
        return metrics
    
    def predict(self, X):
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)
    
    def get_weights(self):
        """Get model weights"""
        if self.model is None:
            raise ValueError("Model not built yet")
        return self.model.get_weights()
    
    def set_weights(self, weights):
        """Set model weights"""
        if self.model is None:
            self.build_model()
        self.model.set_weights(weights)
    
    def save(self, filepath):
        """Save model"""
        if self.model is None:
            raise ValueError("Model not built yet")
        self.model.save(filepath)
    
    def load(self, filepath):
        """Load model"""
        self.model = keras.models.load_model(filepath)
        return self.model


def create_model(input_dim=29):
    """Factory function to create a fraud detection model"""
    model_builder = FraudDetectionModel(input_dim=input_dim)
    return model_builder.build_model()


if __name__ == "__main__":
    # Test model creation
    model = FraudDetectionModel(input_dim=29)
    model.build_model()
    print("Model Summary:")
    model.model.summary()
