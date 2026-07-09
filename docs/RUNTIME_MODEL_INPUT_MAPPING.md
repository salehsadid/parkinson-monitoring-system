# Runtime Model Input Mapping

**Audit Date:** 2026-07-09

To ensure the models trained in Stage 3B function correctly when deployed against the ESP32 runtime, exact channel mapping must be established.

## FOG Detection Mapping

| Daphnet (Training) | Physical Meaning | ESP32 Runtime (Database) | Physical Meaning |
|---|---|---|---|
| `ankle_ax` | Ankle Accel X | `shoe_ax` | Right Ankle Accel X |
| `ankle_ay` | Ankle Accel Y | `shoe_ay` | Right Ankle Accel Y |
| `ankle_az` | Ankle Accel Z | `shoe_az` | Right Ankle Accel Z |

> [!WARNING]
> **Axis Orientation Warning:** The orientation of the sensor on the Daphnet patients' ankles may not exactly match the orientation of the MPU6050 mounted on the user's shoe in our system. During Stage 3B, calculate magnitude-based features (e.g., `sqrt(x^2 + y^2 + z^2)`) to achieve orientation invariance.

## Tremor Detection Mapping

| PADS (Training) | Physical Meaning | ESP32 Runtime (Database) | Physical Meaning |
|---|---|---|---|
| `right_ax` | Right Wrist Accel X | `hand_ax` | Right Hand Accel X |
| `right_ay` | Right Wrist Accel Y | `hand_ay` | Right Hand Accel Y |
| `right_az` | Right Wrist Accel Z | `hand_az` | Right Hand Accel Z |
| `right_gx` | Right Wrist Gyro X | `hand_gx` | Right Hand Gyro X |
| `right_gy` | Right Wrist Gyro Y | `hand_gy` | Right Hand Gyro Y |
| `right_gz` | Right Wrist Gyro Z | `hand_gz` | Right Hand Gyro Z |

> [!WARNING]
> **Placement Warning:** PADS data is collected from a smartwatch on the wrist. Our system assumes a glove or ring mount on the hand. While dynamics are similar, high-frequency finger tremors might be attenuated at the wrist. Models should rely on fundamental frequency features rather than raw amplitudes.
