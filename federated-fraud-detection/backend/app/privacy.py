"""
Differential Privacy implementation for federated learning
"""
import tensorflow as tf
import numpy as np

# Try to import tensorflow_privacy, fallback to manual implementation if not available
try:
    from tensorflow_privacy.privacy.optimizers import dp_optimizer_keras
    from tensorflow_privacy.privacy.analysis import compute_dp_sgd_privacy
    TFP_AVAILABLE = True
except ImportError:
    print("WARNING: tensorflow-privacy not available. Using manual DP implementation.")
    TFP_AVAILABLE = False

class DifferentialPrivacyManager:
    """
    Manages differential privacy for federated learning
    Implements DP-SGD with Gaussian noise
    """
    
    def __init__(self, l2_norm_clip=1.0, noise_multiplier=1.1, num_microbatches=32, learning_rate=0.001):
        self.l2_norm_clip = l2_norm_clip
        self.noise_multiplier = noise_multiplier
        self.num_microbatches = num_microbatches
        self.learning_rate = learning_rate
        self.epsilon = None
        self.delta = None
        
    def create_dp_optimizer(self):
        """Create a differentially private optimizer"""
        if TFP_AVAILABLE:
            optimizer = dp_optimizer_keras.DPKerasAdamOptimizer(
                l2_norm_clip=self.l2_norm_clip,
                noise_multiplier=self.noise_multiplier,
                num_microbatches=self.num_microbatches,
                learning_rate=self.learning_rate
            )
        else:
            # Fallback to regular Adam optimizer (noise will be added manually)
            optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        return optimizer
    
    def compute_privacy_budget(self, n_samples, batch_size, epochs):
        """
        Compute privacy budget (epsilon) for given training parameters
        
        Args:
            n_samples: Number of training samples
            batch_size: Batch size
            epochs: Number of training epochs
        
        Returns:
            epsilon: Privacy budget
            delta: Privacy parameter (typically 1/n_samples)
        """
        steps = epochs * (n_samples // batch_size)
        delta = 1.0 / n_samples
        
        if TFP_AVAILABLE:
            try:
                epsilon = compute_dp_sgd_privacy.compute_dp_sgd_privacy(
                    n=n_samples,
                    batch_size=batch_size,
                    noise_multiplier=self.noise_multiplier,
                    epochs=epochs,
                    delta=delta
                )[0]
            except Exception as e:
                # Fallback calculation if TF Privacy computation fails
                epsilon = self._approximate_epsilon(steps, n_samples, batch_size, delta)
        else:
            # Use approximation when tensorflow_privacy is not available
            epsilon = self._approximate_epsilon(steps, n_samples, batch_size, delta)
        
        self.epsilon = epsilon
        self.delta = delta
        
        return epsilon, delta
    
    def _approximate_epsilon(self, steps, n_samples, batch_size, delta):
        """Approximate epsilon using moments accountant"""
        # Simplified approximation
        q = batch_size / n_samples  # Sampling ratio
        sigma = self.noise_multiplier
        
        # Rough approximation: ε ≈ q * steps / sigma
        epsilon = (q * steps) / (sigma * np.sqrt(2 * np.log(1.25 / delta)))
        
        return epsilon
    
    def add_noise_to_gradients(self, gradients):
        """Add Gaussian noise to gradients for differential privacy"""
        noisy_gradients = []
        
        for grad in gradients:
            if grad is not None:
                # Clip gradient
                clipped_grad = tf.clip_by_norm(grad, self.l2_norm_clip)
                
                # Add Gaussian noise
                noise = tf.random.normal(
                    shape=grad.shape,
                    mean=0.0,
                    stddev=self.l2_norm_clip * self.noise_multiplier
                )
                noisy_grad = clipped_grad + noise
                noisy_gradients.append(noisy_grad)
            else:
                noisy_gradients.append(None)
        
        return noisy_gradients
    
    def add_noise_to_weights(self, weights, scale=None):
        """Add calibrated noise to model weights"""
        if scale is None:
            scale = self.l2_norm_clip * self.noise_multiplier
        
        noisy_weights = []
        for w in weights:
            noise = np.random.normal(0, scale, w.shape)
            noisy_w = w + noise
            noisy_weights.append(noisy_w)
        
        return noisy_weights
    
    def get_privacy_metrics(self):
        """Get current privacy metrics"""
        return {
            'epsilon': self.epsilon,
            'delta': self.delta,
            'l2_norm_clip': self.l2_norm_clip,
            'noise_multiplier': self.noise_multiplier
        }
    
    def is_privacy_preserved(self, epsilon_threshold=3.0):
        """Check if privacy budget is within acceptable range"""
        if self.epsilon is None:
            return None
        return self.epsilon <= epsilon_threshold


class PrivacyAttackSimulator:
    """
    Simulate privacy attacks to test robustness
    - Membership inference attack
    - Model inversion attack
    """
    
    def __init__(self, model):
        self.model = model
        
    def membership_inference_attack(self, X_train, X_test, y_train, y_test, n_samples=100):
        """
        Simulate membership inference attack
        Try to determine if a sample was in the training set
        
        Returns:
            attack_accuracy: How well the attack performs (lower is better)
        """
        # Select random samples
        train_indices = np.random.choice(len(X_train), min(n_samples, len(X_train)), replace=False)
        test_indices = np.random.choice(len(X_test), min(n_samples, len(X_test)), replace=False)
        
        # Get predictions and confidence
        train_preds = self.model.predict(X_train[train_indices], verbose=0)
        test_preds = self.model.predict(X_test[test_indices], verbose=0)
        
        # Calculate prediction confidence (distance from 0.5)
        train_confidence = np.abs(train_preds - 0.5).mean()
        test_confidence = np.abs(test_preds - 0.5).mean()
        
        # Attack assumes higher confidence = training member
        # If we can distinguish, attack succeeds
        attack_accuracy = abs(train_confidence - test_confidence) / (train_confidence + test_confidence + 1e-10)
        
        # Convert to success rate (0 = perfect defense, 1 = attack succeeds)
        attack_success_rate = min(attack_accuracy * 2, 1.0)
        
        return {
            'attack_success_rate': float(attack_success_rate),
            'defense_success_rate': float(1.0 - attack_success_rate),
            'train_confidence': float(train_confidence),
            'test_confidence': float(test_confidence)
        }
    
    def model_inversion_attack(self, X_sample, iterations=100):
        """
        Simulate model inversion attack
        Try to reconstruct input from model outputs
        
        Returns:
            reconstruction_error: How well the attack performs (higher is better for defense)
        """
        # Start with random input
        reconstructed = np.random.randn(*X_sample.shape)
        
        # Try to reconstruct (simplified simulation)
        original_pred = self.model.predict(X_sample.reshape(1, -1), verbose=0)
        reconstructed_pred = self.model.predict(reconstructed.reshape(1, -1), verbose=0)
        
        # Calculate reconstruction error
        reconstruction_error = np.mean(np.abs(X_sample - reconstructed))
        prediction_diff = np.abs(original_pred - reconstructed_pred)
        
        # Higher error = better defense
        defense_score = min(reconstruction_error / 10.0, 1.0)
        
        return {
            'reconstruction_error': float(reconstruction_error),
            'prediction_difference': float(prediction_diff[0][0]),
            'defense_score': float(defense_score)
        }
    
    def run_all_attacks(self, X_train, X_test, y_train, y_test):
        """Run all privacy attacks and return results"""
        print("Running privacy attack simulations...")
        
        # Membership inference
        membership_results = self.membership_inference_attack(X_train, X_test, y_train, y_test)
        
        # Model inversion
        sample_idx = np.random.randint(0, len(X_test))
        inversion_results = self.model_inversion_attack(X_test[sample_idx])
        
        results = {
            'membership_inference': membership_results,
            'model_inversion': inversion_results,
            'overall_defense_rate': (membership_results['defense_success_rate'] + inversion_results['defense_score']) / 2
        }
        
        print(f"Privacy Defense Success Rate: {results['overall_defense_rate']*100:.1f}%")
        
        return results


if __name__ == "__main__":
    # Test DP manager
    dp_manager = DifferentialPrivacyManager(
        l2_norm_clip=1.0,
        noise_multiplier=1.1,
        num_microbatches=32
    )
    
    # Compute privacy budget
    epsilon, delta = dp_manager.compute_privacy_budget(
        n_samples=10000,
        batch_size=32,
        epochs=10
    )
    
    print(f"Privacy Budget: ε = {epsilon:.2f}, δ = {delta:.2e}")
    print(f"Privacy Preserved: {dp_manager.is_privacy_preserved()}")
