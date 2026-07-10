# Stage 3B Final Report

**Date:** 2026-07-09

## Execution Summary
Stage 3B (Daphnet FOG Preprocessing Pipeline) is strictly complete. We successfully implemented a signal processing pipeline that safely converts interim CSV files into ML-ready tensor arrays.

## Verified Inputs and Physics
- **Actual Input Schema:** `dataset_name`, `dataset_version`, `subject_id`, `recording_id`, `source_file`, `timestamp`, `ankle_ax`, `ankle_ay`, `ankle_az`, `raw_annotation`, `fog_label`
- **Source Units:** milli-g -> **Target Units:** m/s²
- **Source Rate:** 64 Hz -> **Target Rate:** 50 Hz

## Configuration Parameters
- **Filter:** 4th-order low-pass Butterworth, Cutoff = 20 Hz, zero-phase.
- **Window:** 2.0 seconds (100 samples), Stride = 50 samples (50% overlap).
- **Labeling:** >= 50% FOG samples inside a window yields a positive label.

## Subject Split & Class Imbalance
We implemented an explicit subject split to guarantee positive FOG examples in all datasets, as 4 out of 10 subjects had zero FOG events.
- **Train (S01, S03, S04, S05, S08, S09):** 10,570 windows (1,339 FOG, 9,231 NO_FOG)
- **Val (S06, S07):** 3,596 windows (215 FOG, 3,381 NO_FOG)
- **Test (S02, S10):** 3,642 windows (181 FOG, 3,461 NO_FOG)
- **Scaler Strategy:** `StandardScaler` fitted explicitly on the Train dataset only, applied to Val/Test.
- **Recommended Class Weights (Stage 3C):** Class 0 (1.0), Class 1 (~6.89).

## Artifacts Produced
- `data/processed/daphnet/X_train.npy` ... `y_test.npy` (Shapes: `(N, 100, 3)`)
- `data/processed/daphnet/scaler.json`
- `data/processed/daphnet/window_metadata.csv`
- `data/qa/fog_window_sample.png`
- `data/qa/no_fog_window_sample.png`

## Blockers and Risks
- **Zero-Phase Filtering Risk:** We used `scipy.signal.filtfilt` (zero-phase filtering). This looks forward in time. When deploying to the ESP32 (Stage 4), zero-phase is mathematically impossible in real-time. The ML model might learn features that don't exist in live data. We may need to retrain without filtering or use a causal filter during Stage 3C.
- **No Blockers:** The pipeline successfully completed.

## Stage 3C Readiness
**The FOG dataset is 100% ready for Stage 3C (Model Training).**
