# ML Datasets

This directory stores raw sensor data from ESP32 devices for ML model training.

## Directory Structure

```
datasets/
├── README.md              # This file
├── raw/                   # Raw sensor recordings
├── processed/             # Preprocessed data
└── metadata/              # Dataset documentation
```

## Data Format

### Raw Sensor Data

Raw data is stored as CSV files with the following columns:

| Column | Description | Unit |
|--------|-------------|------|
| timestamp_ms | Unix epoch timestamp | milliseconds |
| patient_id | Patient identifier | string |
| device_id | Device identifier | string |
| sequence | Packet sequence number | integer |
| hand_ax | Hand acceleration X | m/s² |
| hand_ay | Hand acceleration Y | m/s² |
| hand_az | Hand acceleration Z | m/s² |
| hand_gx | Hand gyroscope X | °/s |
| hand_gy | Hand gyroscope Y | °/s |
| hand_gz | Hand gyroscope Z | °/s |
| shoe_ax | Shoe acceleration X | m/s² |
| shoe_ay | Shoe acceleration Y | m/s² |
| shoe_az | Shoe acceleration Z | m/s² |
| shoe_gx | Shoe gyroscope X | °/s |
| shoe_gy | Shoe gyroscope Y | °/s |
| shoe_gz | Shoe gyroscope Z | °/s |

### Labels

Labels are stored in separate CSV files:

| Column | Description |
|--------|-------------|
| timestamp_ms | Event timestamp |
| patient_id | Patient identifier |
| event_type | FOG, TREMOR_RESULT |
| label | Ground truth label |
| notes | Clinical notes |

## Usage

### Loading Data

```python
import pandas as pd

# Load raw sensor data
df = pd.read_csv("datasets/raw/P001_session1.csv")

# Load labels
labels = pd.read_csv("datasets/raw/P001_session1_labels.csv")
```

### Data Collection

1. Connect ESP32 to PC backend
2. Start recording session
3. Annotate events in real-time (if possible)
4. Export data from SQLite database
5. Store in this directory

## Privacy

- Anonymize patient IDs
- Remove identifying information
- Follow institutional data policies
- Document consent forms

## Current Status

**No datasets available yet.**

Datasets will be collected in Stage 3 after:
- IRB approval (if required)
- Patient recruitment
- Data collection sessions
- Clinical annotation
