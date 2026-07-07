# Stage 1.1 Plan — Hardening, Consistency, and Integration Fixes

## Status: COMPLETED

```
Baseline: 47 passed, 6 warnings
Final:    57 passed, 1 warning
```

- Fixed: 5 Pydantic v2 warnings (migrated to ConfigDict)
- Added: 10 new tests for Stage 1.1 features
- Remaining: 1 Starlette httpx deprecation (external, not our code)

## Issues Verified

### 1. Device Identity Mismatch (HIGH)
- **File**: `pc_backend/app/websocket/sensor_endpoint.py`
- **Problem**: WebSocket endpoint accepts `device_id` from URL, but packet may contain a different `device_id`. Currently uses URL `device_id` for DB storage without validating against packet.
- **Risk**: Silent identity inconsistency.

### 2. Device-Patient Consistency (HIGH)
- **File**: `pc_backend/app/websocket/sensor_endpoint.py`
- **Problem**: If device ESP32_001 is registered to P001, a later packet claiming P002 is accepted without rejection.
- **Risk**: Corrupted patient association history.

### 3. Database Engine Fragmentation (HIGH)
- **Files**: `pc_backend/app/database/base.py`, `pc_backend/app/database/session.py`
- **Problem**: `init_database()` creates one engine with PRAGMA listeners. `DatabaseManager` creates a separate engine without PRAGMAs. Runtime sessions may not have WAL/foreign_keys.
- **Risk**: Inconsistent SQLite configuration.

### 4. Missing Server Receive Timestamp (HIGH)
- **File**: `pc_backend/app/database/base.py`
- **Problem**: `SensorRecord` has no `server_received_at_ms`. Device clock may be inaccurate in Stage 2.
- **Risk**: No way to distinguish device time from server arrival time.

### 5. Multiple Commits Per Packet (MEDIUM)
- **File**: `pc_backend/app/websocket/sensor_endpoint.py`
- **Problem**: `handle_sensor_packet` commits separately for patient creation, device creation/update, and sensor record. At 50 Hz this is inefficient and risks partial state.
- **Risk**: Performance issues, partial writes on failure.

### 6. Generic Exception on Validation (MEDIUM)
- **File**: `pc_backend/app/websocket/sensor_endpoint.py`
- **Problem**: Catches `Exception` instead of Pydantic `ValidationError`. May swallow programming errors as validation failures.
- **Risk**: Hidden bugs masked as bad packets.

### 7. Duplicate Sequence Handling (LOW)
- **Problem**: No deduplication policy documented or implemented. ESP32 reboot may restart sequence at 0.
- **Decision**: Document policy, do not add fragile deduplication in Stage 1.1.

### 8. Simulator Async Task Leak (MEDIUM)
- **File**: `simulator/mock_esp32.py`
- **Problem**: `receive_task` created via `asyncio.create_task()` is never cancelled on disconnect/reconnect.
- **Risk**: Orphan tasks accumulate on reconnect.

### 9. Cue Fail-Safe (MEDIUM)
- **File**: `pc_backend/app/schemas/commands.py`, `pc_backend/app/services/cue_service.py`
- **Problem**: No `duration_ms` field. If FOG_CUE_OFF is lost, ESP32 could cue indefinitely.
- **Decision**: Add optional `duration_ms` to CommandPacket with bounds.

### 10. Cue State Consistency (LOW)
- **File**: `pc_backend/app/services/cue_service.py`
- **Problem**: Calling `trigger_fog_cue()` twice overwrites previous cue info silently.
- **Decision**: Log warning, update state cleanly.

### 11. Pydantic v2 Warnings (LOW)
- **Files**: `sensor.py`, `commands.py`, `events.py`
- **Problem**: Deprecated `class Config` instead of `model_config = ConfigDict(...)`.
- **Decision**: Migrate to `ConfigDict`.

### 12. Unused Imports (LOW)
- `sensor.py`: `from typing import Optional` unused
- `commands.py`: `from typing import Optional` unused
- `cue_service.py`: `import uuid` unused
- `sensor_endpoint.py`: `from typing import Optional` unused, `from pc_backend.app.core.config import settings` unused

## Proposed Fixes

| # | Issue | Fix | Files |
|---|-------|-----|-------|
| 1 | Device identity mismatch | Validate `packet.device_id == url device_id`, reject on mismatch | sensor_endpoint.py |
| 2 | Device-patient consistency | Check existing device patient, reject if different | sensor_endpoint.py |
| 3 | DB engine fragmentation | Single shared engine in DatabaseManager with PRAGMAs | base.py, session.py |
| 4 | Server receive timestamp | Add `server_received_at_ms` column to SensorRecord | base.py, sensor_endpoint.py |
| 5 | Multiple commits | Single transaction for patient+device+record | sensor_endpoint.py |
| 6 | Generic exception | Catch `pydantic.ValidationError` specifically | sensor_endpoint.py |
| 7 | Duplicate sequences | Document policy only | DATA_CONTRACT.md |
| 8 | Simulator async cleanup | Cancel receive_task on disconnect, use try/finally | mock_esp32.py |
| 9 | Cue fail-safe | Add optional `duration_ms` with bounds to CommandPacket | commands.py, cue_service.py |
| 10 | Cue state consistency | Log warning on duplicate trigger, clean state management | cue_service.py |
| 11 | Pydantic v2 warnings | Replace `class Config` with `ConfigDict` | sensor.py, commands.py, events.py |
| 12 | Unused imports | Remove unused imports | sensor.py, commands.py, sensor_endpoint.py, cue_service.py |

## Compatibility Risks

- **Database schema change** (`server_received_at_ms`): Existing `parkinson_monitoring.db` will need migration. Since this is a development database with no real data, safest approach is to delete and recreate.
- **CommandPacket schema change** (`duration_ms`): Optional field with default, backward compatible.
- **No public API changes**: WebSocket endpoint path unchanged, REST endpoints unchanged.

## Tests to Add

1. Device ID match accepted
2. Device ID mismatch rejected
3. Mismatch not persisted to DB
4. New device-patient registration
5. Existing device same patient accepted
6. Existing device different patient rejected
7. Conflicting packet not persisted
8. Invalid Pydantic packet rejected (specific ValidationError)
9. Connection survives invalid packet
10. Server receive timestamp populated and reasonable
11. Single transaction commit (all or nothing)
12. Cue duration_ms valid/invalid validation
13. Repeated cue trigger behavior
14. Cue stop with no active cue

---

## Completed Fixes Summary

### Files Modified

| File | Changes |
|------|---------|
| `pc_backend/app/database/base.py` | Shared engine, FK constraints, `server_received_at_ms` |
| `pc_backend/app/database/session.py` | Uses `create_configured_engine()`, consistent PRAGMAs |
| `pc_backend/app/schemas/sensor.py` | `ConfigDict`, whitespace validation |
| `pc_backend/app/schemas/commands.py` | `ConfigDict`, `duration_ms` with bounds |
| `pc_backend/app/schemas/events.py` | `ConfigDict`, removed unused imports |
| `pc_backend/app/websocket/sensor_endpoint.py` | Identity validation, single transaction, `ValidationError` catch |
| `pc_backend/app/services/cue_service.py` | `duration_ms` parameter, fail-safe documentation |
| `tests/test_database.py` | Updated for `server_received_at_ms` |
| `tests/test_retention.py` | Updated for `server_received_at_ms` |
| `tests/test_schemas.py` | Added `duration_ms` validation tests |

### Key Changes

1. **Device Identity Validation**: `_validate_device_identity()` checks URL vs packet device_id
2. **Patient Consistency**: Rejects packets from device registered to different patient
3. **Single Transaction**: All DB ops in one commit (patient + device + record)
4. **Server Timestamp**: `server_received_at_ms` captures packet arrival time
5. **Specific ValidationError**: Only catches Pydantic errors, not generic exceptions
6. **Cue Fail-Safe**: `duration_ms` field with 1000-30000ms bounds
7. **Pydantic v2**: Migrated from `class Config` to `ConfigDict`
8. **PRAGMA Consistency**: All engines use WAL + foreign_keys=ON
