# Stage 3B.1 Final Report

**Date:** 2026-07-10

## Execution Summary
Stage 3B.1 (Deployment-Aligned Filtering Variants) is strictly complete. We successfully extended the Daphnet preprocessing pipeline to output three mathematically distinct variants without modifying the underlying SQLite schema, transmission pipelines, or Stage 3B legacy outputs.

## Verified Inputs and Variables
- **Input:** `data/interim/daphnet/*.csv` (Remains untouched)
- **Shared Variables (Preserved across all modes):**
  - Units: milli-g → m/s²
  - Rate: 64 Hz → 50 Hz
  - Window: 2.0s (100 samples)
  - Stride: 50% overlap (50 samples)
  - Label Threshold: 0.5 (Fractional)
  - Subject Split: Train (S01, S03, S04, S05, S08, S09), Val (S06, S07), Test (S02, S10)
  - Leakage Policy: Windowing and filtering reset per-recording. No leakage.

## Filter Variants Implemented
1. **`none`**: No software filtering.
2. **`offline_zero_phase`**: `scipy.signal.filtfilt` (Butterworth, Order 4, Cutoff 20Hz).
3. **`causal`**: `scipy.signal.sosfilt` (Butterworth, Order 4, Cutoff 20Hz). Initialized with `scipy.signal.sosfilt_zi(sos) * data[0]` to minimize transient artifacts.

## Normalization (Scaler Strategy)
- A separate `StandardScaler` was instantiated, fitted on the TRAIN set, and applied to the Validation/Test sets individually for **each** of the three variants. The scaling parameters differ precisely per variant and are saved in `scaler.json` within each variant's directory.

## Output Structure & Class Balance
Outputs are explicitly isolated:
- `data/processed/daphnet/none/`
- `data/processed/daphnet/causal/`
- `data/processed/daphnet/offline_zero_phase/`

**Shapes & Balance (Identical for all three modes):**
- **Train:** 10,570 windows `(10570, 100, 3)` (1,339 FOG | 9,231 NO_FOG)
- **Val:** 3,596 windows `(3596, 100, 3)` (215 FOG | 3,381 NO_FOG)
- **Test:** 3,642 windows `(3642, 100, 3)` (181 FOG | 3,461 NO_FOG)
- **Recommended Train Weights:** 0: 1.0, 1: 6.89

## Tests & QA
- **Tests Added:** Parameterized `test_preprocessing_pipeline_modes` to run for all three modes, and `test_filtering_differences` to mathematically assert `none != causal != offline_zero_phase`.
- **Final Test Run:** 91 tests passed successfully (0 failures, 0 errors).
- **QA Tool:** `tools/qa_compare_filters.py` plots 3 variants stacked together.

## Blockers and Risks
- **No Blockers.** The pipeline executed successfully.
- **Note:** We do not claim `causal` is strictly "better" for ML accuracy—only that it aligns with the ESP32 deployment constraints. We will evaluate accuracy during Stage 3C.

## Stage 3C Readiness
**The FOG dataset variants are 100% ready for Stage 3C (Model Training).**
