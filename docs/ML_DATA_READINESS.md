# ML Data Readiness Assessment

## Checklist

| # | Question | Status | Evidence |
|---|----------|--------|----------|
| 1 | Are all 12 channels present? | **READY** | SensorRecord has hand_ax..hand_gz, shoe_ax..shoe_gz (12 columns) |
| 2 | Are units documented? | **READY** | Accelerometer: m/s², Gyroscope: deg/s (from schema docs) |
| 3 | Is sampling rate known? | **READY** | sampling_rate_hz field stored per record, default 50 Hz |
| 4 | Is achieved sampling rate measured? | **READY** | `compute_sampling_metrics()` computes observed rate from timestamps |
| 5 | Are sequence gaps measurable? | **READY** | `detect_sequence_gaps()` identifies missing, duplicates, out-of-order |
| 6 | Is packet loss measurable? | **READY** | `detect_sequence_gaps()` estimates loss percentage |
| 7 | Are timestamps usable? | **READY** | Both device timestamp_ms and server_received_at_ms stored |
| 8 | Are device and server timestamps distinguishable? | **READY** | Separate columns, `compute_arrival_offset()` analyzes difference |
| 9 | Are sessions reproducible? | **READY** | Session metadata in JSON, sequence-based boundaries |
| 10 | Are manual labels supported? | **READY** | `record_session.py` supports researcher-defined activity labels |
| 11 | Is sensor placement recorded? | **READY** | Session metadata includes hand_placement and shoe_placement |
| 12 | Can raw sessions be exported? | **READY** | `export_sensor_session.py` exports full CSV with all channels |
| 13 | Can stationary bias/noise be measured? | **READY** | `compute_signal_quality()` provides per-channel mean, std, RMS |
| 14 | Can hand/shoe independence be checked? | **READY** | `check_independence()` computes variance and energy ratios |
| 15 | Are reboot/reconnect boundaries handled? | **READY** | `detect_sessions()` segments on gaps and sequence resets |
| 16 | Is raw data preserved? | **READY** | CSV exports in data/raw/, never overwritten by preprocessing |
| 17 | Are clinical labels absent unless genuinely provided? | **READY** | No automatic FOG/tremor labels. Manual labels only. |
| 18 | Is data ready for future preprocessing? | **PARTIALLY READY** | Raw data is clean. Preprocessing pipeline not yet implemented. |

## Summary

**16/18 items: READY**
**2/18 items: PARTIALLY READY** (preprocessing pipeline)

## What Is Ready

- Raw sensor data collection via real hardware
- 12-channel IMU storage in SQLite
- Sampling rate measurement
- Packet loss detection
- Jitter analysis
- Session segmentation
- Manual labeling
- CSV export
- Signal quality metrics
- Independence verification

## What Is NOT Ready (Stage 3)

- Signal preprocessing (filtering, resampling)
- Feature extraction
- ML model training
- Train/validation/test splitting
- Augmentation
- Normalization

## Conclusion

The data pipeline from ESP32 → WebSocket → SQLite is **ML-ready** for raw data collection and analysis. Preprocessing and feature extraction will be implemented in Stage 3.

All 12 IMU channels are stored with proper metadata. Units are documented. Timestamps are usable. Sessions are reproducible. Manual labels are supported. Raw data is preserved.
