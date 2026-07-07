# Data Contract Documentation

## Parkinson's Tremor and FOG Monitoring & Cueing System

### Overview

This document defines the data contracts for communication between ESP32 devices and the PC backend. All data exchange follows strict schema validation using Pydantic.

### Protocol Version

**Current Version:** 1.0

All packets include a `protocol_version` field for backward compatibility. Future versions may add new fields but should maintain backward compatibility with existing parsers.

### Sensor Packet (ESP32 → PC)

#### Structure

```json
{
  "protocol_version": "1.0",
  "message_type": "sensor_data",
  "patient_id": "P001",
  "device_id": "ESP32_001",
  "sequence": 12345,
  "timestamp_ms": 1720012345678,
  "sampling_rate_hz": 50,
  "hand": {
    "ax": 0.12,
    "ay": -0.04,
    "az": 9.71,
    "gx": 2.30,
    "gy": 1.10,
    "gz": -0.40
  },
  "shoe": {
    "ax": 1.24,
    "ay": 0.33,
    "az": 9.22,
    "gx": 12.40,
    "gy": 4.20,
    "gz": 2.10
  }
}
```

#### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocol_version` | string | Yes | Protocol version (default: "1.0") |
| `message_type` | string | Yes | Message type identifier ("sensor_data") |
| `patient_id` | string | Yes | Unique patient identifier (min 1 char) |
| `device_id` | string | Yes | ESP32 device identifier (min 1 char) |
| `sequence` | integer | Yes | Monotonically increasing sequence number (≥ 0) |
| `timestamp_ms` | integer | Yes | Unix epoch timestamp in milliseconds (> 0) |
| `sampling_rate_hz` | integer | Yes | Actual sampling rate in Hz (> 0) |
| `hand` | IMUData | Yes | Hand sensor (tremor analysis) data |
| `shoe` | IMUData | Yes | Shoe sensor (FOG detection) data |

#### IMUData Structure

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `ax` | float | m/s² | Acceleration X-axis |
| `ay` | float | m/s² | Acceleration Y-axis |
| `az` | float | m/s² | Acceleration Z-axis |
| `gx` | float | °/s | Gyroscope X-axis |
| `gy` | float | °/s | Gyroscope Y-axis |
| `gz` | float | °/s | Gyroscope Z-axis |

#### Units

- **Acceleration**: meters per second squared (m/s²)
- **Gyroscope**: degrees per second (°/s)
- **Timestamp**: Unix epoch milliseconds
- **Sampling Rate**: Hertz (Hz)

#### Coordinate Frame Notes

- **Hand Sensor**: Mounted on glove/ring, orientation depends on mounting position
- **Shoe Sensor**: Mounted on shoe, orientation depends on mounting position
- **Future Requirements**: Calibration, axis normalization, orientation handling

#### Validation Rules

1. `patient_id` cannot be empty
2. `device_id` cannot be empty
3. `sequence` must be ≥ 0
4. `timestamp_ms` must be > 0
5. `sampling_rate_hz` must be > 0
6. All IMU fields are required

#### Malformed Packet Handling

- Packets failing validation are logged and discarded
- No response is sent to the device for malformed packets
- Device continues sending subsequent packets

---

### Command Packet (PC → ESP32)

#### Structure

```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "command": "FOG_CUE_ON",
  "command_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp_ms": 1720012345678
}
```

#### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocol_version` | string | Yes | Protocol version (default: "1.0") |
| `message_type` | string | Yes | Message type identifier ("command") |
| `command` | CommandType | Yes | Command to execute |
| `command_id` | string | Yes | Unique command identifier (UUID) |
| `timestamp_ms` | integer | Yes | Unix epoch timestamp in milliseconds (> 0) |

#### Command Types

| Command | Description |
|---------|-------------|
| `FOG_CUE_ON` | Activate rhythmic buzzer cueing |
| `FOG_CUE_OFF` | Deactivate buzzer cueing |
| `PING` | Heartbeat ping to check connectivity |
| `REQUEST_STATUS` | Request device status information |

---

### Event Packets (Future)

#### FOG Event

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "event_type": "FOG",
  "detected_at_ms": 1720012345678,
  "confidence": 0.91,
  "cue_triggered": true,
  "model_version": "v1.0"
}
```

#### Tremor Result

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "event_type": "TREMOR_RESULT",
  "detected_at_ms": 1720012345678,
  "predicted_class": "not_available",
  "confidence": null,
  "model_version": "v1.0"
}
```

### Medical Disclaimer

**Important**: The data contracts defined here are for a research prototype. Event labels and confidence scores do NOT constitute medical diagnoses or clinical assessments. Actual clinical validation requires:
1. Validated clinical datasets
2. Expert annotation
3. Regulatory approval (if used as medical device)

Do NOT use these results for clinical decisions.
