# FOG Preprocessing Architecture

## Overview
This document outlines the signal processing steps applied to the Daphnet FOG dataset to make it mathematically compatible with the ESP32 runtime.

## 1. Unit Conversion
- **Raw Data:** milli-g
- **Runtime:** m/s²
- **Process:** We explicitly multiply all `ankle_ax`, `ankle_ay`, and `ankle_az` values by `0.00980665`.

## 2. Resampling
- **Raw Rate:** 64 Hz
- **Runtime Rate:** 50 Hz
- **Process:** We use `scipy.interpolate.interp1d` to interpolate the continuous acceleration channels from 64Hz down to 50Hz based on timestamps. We use `kind='nearest'` interpolation on the `fog_label` to ensure labels remain strictly categorical (no fractions like 0.3 FOG).

## 3. Filtering
- **Design:** Zero-phase low-pass Butterworth filter.
- **Parameters:** Order 4, Cutoff 20.0 Hz.
- **Implementation:** `scipy.signal.filtfilt`.
- **Warning for Real-time:** Zero-phase filtering (`filtfilt`) looks ahead in time and cannot be used in a live ESP32 pipeline. During Stage 3C, we must either replicate a causal filter (`lfilter`) or train the model to be robust without filtering, relying instead on the hardware MPU6050 DLPF.

## 4. Normalization
- **Strategy:** `StandardScaler` (z-score normalization).
- **Leakage Prevention:** The mean and variance are calculated **exclusively on the training set**. The validation and test sets are scaled using these fixed parameters.
- **Output:** The parameters are saved transparently to `data/processed/daphnet/scaler.json` for later porting to the ESP32 C++ runtime.
