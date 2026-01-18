import torch
import torch.nn as nn
import logging
from pathlib import Path

logger = logging.getLogger("garbage-parent")

class GarbageSeverityModel(nn.Module):
    """
    Trained severity prediction model for garbage.
    Input: 5 features (volume, waste_type, emotion, location, upvote)
    Output: 1 severity score (0-100)
    """
    def __init__(self, input_size=5, hidden_sizes=[16, 8], output_size=1):
        super(GarbageSeverityModel, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, output_size))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class GarbageModelLoader:
    """Singleton pattern for model loading"""
    _instance = None
    _model = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GarbageModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, model_path: str):
        """Load the trained model once at startup"""
        if self._model is not None:
            logger.info("Model already loaded")
            return
        
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self._device}")
        
        self._model = GarbageSeverityModel(
            input_size=5,
            hidden_sizes=[16, 8],
            output_size=1
        )
        
        model_path = Path(model_path)
        if not model_path.exists():
            logger.warning(f"Model file not found: {model_path}. Using untrained model.")
        else:
            # Load with weights_only=False to allow older pickle files
            # Warning: Only do this with trusted local models!
            state_dict = torch.load(model_path, map_location=self._device, weights_only=False)
            self._model.load_state_dict(state_dict)
            logger.info(f"Model loaded successfully from {model_path}")
        
        self._model.to(self._device)
        self._model.eval()
    
    def get_model(self):
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._model, self._device


# Global singleton instance
garbage_model_loader = GarbageModelLoader()
