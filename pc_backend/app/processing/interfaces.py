"""
Processing interfaces for hand and shoe IMU data.

This module defines abstract interfaces for signal processing
pipelines that will be implemented in future stages.

Stage 1 Purpose:
- Define clean interfaces for future implementation
- Document expected inputs and outputs
- Provide placeholder methods that raise NotImplementedError

Future Implementation:
- Real signal preprocessing (filtering, normalization)
- Feature extraction (time-domain, frequency-domain)
- Windowing for ML inference
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import numpy as np


class HandProcessorInterface(ABC):
    """
    Abstract interface for hand IMU data processing.

    This interface defines the contract for processing hand sensor
    data for tremor analysis. Future implementations will include:
    - Signal preprocessing (filtering, detrending)
    - Feature extraction (RMS, frequency analysis)
    - Windowing for ML inference
    """

    @abstractmethod
    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """
        Preprocess raw hand IMU data.

        Args:
            data: Raw IMU data array with shape (N, 6)
                  Columns: [ax, ay, az, gx, gy, gz]

        Returns:
            np.ndarray: Preprocessed data array

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Preprocessing not implemented in Stage 1")

    @abstractmethod
    def extract_features(self, window: np.ndarray) -> np.ndarray:
        """
        Extract features from a window of hand IMU data.

        Args:
            window: Windowed IMU data array with shape (W, 6)
                    where W is the window size

        Returns:
            np.ndarray: Feature vector

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Feature extraction not implemented in Stage 1")

    @abstractmethod
    def create_windows(
        self,
        data: np.ndarray,
        window_size: int,
        step_size: int,
    ) -> List[np.ndarray]:
        """
        Create overlapping windows from continuous data.

        Args:
            data: Continuous IMU data array with shape (N, 6)
            window_size: Number of samples per window
            step_size: Number of samples between windows

        Returns:
            List[np.ndarray]: List of windowed data arrays

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Windowing not implemented in Stage 1")


class ShoeProcessorInterface(ABC):
    """
    Abstract interface for shoe IMU data processing.

    This interface defines the contract for processing shoe sensor
    data for Freezing of Gait (FOG) detection. Future implementations
    will include:
    - Signal preprocessing (filtering, normalization)
    - Feature extraction (gait cadence, symmetry)
    - Windowing for ML inference
    """

    @abstractmethod
    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """
        Preprocess raw shoe IMU data.

        Args:
            data: Raw IMU data array with shape (N, 6)
                  Columns: [ax, ay, az, gx, gy, gz]

        Returns:
            np.ndarray: Preprocessed data array

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Preprocessing not implemented in Stage 1")

    @abstractmethod
    def extract_features(self, window: np.ndarray) -> np.ndarray:
        """
        Extract features from a window of shoe IMU data.

        Args:
            window: Windowed IMU data array with shape (W, 6)
                    where W is the window size

        Returns:
            np.ndarray: Feature vector

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Feature extraction not implemented in Stage 1")

    @abstractmethod
    def create_windows(
        self,
        data: np.ndarray,
        window_size: int,
        step_size: int,
    ) -> List[np.ndarray]:
        """
        Create overlapping windows from continuous data.

        Args:
            data: Continuous IMU data array with shape (N, 6)
            window_size: Number of samples per window
            step_size: Number of samples between windows

        Returns:
            List[np.ndarray]: List of windowed data arrays

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Windowing not implemented in Stage 1")


class SignalProcessor:
    """
    Concrete signal processor with basic implementations.

    This class provides basic signal processing utilities that can
    be used as building blocks for future processing pipelines.
    """

    @staticmethod
    def apply_lowpass_filter(
        data: np.ndarray,
        cutoff_freq: float,
        sampling_rate: int,
        order: int = 4,
    ) -> np.ndarray:
        """
        Apply a Butterworth low-pass filter.

        Args:
            data: Input signal array
            cutoff_freq: Cutoff frequency in Hz
            sampling_rate: Sampling rate in Hz
            order: Filter order

        Returns:
            np.ndarray: Filtered signal

        Raises:
            NotImplementedError: In Stage 1
        """
        raise NotImplementedError("Filtering not implemented in Stage 1")

    @staticmethod
    def compute_rms(data: np.ndarray) -> float:
        """
        Compute Root Mean Square of signal.

        Args:
            data: Input signal array

        Returns:
            float: RMS value
        """
        return np.sqrt(np.mean(data ** 2))

    @staticmethod
    def compute_peak_amplitude(data: np.ndarray) -> float:
        """
        Compute peak amplitude of signal.

        Args:
            data: Input signal array

        Returns:
            float: Peak amplitude
        """
        return np.max(np.abs(data))
