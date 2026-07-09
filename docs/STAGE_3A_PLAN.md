# Stage 3A: Dataset Audit, Compatibility Verification, and Dataset Adapter Foundation

This plan outlines the architecture and tasks required to set up the foundation for ingesting, auditing, and adapting the Daphnet and PADS datasets for the Parkinson's Monitoring System.

## Project Context
- **Current State**: Stage 2.1 (Real Signal Validation) is complete. The physical pipeline works: ESP32 streams all 12 channels (6 hand, 6 shoe) to the FastAPI backend and SQLite database. 
- **Requirement**: Build a foundation for Stage 3A without altering the existing physical pipeline, database schemas, or running models. The dataset adapters must be deterministic, non-destructive to raw files, and robust against structural mismatch.
- **Datasets**: 
  - **Daphnet (FOG)**: We will extract only `ankle_ax`, `ankle_ay`, `ankle_az`, and the `annotation` mapping.
  - **PADS (Tremor)**: We will extract only right wrist data (`right_ax`, `right_ay`, `right_az`, `right_gx`, `right_gy`, `right_gz`). Tremor labels will be carefully audited before use.
- **Dataset Availability**: **PRESENT**. The user has provided `dataset_fog_release` (Daphnet) and `pads-parkinsons-disease-smartwatch-dataset-1.0.0` (PADS) in the root directory.

## Proposed Changes

We will introduce a clean object-oriented architecture in the `ml/datasets/` package to handle ingestion, along with several CLI tools in `tools/` to facilitate auditing.

---

### 1. Data Reorganization
- Move `dataset_fog_release/` to `data/raw/daphnet/`.
- Move `pads-parkinsons-disease-smartwatch-dataset-1.0.0/` to `data/raw/pads/`.

### 2. Core ML Dataset Infrastructure

#### [NEW] `ml/datasets/__init__.py`
Exports the base classes and adapters.

#### [NEW] `ml/datasets/schemas.py`
Pydantic schemas for canonical representation:
- `DaphnetCanonicalRecord`: dataset_name, dataset_version, subject_id, recording_id, source_file, timestamp, ankle_ax, ankle_ay, ankle_az, raw_annotation, fog_label.
- `PADSCanonicalRecord`: dataset_name, dataset_version, participant_id, recording_id, task_id, source_file, timestamp, right_ax, right_ay, right_az, right_gx, right_gy, right_gz.

#### [NEW] `ml/datasets/base.py`
Base classes for Dataset Adapters ensuring a standard contract (e.g., `audit()`, `import_data()`).

#### [NEW] `ml/datasets/daphnet_adapter.py`
Adapter for Daphnet. It will parse the raw files, validate the expected schema (timestamp, ankle XYZ, thigh XYZ, trunk XYZ, annotation), drop thigh/trunk data, map annotations (1->0, 2->1, 0->exclude), and enforce subject-identity tracking.

#### [NEW] `ml/datasets/pads_adapter.py`
Adapter for PADS. It will implement right-wrist identification logic by dynamically mapping participants' "handedness", enforce six-channel ingestion, and refrain from faking tremor labels.

---

### 3. CLI Tools

#### [NEW] `tools/audit_daphnet.py`
CLI script to scan `data/raw/daphnet`, report file counts, subjects, annotation balances, and missing data.

#### [NEW] `tools/import_daphnet.py`
CLI script to convert valid Daphnet files into interim canonical CSV/Parquet format in `data/interim/daphnet/`.

#### [NEW] `tools/audit_pads.py`
CLI script to scan `data/raw/pads`, report participant structure, task availability, exact right-wrist logic, and tremor label feasibility based on the provided metadata JSONs.

#### [NEW] `tools/import_pads_right_wrist.py`
CLI script to extract right-wrist data into canonical format, with strict guards against left-wrist substitution.

---

### 4. Documentation

We will create a suite of concise, evidence-based documents under `docs/` based on the direct analysis of the dataset files.

#### [NEW] `docs/STAGE_3A_PLAN.md`
This exact implementation plan.

#### [NEW] `docs/DAPHNET_AUDIT.md` & `docs/PADS_AUDIT.md`
Detailed reports on the structure of the provided datasets.

#### [NEW] `docs/PADS_TREMOR_LABEL_AUDIT.md`
A feasibility study on granular tremor labels in PADS, explaining whether they are suitable for tremor detection/severity or just PD classification.

#### [NEW] `docs/UNIT_COMPATIBILITY.md` & `docs/SAMPLING_RATE_COMPATIBILITY.md`
Rules to prevent silent unit mixing (g vs m/s², rad/s vs deg/s) and resampling guidelines based on actual file analysis.

#### [NEW] `docs/LEAKAGE_PREVENTION.md`
Strict subject-wise split rules.

#### [NEW] `docs/RUNTIME_MODEL_INPUT_MAPPING.md`
Mapping physical coordinates (e.g., shoe_ax -> ankle_ax) and warning of potential axis orientation differences.

#### [NEW] `docs/DATASET_COMPATIBILITY_MATRIX.md` & `docs/STAGE_3A_REPORT.md`
Summaries of compatibility and the final stage report determining if the datasets can proceed to Stage 3B.

#### [NEW] `docs/START_STAGE_3A_HERE.md`
Instructions on how to use the newly created adapters and tools.

---

### 5. Testing and Source Control

#### [NEW] `tests/test_daphnet_adapter.py`
Verify column selection, exclusion, annotation mapping, and graceful handling of malformed rows.

#### [NEW] `tests/test_pads_adapter.py`
Verify right-wrist selection logic, channel preservation, and participant identity tracking.

#### [MODIFY] `.gitignore`
Add explicit ignores for `data/raw/daphnet/*` and `data/raw/pads/*` to prevent committing the datasets.
