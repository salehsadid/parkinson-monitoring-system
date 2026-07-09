from pydantic import BaseModel, Field
from typing import Optional

class DaphnetCanonicalRecord(BaseModel):
    dataset_name: str = "Daphnet"
    dataset_version: str = "1.0"
    subject_id: str
    recording_id: str
    source_file: str
    timestamp: float
    ankle_ax: float
    ankle_ay: float
    ankle_az: float
    raw_annotation: int
    fog_label: int

class PADSCanonicalRecord(BaseModel):
    dataset_name: str = "PADS"
    dataset_version: str = "1.0.0"
    participant_id: str
    recording_id: str
    task_id: str
    source_file: str
    timestamp: float
    right_ax: float
    right_ay: float
    right_az: float
    right_gx: float
    right_gy: float
    right_gz: float
