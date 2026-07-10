# FOG Window Label Policy

## The Problem
FOG annotations are provided at a per-sample level. When windowing data (e.g., 2.0 seconds = 100 samples), a window might contain a transition from Normal Gait to FOG. How do we label the entire window?

## The Threshold Policy
We implement a Fractional Threshold Policy, configurable in `ml/preprocessing/config.py`.

1. **Calculate FOG Fraction:** For every window, we calculate the sum of FOG samples divided by the total number of samples (100).
   `fog_fraction = sum(labels) / 100`
2. **Apply Threshold:**
   If `fog_fraction >= 0.5`: The final window label is `1` (FOG).
   If `fog_fraction < 0.5`: The final window label is `0` (NO FOG).

## Transparency
The exact `fog_fraction` for every single window is saved in `data/processed/daphnet/window_metadata.csv`. This allows us to re-label data in the future without re-running the entire signal processing pipeline, or train models that predict the exact fraction.
