# Data Storage Flow

## Overview

This document explains exactly how real sensor data flows from ESP32 to SQLite database.

## Complete Data Flow

```
ESP32 JSON Packet (dual MPU6050)
│
│  WebSocket connection
│  ws://LAPTOP_IP:8000/ws/device/ESP32_001
│
▼
FastAPI WebSocket Endpoint
│  pc_backend/app/websocket/sensor_endpoint.py
│  Route: /ws/device/{device_id}
│
▼
JSON Deserialization
│  json.loads(message)
│
▼
Pydantic SensorPacket Validation
│  pc_backend/app/schemas/sensor.py
│  Validates: patient_id, device_id, sequence,
│  timestamp_ms, sampling_rate_hz, hand, shoe
│
│  Rejects: malformed JSON, missing fields,
│  invalid types, empty strings
│
▼
Device Identity Validation
│  _validate_device_identity()
│  - device_id in URL must match packet.device_id
│  - device must exist in database
│  - device must be registered to packet.patient_id
│
▼
Server Receive Timestamp
│  server_received_at_ms = int(time.time() * 1000)
│  Captures when server received the packet
│
▼
Single Transaction (all-or-nothing)
│  1. Ensure patient exists (auto-register if new)
│  2. Update device last_seen_at
│  3. Create SensorRecord
│  4. db.commit()
│
│  On any error: db.rollback()
│
▼
SQLite Database
│  File: parkinson_monitoring.db
│  Table: sensor_records
│  20 columns including all IMU data
│
▼
You can inspect with tools/
```

## Database File Location

Default path (from config.py):
```
sqlite:///./parkinson_monitoring.db
```

When running uvicorn from project root:
```
D:\Academic Projects\IoT\parkinson-monitoring-system\parkinson_monitoring.db
```

## SensorRecord Schema

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, autoincrement |
| patient_id | VARCHAR(50) | FK → patients.patient_id |
| device_id | VARCHAR(50) | FK → devices.device_id |
| sequence | INTEGER | Monotonic counter from ESP32 |
| timestamp_ms | INTEGER | Device timestamp (millis()) |
| server_received_at_ms | INTEGER | Server receive time |
| sampling_rate_hz | INTEGER | Sampling rate (50 Hz) |
| hand_ax | FLOAT | Hand accelerometer X (m/s²) |
| hand_ay | FLOAT | Hand accelerometer Y (m/s²) |
| hand_az | FLOAT | Hand accelerometer Z (m/s²) |
| hand_gx | FLOAT | Hand gyroscope X (deg/s) |
| hand_gy | FLOAT | Hand gyroscope Y (deg/s) |
| hand_gz | FLOAT | Hand gyroscope Z (deg/s) |
| shoe_ax | FLOAT | Shoe accelerometer X (m/s²) |
| shoe_ay | FLOAT | Shoe accelerometer Y (m/s²) |
| shoe_az | FLOAT | Shoe accelerometer Z (m/s²) |
| shoe_gx | FLOAT | Shoe gyroscope X (deg/s) |
| shoe_gy | FLOAT | Shoe gyroscope Y (deg/s) |
| shoe_gz | FLOAT | Shoe gyroscope Z (deg/s) |
| created_at | DATETIME | Server creation time |

## Timestamps Explained

### timestamp_ms
- Source: ESP32 `millis()`
- Meaning: Milliseconds since ESP32 boot
- Use: Device-side timing, sequence correlation

### server_received_at_ms
- Source: Server `int(time.time() * 1000)`
- Meaning: Unix epoch milliseconds when server received packet
- Use: Server-side timing, accurate timestamps

### created_at
- Source: SQLAlchemy default
- Meaning: When record was created in database
- Use: Database record creation time

## Transaction Behavior

### Successful Packet
```
Patient exists? → Create/update
Device exists? → Update last_seen_at
Create SensorRecord with all fields
COMMIT (all-or-nothing)
```

### Failed Packet
```
Any exception occurs
ROLLBACK all changes
Log error
Connection continues (next packet)
```

## Auto-Registration (Dev Convenience)

If a packet arrives for an unknown patient or device:
- Patient is automatically created
- Device is automatically created and linked to patient

This is for development convenience. Production should pre-register patients and devices.

## Querying Data

### Using Python Tools
```bash
python tools/inspect_sensor_data.py --limit 20
python tools/inspect_sensor_data.py --patient-id P001
python tools/count_sensor_records.py
python tools/watch_sensor_data.py
```

### Using SQLite Directly
```sql
SELECT
  id, patient_id, device_id, sequence,
  timestamp_ms, server_received_at_ms,
  hand_ax, hand_ay, hand_az,
  shoe_ax, shoe_ay, shoe_az
FROM sensor_records
ORDER BY id DESC
LIMIT 20;
```

### Using sqlite3 CLI
```bash
sqlite3 parkinson_monitoring.db
.headers on
.mode column
SELECT id, patient_id, sequence, server_received_at_ms,
       hand_ax, hand_ay, hand_az,
       shoe_ax, shoe_ay, shoe_az
FROM sensor_records
ORDER BY id DESC
LIMIT 20;
```
