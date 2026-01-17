import torch
import torch.nn as nn
import logging
from pathlib import Path

logger = logging.getLogger("pothole-parent")

class PotholeSeverityModel(nn.Module):
    """
    Trained severity prediction model for potholes.
    Input: 5 features (depth, spread, emotion, location, upvote)
    Output: 1 severity score (0-100)
    """
    def __init__(self, input_size=5, hidden_sizes=[16, 8], output_size=1):
        super(PotholeSeverityModel, self).__init__()
        
        layers = []
        prev_size = input_size
        
        # Hidden layers with ReLU activation
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            prev_size = hidden_size
        
        # Output layer
        layers.append(nn.Linear(prev_size, output_size))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class PotholeModelLoader:
    """Singleton pattern for model loading"""
    _instance = None
    _model = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PotholeModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, model_path: str):
        """Load the trained model once at startup"""
        if self._model is not None:
            logger.info("Model already loaded")
            return
        
        # Determine device
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self._device}")
        
        # Initialize model architecture
        self._model = PotholeSeverityModel(
            input_size=5,
            hidden_sizes=[16, 8],
            output_size=1
        )
        
        # Load trained weights
        model_path = Path(model_path)
        if not model_path.exists():
            logger.warning(f"Model file not found: {model_path}. Using untrained model.")
        else:
            state_dict = torch.load(model_path, map_location=self._device)
            self._model.load_state_dict(state_dict)
            logger.info(f"Model loaded successfully from {model_path}")
        
        self._model.to(self._device)
        self._model.eval()  # Set to evaluation mode
    
    def get_model(self):
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._model, self._device


# Global singleton instance
pothole_model_loader = PotholeModelLoader()
