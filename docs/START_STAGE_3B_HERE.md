# Start Stage 3B Here

Welcome to Stage 3B: Daphnet FOG Preprocessing.

## What's Available
This module provides a robust signal processing pipeline to convert raw interim CSV files into mathematically robust, normalized `.npy` tensors for model training.

## How to Run Preprocessing
Ensure you have run the Stage 3A import tools first so that `data/interim/daphnet/*.csv` exists. Then:

```powershell
# Activate your environment
.\venv\Scripts\activate

# Run the complete pipeline
python tools/run_fog_preprocessing.py
```

This will create:
- `X_train.npy`, `y_train.npy`
- `X_val.npy`, `y_val.npy`
- `X_test.npy`, `y_test.npy`
- `scaler.json`
- `window_metadata.csv`
- `split_manifest.json`
inside the `data/processed/daphnet/` directory.

## How to Run Visual QA
After generating the processed `.npy` files, you can plot sample windows to visually verify the signal structure:

```powershell
python tools/qa_plot_windows.py
```

This will save `fog_window_sample.png` and `no_fog_window_sample.png` in `data/qa/`.

## Next Steps
Read the `docs/FOG_SPLIT_REPORT.md` to understand the class weights before you begin Stage 3C (Model Training).
