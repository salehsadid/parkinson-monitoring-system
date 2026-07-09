# Sampling Rate Compatibility Audit

**Audit Date:** 2026-07-09

## Current System (ESP32)
- **Target Sampling Rate:** 50 Hz

## Daphnet (FOG)
- **Native Sampling Rate:** 64 Hz
- **Compatibility:** Mismatch
- **Action for Stage 3B:** Daphnet data must be downsampled from 64 Hz to 50 Hz before training, or the ESP32 must be adjusted to 64 Hz. Given ESP32 Wi-Fi constraints, downsampling Daphnet to 50 Hz using a polyphase filter (`scipy.signal.resample_poly`) is highly recommended.

## PADS (Tremor)
- **Native Sampling Rate:** 100 Hz (based on timestamps: 0.0, 0.01)
- **Compatibility:** Mismatch
- **Action for Stage 3B:** PADS data must be downsampled from 100 Hz to 50 Hz (decimation by a factor of 2).

## Conclusion
No models should be trained directly on the raw 64 Hz or 100 Hz data if the runtime inference will occur at 50 Hz, as frequency-domain features (vital for Tremor and FOG) will be completely corrupted. Resampling must be the first step in the Stage 3B ML pipeline.
