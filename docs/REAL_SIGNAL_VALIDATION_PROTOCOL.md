# Real Signal Validation Protocol

## Purpose

This protocol defines physical tests to validate real sensor data quality before ML development.

## Prerequisites

- ESP32 powered and connected to Wi-Fi
- Backend running (`uvicorn pc_backend.app.main:app --host 0.0.0.0 --port 8000`)
- Both MPU6050 sensors wired and detected
- Serial Monitor open

---

## TEST 1 — Stationary Baseline

**Duration**: 2-5 minutes

**Setup**: Place both sensors on a flat, stable surface. Do not touch them.

**Command to record**:
```powershell
python tools/record_session.py start --patient-id P001 --device-id ESP32_001 --label stationary --notes "baseline test"
```

**Command to stop**:
```powershell
python tools/record_session.py stop --session-id <id-from-start>
```

**Command to analyze**:
```powershell
python tools/analyze_stream_stability.py --patient-id P001 --device-id ESP32_001
python tools/generate_data_quality_report.py --patient-id P001 --device-id ESP32_001
```

**Expected observations**:
- Hand AZ ≈ 9.8 m/s² (gravity)
- Hand AX, AY ≈ 0 (no acceleration)
- Gyro channels ≈ 0 ± small noise
- Sampling rate ≈ 50 Hz
- Packet loss ≈ 0%

**Pass criteria**: Sampling rate within 10% of declared, packet loss < 1%, gyro std < 5 deg/s

---

## TEST 2 — Hand-Only Movement

**Setup**: Keep shoe sensor still. Move hand sensor in various orientations.

**Command**:
```powershell
python tools/record_session.py start --patient-id P001 --device-id ESP32_001 --label voluntary_hand_motion --notes "hand movement test"
```

**Expected observations**:
- Hand stream shows large variations
- Shoe stream remains stable
- Independence check shows hand variance >> shoe variance

**Analyze independence**:
```powershell
python tools/generate_data_quality_report.py --patient-id P001 --device-id ESP32_001
```

---

## TEST 3 — Shoe-Only Movement

**Setup**: Keep hand sensor still. Move/shake shoe sensor.

**Expected observations**:
- Shoe stream shows large variations
- Hand stream remains stable

---

## TEST 4 — Both Moving

**Setup**: Move both sensors simultaneously.

**Expected**: Both streams show independent movement patterns.

---

## TEST 5 — Normal Walking Pilot

**Only if physically safe.**

**Setup**: Mount sensors as intended (hand on glove/ring, shoe on footwear).

**Action**: Walk normally for 2-3 minutes.

**Expected**: Both streams show rhythmic patterns consistent with gait.

---

## TEST 6 — Turning Pilot

**Setup**: Same as Test 5.

**Action**: Walk, stop, turn 180°, walk again.

**Expected**: Gyroscope shows rotation during turns.

---

## TEST 7 — Wi-Fi Interruption

**Setup**: Normal streaming.

**Action**: Briefly disconnect Wi-Fi on ESP32 (or move out of range), then reconnect.

**Analyze**:
```powershell
python tools/analyze_stream_stability.py --patient-id P001 --device-id ESP32_001
```

**Expected**:
- Gap in sequence during disconnection
- Session boundary detected
- No data corruption after reconnection

---

## TEST 8 — ESP32 Reboot

**Setup**: Normal streaming.

**Action**: Press reset button on ESP32.

**Expected**:
- Sequence resets to 0
- Session boundary detected
- New session starts cleanly

---

## TEST 9 — 10-Minute Stream

**Duration**: 10 minutes continuous.

**Purpose**: Verify stability over moderate duration.

**Analyze**:
```powershell
python tools/analyze_stream_stability.py --limit 50000
python tools/analyze_database_growth.py
```

**Pass criteria**: Sustained rate, low loss, no corruption.

---

## TEST 10 — 30-Minute Stream

**Duration**: 30 minutes continuous.

**Purpose**: Verify long-running stability.

**Same analysis as Test 9.**

---

## TEST 11 — Buzzer Interference

**Setup**: Normal streaming.

**Action**: Trigger buzzer commands during acquisition.

```powershell
# From Python (with backend running):
from pc_backend.app.services.cue_service import cue_service
import asyncio
asyncio.run(cue_service.trigger_fog_cue("ESP32_001", "P001", 0.9, duration_ms=3000))
```

**Analyze**: Compare sampling jitter during buzzer vs. idle.

**Expected**: Non-blocking firmware preserves acquisition quality.

---

## Analysis Commands Summary

| Test | Start | Stop | Analyze |
|------|-------|------|---------|
| Any | `record_session.py start ...` | `record_session.py stop ...` | `analyze_stream_stability.py` |
| Quality | — | — | `generate_data_quality_report.py` |
| Growth | — | — | `analyze_database_growth.py` |
| Live | — | — | `live_signal_plot.py` |
| Export | — | — | `export_sensor_session.py` |
