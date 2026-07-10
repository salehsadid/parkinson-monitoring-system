# Stage 3B: Daphnet FOG Preprocessing Pipeline Plan

*(Approved and Executed Plan)*

## Goal
Implement a reproducible, robust preprocessing pipeline for the Daphnet Freezing of Gait dataset, converting the interim canonical CSV data into ML-ready `.npy` windowed tensors suitable for Stage 3C model training. The pipeline strictly avoids subject/recording leakage and adheres to the physical runtime constraints.

## Proposed Architecture
The architecture is modularly implemented in `ml/preprocessing/`.

### 1. `ml/preprocessing/config.py`
A Pydantic-based configuration model allowing explicit control over all pipeline parameters. It enforces the following explicit subject split to guarantee FOG representation:
- Train: S01, S03, S04, S05, S08, S09
- Val: S06, S07
- Test: S02, S10

### 2. `ml/preprocessing/pipeline.py`
The orchestrator class `FOGPreprocessingPipeline` executes:
1. Input Validation (Checks schemas)
2. Unit Conversion (milli-g to m/s²)
3. Resampling (64 Hz → 50 Hz via interpolation)
4. Filtering (Zero-phase Butterworth low-pass)
5. Windowing & Labeling (2.0s windows, 50% overlap)
6. Subject-wise Splitting
7. Normalization (StandardScaler fit on Train only)
8. Output Generation (Numpy Arrays)

### 3. CLI Tools & QA
- `tools/run_fog_preprocessing.py`: Executes the full pipeline.
- `tools/qa_plot_windows.py`: Plots visual QA samples.

### 4. Tests
- `tests/test_preprocessing.py`: Verifies zero leakage, fractional thresholds, and exact tensor shapes.
