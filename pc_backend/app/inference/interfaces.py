"""
ML inference interfaces for tremor and FOG detection models.

This module defines abstract interfaces for machine learning models
that will be implemented in future stages.

Stage 1 Purpose:
- Define clean interfaces for model loading and prediction
- Document expected inputs and outputs
- Provide placeholder methods that raise NotImplementedError

Future Implementation:
- Trained scikit-learn models for tremor classification
- Trained scikit-learn models for FOG detection
- Model versioning and persistence
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class TremorModelInterface(ABC):
    """
    Abstract interface for tremor classification model.

    This interface defines the contract for ML models that classify
    tremor severity from hand IMU data. Future implementations will
    include trained scikit-learn models.

    Expected Input:
    - Feature vector extracted from hand IMU window
    - Shape: (n_features,) or (1, n_features) for batch

    Expected Output:
    - Predicted class (e.g., "no_tremor", "mild", "moderate", "severe")
    - Confidence score (0.0 to 1.0)
    """

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """
        Load a trained model from disk.

        Args:
            model_path: Path to saved model file

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Model loading not implemented in Stage 1")

    @abstractmethod
    def predict(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Predict tremor class and confidence.

        Args:
            features: Feature vector with shape (n_features,)

        Returns:
            Tuple[str, float]: (predicted_class, confidence)

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Prediction not implemented in Stage 1")

    @abstractmethod
    def predict_batch(self, features_batch: np.ndarray) -> List[Tuple[str, float]]:
        """
        Predict tremor class for a batch of samples.

        Args:
            features_batch: Batch of feature vectors with shape (n_samples, n_features)

        Returns:
            List[Tuple[str, float]]: List of (predicted_class, confidence)

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Batch prediction not implemented in Stage 1")

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dict with model metadata (version, type, features, etc.)

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Model info not implemented in Stage 1")


class FOGModelInterface(ABC):
    """
    Abstract interface for Freezing of Gait (FOG) detection model.

    This interface defines the contract for ML models that detect
    FOG events from shoe IMU data. Future implementations will
    include trained scikit-learn models.

    Expected Input:
    - Feature vector extracted from shoe IMU window
    - Shape: (n_features,) or (1, n_features) for batch

    Expected Output:
    - Boolean indicating FOG detection
    - Confidence score (0.0 to 1.0)
    """

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """
        Load a trained model from disk.

        Args:
            model_path: Path to saved model file

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Model loading not implemented in Stage 1")

    @abstractmethod
    def predict(self, features: np.ndarray) -> Tuple[bool, float]:
        """
        Predict FOG detection and confidence.

        Args:
            features: Feature vector with shape (n_features,)

        Returns:
            Tuple[bool, float]: (is_fog_detected, confidence)

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Prediction not implemented in Stage 1")

    @abstractmethod
    def predict_batch(self, features_batch: np.ndarray) -> List[Tuple[bool, float]]:
        """
        Predict FOG detection for a batch of samples.

        Args:
            features_batch: Batch of feature vectors with shape (n_samples, n_features)

        Returns:
            List[Tuple[bool, float]]: List of (is_fog_detected, confidence)

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Batch prediction not implemented in Stage 1")

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dict with model metadata (version, type, features, etc.)

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Model info not implemented in Stage 1")


class ModelManager:
    """
    Concrete model manager with basic implementations.

    This class provides model management utilities that can be
    extended for future model loading and inference.
    """

    def __init__(self):
        """Initialize model manager."""
        self._models: Dict[str, Any] = {}

    def register_model(self, name: str, model: Any) -> None:
        """
        Register a model with the manager.

        Args:
            name: Model name identifier
            model: Model object
        """
        self._models[name] = model

    def get_model(self, name: str) -> Optional[Any]:
        """
        Get a registered model by name.

        Args:
            name: Model name identifier

        Returns:
            Optional[Any]: Model object or None
        """
        return self._models.get(name)

    def list_models(self) -> List[str]:
        """
        List all registered model names.

        Returns:
            List[str]: List of model names
        """
        return list(self._models.keys())

    def remove_model(self, name: str) -> bool:
        """
        Remove a registered model.

        Args:
            name: Model name identifier

        Returns:
            bool: True if model was removed, False if not found
        """
        if name in self._models:
            del self._models[name]
            return True
        return False
