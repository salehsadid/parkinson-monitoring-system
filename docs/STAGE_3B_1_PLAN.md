# Stage 3B.1: Deployment-Aligned Filtering Variants Plan

*(Approved and Executed Plan)*

## Goal
Implement deployment-aligned filtering variants (`none` and `causal`) to the Daphnet FOG preprocessing pipeline. This ensures the ML models trained in Stage 3C do not inadvertently learn future-dependent signal artifacts from the legacy `filtfilt` zero-phase offline filter, aligning them with the real-time constraints of the ESP32 deployment.

## Architecture & Implementation

### 1. `ml/preprocessing/config.py`
- Replaced `apply_filter: bool` with `filter_mode: str`.
- Allowed values: `"none"`, `"causal"`, `"offline_zero_phase"`.
- Kept defaults for the split configuration exactly as they are currently to preserve the exact subset distribution.

### 2. `ml/preprocessing/pipeline.py`
Modified `Step 4: Filtering` to respect `filter_mode`:
- **`none`**: Bypassed filtering entirely.
- **`offline_zero_phase`**: Kept existing `signal.filtfilt(b, a, resampled_accel, axis=0)` implementation.
- **`causal`**: 
  - Designed a Second-Order Sections (SOS) Butterworth filter using `signal.butter(..., output='sos')`.
  - Processed using `signal.sosfilt(sos, resampled_accel, axis=0)`. This is strictly causal (only uses present and past samples).
  - Explicitly initialized state (`zi = signal.sosfilt_zi(sos) * data[0]`) to minimize startup transients, resetting per-recording to prevent leakage across boundaries.

Modified `Step 8: Save Outputs`:
- Ensured outputs are saved into `data/processed/daphnet/{filter_mode}/`.
- Preserved existing outputs by NOT deleting existing files.
- Serialized `preprocessing_config.json` and renamed `split_manifest.json` to `manifest.json`.

### 3. CLI Tools & QA
- **`tools/run_fog_preprocessing.py`**: Updated to loop through the `filter_mode`s and process each.
- **`tools/qa_compare_filters.py`**: Created a new tool that loads metadata, finds an identical window across variants, and plots the `none`, `causal`, and `offline_zero_phase` signals overlapping for visual comparison.

### 4. Tests
- **`tests/test_preprocessing.py`**:
  - Added parameterized testing for all three modes.
  - Validated that `none` does not alter the signal post-resampling.
  - Validated that the `causal` output differs from `offline_zero_phase` but maintains the same shape.
  - Asserted exact split constraints and categorical labels are preserved across all modes.
