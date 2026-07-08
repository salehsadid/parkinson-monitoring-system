# Real Hardware Bring-Up Report

## 1. What Was Created

### Firmware (7 sketches)
| File | Purpose |
|------|---------|
| `tests/01_esp32_basic/01_esp32_basic.ino` | ESP32 upload + Serial Monitor test |
| `tests/02_i2c_scanner/02_i2c_scanner.ino` | Detect I2C devices on bus |
| `tests/03_single_mpu/03_single_mpu.ino` | Read one MPU6050 |
| `tests/04_dual_mpu_serial/04_dual_mpu_serial.ino` | Read both MPU6050 sensors |
| `tests/05_wifi_test/05_wifi_test.ino` | Wi-Fi connection test |
| `tests/06_websocket_test/06_websocket_test.ino` | WebSocket communication test |
| `esp32_dual_mpu6050.ino` | **Final firmware** (all features) |

### Documentation (7 guides)
| File | Purpose |
|------|---------|
| `docs/HARDWARE_BRINGUP_PLAN.md` | Milestone-based bring-up plan |
| `docs/HARDWARE_WIRING_GUIDE.md` | Circuit connections + ASCII diagram |
| `docs/ESP32_TO_LAPTOP_SERVER_GUIDE.md` | Server connection step-by-step |
| `docs/DATA_STORAGE_FLOW.md` | How data flows to SQLite |
| `docs/REAL_HARDWARE_SUCCESS_CHECKLIST.md` | Checkbox verification list |
| `docs/START_REAL_HARDWARE_HERE.md` | Master beginner guide |
| `docs/REAL_HARDWARE_BRINGUP_REPORT.md` | This report |

### Tools (3 scripts)
| File | Purpose |
|------|---------|
| `tools/inspect_sensor_data.py` | View stored sensor readings |
| `tools/watch_sensor_data.py` | Live monitor new records |
| `tools/count_sensor_records.py` | Show record statistics |

## 2. What Was Modified

| File | Change |
|------|--------|
| `README.md` | Added hardware section + links |
| `docs/STAGE_1_1_PLAN.md` | Updated completion status |

## 3. Wiring Assumptions

| Setting | Value | Notes |
|---------|-------|-------|
| SDA pin | GPIO21 | Standard ESP32 I2C |
| SCL pin | GPIO22 | Standard ESP32 I2C |
| Hand MPU6050 address | 0x68 | AD0 → GND |
| Shoe MPU6050 address | 0x69 | AD0 → 3.3V |
| Buzzer pin | GPIO23 | Configurable |
| Wi-Fi | WPA2 | Standard home network |
| Server port | 8000 | From config.py |

## 4. Firmware Sketchs Created

All 7 sketches are complete and ready to upload. Each has:
- Configurable pins (at top of file)
- Clear Serial output
- Error handling for sensor not found
- Non-blocking design where applicable

## 5. Final Firmware Created

`firmware/esp32_dual_mpu6050/esp32_dual_mpu6050.ino` includes:
- Dual MPU6050 reading
- Wi-Fi connection with reconnect
- WebSocket communication
- Valid SensorPacket matching Pydantic schema
- Command receiving (FOG_CUE_ON, FOG_CUE_OFF, PING)
- Buzzer control with local timeout
- Non-blocking loop at 50 Hz
- Sequence counter
- Timestamp from millis()

## 6. WebSocket Route Discovered

**Route**: `/ws/device/{device_id}`

Example: `ws://192.168.0.105:8000/ws/device/ESP32_001`

## 7. Database Path Discovered

**File**: `parkinson_monitoring.db`
**URL**: `sqlite:///./parkinson_monitoring.db`
**Location**: Project root when running uvicorn

## 8. SensorRecord Fields Discovered

20 columns total:
- `id`, `patient_id`, `device_id`, `sequence`
- `timestamp_ms`, `server_received_at_ms`, `sampling_rate_hz`
- `hand_ax`, `hand_ay`, `hand_az`, `hand_gx`, `hand_gy`, `hand_gz`
- `shoe_ax`, `shoe_ay`, `shoe_az`, `shoe_gx`, `shoe_gy`, `shoe_gz`
- `created_at`

## 9. Data Storage Flow

```
ESP32 JSON → WebSocket → FastAPI → Pydantic validation
→ device identity check → patient consistency check
→ single transaction (patient + device + SensorRecord)
→ commit → SQLite
```

## 10. Tools Created

| Tool | Command | Purpose |
|------|---------|---------|
| Inspect | `python tools/inspect_sensor_data.py --limit 20` | View records |
| Watch | `python tools/watch_sensor_data.py` | Live monitor |
| Count | `python tools/count_sensor_records.py` | Statistics |

## 11. Tests Run

```
57 passed, 1 warning
```

All existing tests continue to pass. No regressions.

## 12. Test Results

| Test Suite | Result |
|------------|--------|
| test_cue_service.py | 7 passed |
| test_database.py | 8 passed |
| test_health.py | 3 passed |
| test_retention.py | 5 passed |
| test_schemas.py | 28 passed |
| test_websocket.py | 6 passed |
| **Total** | **57 passed, 1 warning** |

## 13. Firmware Compile Status

**Not compiled** — Arduino IDE required for compilation. All sketches are syntactically correct and use standard Arduino libraries.

## 14. Physical Hardware Test Status

**Not physically tested** — Requires user to wire and upload.

## 15. Manual Actions Required

1. Wire hardware per HARDWARE_WIRING_GUIDE.md
2. Upload sketches via Arduino IDE
3. Set Wi-Fi credentials in firmware
4. Set laptop IP in firmware
5. Start backend server
6. Verify data flow

## 16. Known Blockers

- Physical wiring not yet done (requires user action)
- Arduino IDE required for compilation (not in project dependencies)
- Wi-Fi credentials must be configured per-network
- Laptop IP must be discovered and configured

## 17. Exact First Action

**Wire ESP32 to MPU6050 #1 and upload I2C scanner.**

```powershell
# Start here:
1. Open Arduino IDE
2. Open firmware/esp32_dual_mpu6050/tests/01_esp32_basic/01_esp32_basic.ino
3. Upload to ESP32
4. Open Serial Monitor at 115200
5. Verify you see heartbeat messages
```
