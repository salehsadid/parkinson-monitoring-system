"""
Session analysis: recording sessions, metadata, export helpers.
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict


SESSIONS_DIR = "data/sessions"

ACTIVITY_LABELS = [
    "stationary",
    "normal_walk",
    "slow_walk",
    "turn",
    "sit",
    "stand",
    "hand_rest",
    "voluntary_hand_motion",
    "simulated_tremor_like_motion",
    "simulated_freeze_like_motion",
    "unknown",
    "custom",
]


@dataclass
class RecordingSession:
    session_id: str
    patient_id: str
    device_id: str
    start_time: str
    end_time: Optional[str]
    activity_label: str
    sensor_placement_hand: str
    sensor_placement_shoe: str
    notes: str
    sample_count: int
    firmware_version: str
    protocol_version: str
    export_path: Optional[str]


def generate_session_id(patient_id: str, device_id: str) -> str:
    """Generate a session ID from timestamp and identifiers."""
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"session_{ts}_{patient_id}_{device_id}"


def create_session_metadata(
    session_id: str,
    patient_id: str,
    device_id: str,
    activity_label: str = "unknown",
    sensor_placement_hand: str = "unknown",
    sensor_placement_shoe: str = "unknown",
    notes: str = "",
    firmware_version: str = "unknown",
) -> dict:
    """Create session metadata dictionary."""
    return {
        "session_id": session_id,
        "patient_id": patient_id,
        "device_id": device_id,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": None,
        "activity_label": activity_label,
        "sensor_placement_hand": sensor_placement_hand,
        "sensor_placement_shoe": sensor_placement_shoe,
        "notes": notes,
        "sample_count": 0,
        "firmware_version": firmware_version,
        "protocol_version": "1.0",
        "export_path": None,
    }


def save_session_metadata(metadata: dict, sessions_dir: str = SESSIONS_DIR) -> str:
    """Save session metadata to JSON file. Returns file path."""
    os.makedirs(sessions_dir, exist_ok=True)
    filename = f"{metadata['session_id']}.json"
    filepath = os.path.join(sessions_dir, filename)
    with open(filepath, "w") as f:
        json.dump(metadata, f, indent=2)
    return filepath


def load_session_metadata(session_id: str, sessions_dir: str = SESSIONS_DIR) -> Optional[dict]:
    """Load session metadata by ID."""
    filepath = os.path.join(sessions_dir, f"{session_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)


def list_sessions(sessions_dir: str = SESSIONS_DIR) -> List[dict]:
    """List all session metadata files."""
    if not os.path.exists(sessions_dir):
        return []
    sessions = []
    for fn in os.listdir(sessions_dir):
        if fn.endswith(".json"):
            filepath = os.path.join(sessions_dir, fn)
            with open(filepath, "r") as f:
                sessions.append(json.load(f))
    return sorted(sessions, key=lambda s: s.get("start_time", ""))


def update_session_metadata(
    session_id: str,
    updates: dict,
    sessions_dir: str = SESSIONS_DIR,
) -> Optional[dict]:
    """Update session metadata with new values."""
    metadata = load_session_metadata(session_id, sessions_dir)
    if metadata is None:
        return None
    metadata.update(updates)
    save_session_metadata(metadata, sessions_dir)
    return metadata
