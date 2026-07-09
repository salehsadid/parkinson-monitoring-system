# Stage 2.1 Plan — Real Signal Validation, Stream Quality, Session Recording, Storage Evaluation, ML Data Readiness

## Status: IN PROGRESS

## Baseline

```
Tests: 57 passed, 1 warning
Database: 4521 rows, 1.16 MB, real sensor data
```

## Verified Current Architecture

### SensorRecord Schema (20 columns)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Autoincrement |
| patient_id | VARCHAR(50) FK | Patient identifier |
| device_id | VARCHAR(50) FK | Device identifier |
| sequence | INTEGER | Monotonic from ESP32 |
| timestamp_ms | INTEGER | Device millis() |
| server_received_at_ms | INTEGER | Server receive time (Unix epoch ms) |
| sampling_rate_hz | INTEGER | Declared sampling rate |
| hand_ax..hand_gz | FLOAT | 6 hand IMU channels (m/s², deg/s) |
| shoe_ax..shoe_gz | FLOAT | 6 shoe IMU channels (m/s², deg/s) |
| created_at | DATETIME | Record creation time |

### Data Units (from schema docs)

- Accelerometer (ax, ay, az): m/s²
- Gyroscope (gx, gy, gz): degrees/second
- Timestamps: milliseconds

### Configuration

- Database: `sqlite:///./parkinson_monitoring.db`
- Default sampling rate: 50 Hz
- Retention: 72 hours
- WebSocket: `/ws/device/{device_id}`

### Real Data Available

- 4521 records from P001/ESP32_001
- Sequence range: ~11103-11105 (latest)
- Observed intervals: ~20ms (consistent with 50 Hz)
- Hand AZ: ~9.65 m/s² (gravity-scale confirmed)

## Stage 2.1 Scope

### IN SCOPE

1. Stream quality analysis (sampling rate, packet loss, jitter)
2. Signal quality analysis (baseline, noise, bias)
3. Session recording workflow
4. CSV export
5. Real-time visualization
6. Database growth analysis
7. Storage feasibility evaluation
8. ML readiness assessment
9. Validation protocol
10. Tests

### OUT OF SCOPE

- ML model training
- Dataset downloading
- Blynk integration
- Clinical thresholds
- Medical diagnosis
- Cloud deployment

## Proposed Files

### Analysis Package

```
pc_backend/app/analysis/
├── __init__.py
├── stream_quality.py      # Sampling rate, packet loss, jitter
├── signal_quality.py      # Baseline, noise, magnitude
├── storage_analysis.py    # Growth projections, 72-hour feasibility
└── session_analysis.py    # Session segmentation, independence checks
```

### CLI Tools

```
tools/
├── live_signal_plot.py          # Real-time matplotlib plots
├── plot_sensor_session.py       # Offline session plots
├── record_session.py            # Start/stop recording sessions
├── export_sensor_session.py     # CSV export
├── analyze_database_growth.py   # Storage analysis
├── analyze_stream_stability.py  # Long-running stability
├── generate_data_quality_report.py  # Comprehensive quality report
├── inspect_sensor_data.py       # (existing)
├── watch_sensor_data.py         # (existing)
└── count_sensor_records.py      # (existing)
```

### Documentation

```
docs/
├── STAGE_2_1_PLAN.md                    # This file
├── REAL_SIGNAL_VALIDATION_PROTOCOL.md   # Physical test protocol
├── STORAGE_EVALUATION.md                # 72-hour storage analysis
├── ML_DATA_READINESS.md                 # ML readiness assessment
├── START_STAGE_2_1_HERE.md              # Beginner execution guide
└── STAGE_2_1_REPORT.md                  # Final report
```

## Session Recording Design

Use sidecar JSON metadata files (not new DB table) for safety:

```
data/sessions/
├── session_20260708_174400_P001_ESP32_001.json   # Metadata
├── session_20260708_174400_P001_ESP32_001.csv    # Exported data
└── ...
```

Session JSON contains:
- session_id, patient_id, device_id
- start_time, end_time
- activity_label (manual)
- sensor_placement (manual)
- notes (manual)
- sample_count, firmware_version

## Storage Risks

- At 50 Hz, 1 row ≈ 200 bytes
- 1 hour ≈ 180,000 rows ≈ 36 MB
- 72 hours ≈ 12.96 million rows ≈ 2.59 GB
- SQLite handles this but queries slow without indexes
- Recommendation: keep raw for recent, summarize for old

## Compatibility Risks

- No schema changes needed for Stage 2.1
- Analysis tools read existing data read-only
- Session metadata uses sidecar files, not DB migration
- No new heavy dependencies (matplotlib, numpy, pandas already in requirements.txt)

## Tests to Add

1. Sampling interval calculation
2. Observed rate calculation
3. Empty input handling
4. Single-record input
5. Sequence continuity detection
6. Missing sequence detection
7. Duplicate sequence detection
8. Out-of-order detection
9. Sequence reset detection
10. Timestamp jitter metrics
11. Session gap segmentation
12. Stationary channel stats
13. Magnitude calculation
14. CSV export completeness
15. All 12 IMU channels exported
16. Raw values preserved
17. Storage projection math
18. Database tools handle no records
19. Patient/device filtering
20. Existing tests still pass
