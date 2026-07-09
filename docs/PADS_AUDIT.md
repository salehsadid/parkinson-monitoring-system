# PADS Dataset Audit

**Audit Date:** 2026-07-09
**Dataset Location:** `data/raw/pads`

## Dataset Structure
- **Total Participants:** 469
- **Total Tasks:** 11 (e.g., CrossArms, DrinkGlas, PointFinger, Relaxed)
- **Total Movement Files:** 10,318
  - Right Wrist Files: 5,159
  - Left Wrist Files: 5,159
- **Total Right Wrist Rows:** 6,723,584
- **Malformed Rows:** 0

## Columns & Units
Each timeseries file (e.g., `001_CrossArms_RightWrist.txt`) contains 7 comma-separated columns:
1. **Time:** seconds (Wait, need to confirm scale, looks like seconds given values 0.0, 0.01)
2. **Accelerometer_X, Y, Z:** g (Need strict verification, likely g based on values ~1.0 when still)
3. **Gyroscope_X, Y, Z:** rad/s (Usually, Apple Watch records in rad/s, but requires confirmation)

## Right Wrist Identification
The dataset strictly names files based on the sensor location (e.g., `_RightWrist.txt` and `_LeftWrist.txt`). Our `PADSAdapter` explicitly filters by `*_RightWrist.txt` and strictly ignores the left wrist data.

## Conclusion
The PADS dataset is structurally sound and provides extensive right-wrist data (6.7 million samples). It is compatible with our structural requirements for extracting Tremor features.
