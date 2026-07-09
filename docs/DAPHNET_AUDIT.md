# Daphnet Dataset Audit

**Audit Date:** 2026-07-09
**Dataset Location:** `data/raw/daphnet`

## Dataset Structure
- **Total Files:** 17 recordings (e.g., `S01R01.txt`)
- **Total Subjects:** 10 (S01 to S10)
- **Total Rows:** 1,917,887 (at 64Hz, this is ~8.3 hours of continuous data)
- **Malformed Rows:** 0
- **Missing Values:** 0

## Columns & Units
The dataset contains 11 columns in each text file. Based on the official documentation:
1. **Time:** ms
2. **Ankle_X, Ankle_Y, Ankle_Z:** milli-g
3. **Thigh_X, Thigh_Y, Thigh_Z:** milli-g
4. **Trunk_X, Trunk_Y, Trunk_Z:** milli-g
5. **Annotation:** Class label

*Note: The Daphnet adapter explicitly discards the Thigh and Trunk channels to align with our ankle-only FOG detection goal.*

## Annotation Balance
The `Annotation` column contains three values:
- **0 (Outside Experiment):** 777,052 rows (excluded from training)
- **1 (No Freeze):** 1,030,050 rows
- **2 (Freeze):** 110,785 rows

### Class Imbalance
Excluding class 0, the active dataset has 1,140,835 rows.
- **Negative Class (FOG = 0):** 90.3%
- **Positive Class (FOG = 1):** 9.7%

This severe class imbalance will require handling during Stage 3B (e.g., oversampling, class weighting, or custom loss functions).

## Conclusion
The Daphnet dataset is structurally sound and directly compatible with our FOG detection requirements. It can proceed to Stage 3B.
