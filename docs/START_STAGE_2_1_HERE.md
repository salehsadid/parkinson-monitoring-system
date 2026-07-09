# START STAGE 2.1 HERE

## Step-by-Step: Validate Your Real Sensor Data

---

## PART 1 — Start Backend

```powershell
cd "D:\Academic Projects\IoT\parkinson-monitoring-system"
.\venv\Scripts\Activate.ps1
uvicorn pc_backend.app.main:app --host 0.0.0.0 --port 8000
```

**Expected**: `Uvicorn running on http://0.0.0.0:8000`

---

## PART 2 — Confirm ESP32 is Streaming

Check Serial Monitor. You should see:
```
[WS] Connected
```

---

## PART 3 — Confirm Database Growth

Open new PowerShell:
```powershell
python tools/count_sensor_records.py
```

**Expected**: Row count increasing over time.

---

## PART 4 — Run Live Signal Plot

```powershell
python tools/live_signal_plot.py --mode hand_accel
```

**Expected**: Real-time plot of hand accelerometer (AX, AY, AZ).

Close the plot window when done.

---

## PART 5 — Move Hand Sensor Only

With live plot running (`--mode hand_accel`), physically move the hand sensor.

**Expected**: Hand values change dramatically. Shoe values (in `--mode shoe_accel`) remain stable.

---

## PART 6 — Move Shoe Sensor Only

```powershell
python tools/live_signal_plot.py --mode shoe_accel
```

Move shoe sensor only.

**Expected**: Shoe values change. Hand values remain stable.

---

## PART 7 — Record Stationary Session

```powershell
python tools/record_session.py start --patient-id P001 --device-id ESP32_001 --label stationary --notes "baseline"
```

Wait 2 minutes. Then:

```powershell
python tools/record_session.py stop --session-id <id-from-start>
```

---

## PART 8 — Analyze Stationary Baseline

```powershell
python tools/generate_data_quality_report.py --patient-id P001 --device-id ESP32_001
```

**Check**: Hand AZ ≈ 9.8, gyro std is low.

---

## PART 9 — Record Movement Session

```powershell
python tools/record_session.py start --patient-id P001 --device-id ESP32_001 --label voluntary_hand_motion
```

Move both sensors for 1 minute. Then stop.

---

## PART 10 — Analyze Sampling Rate

```powershell
python tools/analyze_stream_stability.py --patient-id P001 --device-id ESP32_001
```

**Check**: Observed rate ≈ 50 Hz, mean interval ≈ 20 ms.

---

## PART 11 — Analyze Sequence Gaps

Same output as Part 10. Check:
- Missing: should be 0 or very low
- Duplicates: should be 0
- Loss %: should be < 1%

---

## PART 12 — Analyze Jitter

Same output as Part 10. Check:
- Device jitter std < 5 ms
- P95 < 30 ms

---

## PART 13 — Export CSV

```powershell
python tools/export_sensor_session.py --patient-id P001 --device-id ESP32_001 --limit 1000 --output data/raw/test_export.csv
```

---

## PART 14 — Open CSV

Open `data/raw/test_export.csv` in Excel or text editor.

**Verify**: 20 columns, all 12 IMU channels present, values are numeric.

---

## PART 15 — 10-Minute Stream

Let ESP32 stream for 10 minutes. Then:

```powershell
python tools/analyze_stream_stability.py --limit 50000
python tools/analyze_database_growth.py
```

---

## PART 16 — Wi-Fi Interruption Test

Briefly disconnect ESP32 from Wi-Fi (or move out of range). Reconnect.

Analyze:
```powershell
python tools/analyze_stream_stability.py
```

**Expected**: Session boundary detected, no corruption.

---

## PART 17 — ESP32 Reboot Test

Press reset button on ESP32. Wait for reconnection.

Analyze: Same as Part 16. Sequence should reset.

---

## PART 18 — Buzzer Interference Test

```powershell
python tools/analyze_stream_stability.py --patient-id P001 --device-id ESP32_001
```

Compare jitter during normal streaming vs. when buzzer is active.

---

## PART 19 — Analyze Database Growth

```powershell
python tools/analyze_database_growth.py
```

**Check**: 72-hour projection is feasible (< 2 GB).

---

## PART 20 — Review ML Readiness

Open `docs/ML_DATA_READINESS.md`.

All 18 items should be READY or PARTIALLY READY.
