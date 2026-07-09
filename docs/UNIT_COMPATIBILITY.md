# Unit Compatibility Audit

**Audit Date:** 2026-07-09

## Daphnet (FOG)
- **Reported Units:** milli-g (mg)
- **Runtime (ESP32) Units:** m/s² (as defined in `docs/DATA_CONTRACT.md`)

**Critical Action for Stage 3B:** 
The Daphnet `ankle_ax, ay, az` signals must be converted from milli-g to m/s² before training, OR the ESP32 runtime must be converted to milli-g before inference. 
*Formula:* `m/s² = (milli-g / 1000) * 9.80665`

## PADS (Tremor)
- **Reported Units (Accel):** g (based on gravity hovering at ~1.0)
- **Runtime (ESP32) Units (Accel):** m/s²
- **Reported Units (Gyro):** rad/s (typical for Apple Watch SensorKit)
- **Runtime (ESP32) Units (Gyro):** degrees/second

**Critical Action for Stage 3B:**
1. Convert PADS `right_ax, ay, az` from `g` to `m/s²` (`* 9.80665`).
2. Convert PADS `right_gx, gy, gz` from `rad/s` to `deg/s` (`* 180 / π`).

## Conclusion
Do not silently mix these units during Stage 3B model training. Explicit preprocessing scaling blocks must be implemented.
