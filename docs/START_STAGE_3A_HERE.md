# Start Stage 3A Here

Welcome to Stage 3A: Dataset Audit and Adapter Foundation.

## Overview
We have set up the infrastructure to safely ingest, audit, and normalize two datasets (Daphnet for FOG and PADS for Tremor) without breaking the existing Stage 2.1 physical pipeline.

## Prerequisites
The datasets have been reallocated to:
- `data/raw/daphnet/`
- `data/raw/pads/`

## How to Audit the Datasets
To generate the real structural reports based on the files in `data/raw/`:

```powershell
# Audit Daphnet
python tools/audit_daphnet.py

# Audit PADS
python tools/audit_pads.py
```

## How to Import the Datasets
To run the adapters and extract only the relevant, canonical columns into `data/interim/`:

```powershell
# Import Daphnet (extracts Ankle XYZ, drops Thigh/Trunk, normalizes labels)
python tools/import_daphnet.py

# Import PADS (extracts only Right Wrist Accel/Gyro)
python tools/import_pads_right_wrist.py
```

## Next Steps
Before training any models (Stage 3B), you must read the compatibility reports:
1. `docs/UNIT_COMPATIBILITY.md`
2. `docs/SAMPLING_RATE_COMPATIBILITY.md`
3. `docs/PADS_TREMOR_LABEL_AUDIT.md` (Note: PADS lacks granular tremor labels).
