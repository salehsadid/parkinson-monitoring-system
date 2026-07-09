# PADS Tremor Label Audit

**Audit Date:** 2026-07-09

## Objective
To determine if the PADS dataset contains objective, granular tremor labels (e.g., sample-level or window-level) that can be used to train a binary or multi-class Tremor Detection model.

## Metadata Inspection
We inspected the `patients/` JSON files (e.g., `patient_001.json`).

### Relevant Fields Found
- `condition`: String (e.g., "Healthy", "Parkinson's Disease")
- `disease_comment`: String
- `effect_of_alcohol_on_tremor`: String

### Tremor Severity/Label Fields
We **did not** find granular, per-sample, or per-window tremor annotations. 
The dataset primarily labels the *patient* as having PD or being Healthy. It does not label *when* a tremor occurs during a recording.

## Feasibility Verdicts

| Goal | Verdict | Evidence / Notes |
|---|---|---|
| Sample-level tremor detection | **NO** | No labels exist per sample (e.g., timestamps). |
| Window-level tremor detection | **NO** | No labels exist for time windows. |
| Task-level tremor classification | **PARTIAL** | We know the task (e.g., "Relaxed"), but we do not know if they were actively trembling during it. |
| Subject-level tremor phenotype | **NO** | No UPDRS sub-scores are provided in the public JSONs. |
| PD vs HC (Subject-level) | **YES** | The `condition` field reliably distinguishes PD from Healthy Controls. |

## Crucial Rule: Do Not Fake Labels
As mandated, we **WILL NOT** map "PD diagnosis" to a "Tremor = 1" label. A patient with PD does not tremor 100% of the time, and a Healthy Control may have physiological tremor. 

## Recommendation for Stage 3B
Because there are no granular tremor labels, **we cannot train a supervised Tremor Detection model** using PADS directly. 
Alternative approaches for Stage 3B:
1. Treat this as an Anomaly Detection / One-Class SVM problem (train on Healthy, detect PD).
2. Use a different dataset for supervised Tremor detection (e.g., Levodopa response datasets with UPDRS scores).
3. Use PADS strictly for Subject-level PD classification using global features.
