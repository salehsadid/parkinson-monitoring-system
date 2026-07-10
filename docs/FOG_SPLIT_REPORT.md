# FOG Subject-Wise Split Report

## The Challenge
The Daphnet dataset only contains 10 subjects. Of those, Subjects S03, S04, S06, and S10 experienced absolutely **zero FOG events** during their recordings.
If we had performed a purely random split (e.g. 70/15/15), the Validation and Test sets could easily end up with 0 positive FOG examples, making evaluation mathematically impossible.

## The Explicit Deterministic Split
To guarantee robust ML evaluation, we implemented an explicit, deterministic subject split that ensures FOG representation across all datasets. No subject crosses boundaries.

### 1. Training Set
- **Subjects:** S01, S03, S04, S05, S08, S09
- **Total Windows:** 10,570
- **FOG Windows:** 1,339
- **NO FOG Windows:** 9,231
- **Rationale:** The bulk of the data and FOG events belong in the training set. We included two non-FOG subjects (S03, S04) to teach the model how to ignore purely healthy/non-freezing gaits.

### 2. Validation Set
- **Subjects:** S06, S07
- **Total Windows:** 3,596
- **FOG Windows:** 215
- **NO FOG Windows:** 3,381
- **Rationale:** S07 provides active FOG examples for tuning hyperparameters, while S06 provides non-FOG gait.

### 3. Test Set
- **Subjects:** S02, S10
- **Total Windows:** 3,642
- **FOG Windows:** 181
- **NO FOG Windows:** 3,461
- **Rationale:** S02 provides robust FOG examples for final, unseen evaluation. S10 provides non-FOG examples.

## Class Imbalance
The Training set has a severe imbalance (9,231 vs 1,339).
**Recommendation for Stage 3C:** Do not use SMOTE automatically. Use PyTorch's `WeightedRandomSampler` or apply a Class Weight during training. 
- **Calculated Weight 0 (No FOG):** 1.0
- **Calculated Weight 1 (FOG):** ~6.89
