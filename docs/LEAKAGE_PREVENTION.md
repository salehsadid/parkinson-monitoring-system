# Leakage Prevention Protocol

To ensure robust machine learning models for Tremor and FOG detection, strict data leakage prevention rules must be adhered to in Stage 3B.

## 1. Subject-Wise Splitting
- **Rule:** Data from the same human subject MUST NOT appear in both the training set and the validation/test set.
- **Why:** Models can easily learn an individual's specific gait or movement pattern rather than the generalized pathology (FOG/Tremor).
- **Implementation:**
  - Daphnet: Split based on `subject_id` (e.g., Train: S01-S07, Val: S08-S09, Test: S10).
  - PADS: Split based on `participant_id`.

## 2. Overlapping-Window Leakage
- **Rule:** If generating sliding windows with overlap (e.g., 50% overlap), the train/test split must occur *before* windowing, or strictly based on subject boundaries.
- **Why:** Adjacent overlapping windows share 50% of the exact same data points. If one falls in 'train' and the other in 'test', the test set is compromised.

## 3. Normalization Leakage
- **Rule:** Fit scalers (e.g., `StandardScaler`) **only** on the training set, then apply the fitted scaler to the validation and test sets.
- **Why:** Using global mean/variance across the entire dataset exposes the test set distribution to the training process.

## 4. Metadata Leakage
- **Rule:** Do not use patient metadata (age, height, weight) in models unless you have explicitly evaluated the risk of the model mapping "older/heavier" to "Parkinson's" due to small dataset biases.
