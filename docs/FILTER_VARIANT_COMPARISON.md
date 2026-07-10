# Filter Variant Comparison

## Why Filter Variants Matter
In Stage 3B, we utilized `scipy.signal.filtfilt` (a zero-phase filter) to remove high-frequency noise above 20Hz. However, `filtfilt` operates by filtering the signal forward, then backward in time. This creates a "zero-phase" output but strictly relies on knowing future samples. 
In our ESP32 deployment (Stage 4), the microcontroller processes data in real-time. It can only use a causal filter (relying on present and past samples). If an ML model learns to rely on the perfectly clean, future-aware zero-phase signals, it may degrade significantly when deployed on the ESP32.

To prevent this, Stage 3B.1 introduces three mathematically distinct variants for training and comparison:

### 1. `none`
- **Mechanism:** No software filtering. Preserves the 50Hz resampling.
- **Pros:** Exactly represents the raw signal (if ESP32 applies no software filter).
- **Cons:** Contains high-frequency noise that the hardware MPU6050 DLPF didn't catch.

### 2. `causal` (Deployment-Aligned)
- **Mechanism:** `scipy.signal.sosfilt` (Second-Order Sections Butterworth, order=4, cutoff=20Hz).
- **Pros:** 100% causal. Can be identically translated to C++ on the ESP32. Uses `sosfilt_zi` scaled to the initial recording sample to minimize transient "startup" artifacts.
- **Cons:** Introduces a phase delay (shifts the signal slightly in time).

### 3. `offline_zero_phase` (Legacy)
- **Mechanism:** `scipy.signal.filtfilt` (Butterworth, order=4, cutoff=20Hz).
- **Pros:** Perfect phase alignment; no temporal shifting.
- **Cons:** Relies on future samples. Impossible to implement in real-time.

## Visual QA Analysis
Using `tools/qa_compare_filters.py`, we generated overlapping plots (`data/qa/compare_fog_window.png` and `data/qa/compare_no_fog_window.png`).
- The `none` signal appears jagged.
- The `offline_zero_phase` signal perfectly tracks the center of the `none` signal.
- The `causal` signal is smoothed but slightly phase-delayed compared to `none` (shifted to the right), which is exactly the expected mathematical behavior of a real-time filter.

**Recommendation:** For Stage 3C, we should evaluate model performance on the `causal` or `none` datasets to ensure deployment fidelity.
