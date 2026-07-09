# Dataset Compatibility Matrix

**Audit Date:** 2026-07-09

| Feature | Daphnet (FOG) | PADS (Tremor) | ESP32 Runtime | Action Required |
|---|---|---|---|---|
| **Sampling Rate** | 64 Hz | 100 Hz | 50 Hz | **Resample** datasets to 50 Hz |
| **Accel Units** | milli-g | g | m/s² | **Scale** datasets to m/s² |
| **Gyro Units** | N/A | rad/s | deg/s | **Scale** PADS to deg/s |
| **Placement** | Ankle / Leg / Hip | Wrist | Shoe / Hand | Extract rotation-invariant features |
| **Granular Labels**| Yes (Sample level) | No (Subject level) | N/A | **Blocker:** PADS cannot be used for supervised tremor detection without generating custom labels. |
| **Data Volume** | ~8 hours | ~18 hours | N/A | Sufficient for baseline modeling |
