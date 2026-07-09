"""
Session Recording — Start/stop recording sessions with metadata.

Usage:
    python tools/record_session.py start --patient-id P001 --device-id ESP32_001 --label stationary
    python tools/record_session.py stop --session-id session_20260708_174400_P001_ESP32_001
    python tools/record_session.py list
"""

import argparse
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord
from pc_backend.app.analysis.session_analysis import (
    generate_session_id, create_session_metadata,
    save_session_metadata, load_session_metadata,
    update_session_metadata, list_sessions, ACTIVITY_LABELS,
)


def cmd_start(args):
    session_id = generate_session_id(args.patient_id, args.device_id)
    metadata = create_session_metadata(
        session_id=session_id,
        patient_id=args.patient_id,
        device_id=args.device_id,
        activity_label=args.label,
        sensor_placement_hand=args.hand_placement,
        sensor_placement_shoe=args.shoe_placement,
        notes=args.notes,
    )

    # Get current max sequence as start marker
    engine = create_engine(settings.DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        max_record = db.query(SensorRecord).filter(
            SensorRecord.device_id == args.device_id
        ).order_by(SensorRecord.id.desc()).first()
        if max_record:
            metadata["start_sequence"] = max_record.sequence
    finally:
        db.close()

    filepath = save_session_metadata(metadata)
    print(f"Session started: {session_id}")
    print(f"Metadata saved: {filepath}")
    print(f"Label: {args.label}")
    print(f"\nNow streaming. To stop, run:")
    print(f"  python tools/record_session.py stop --session-id {session_id}")


def cmd_stop(args):
    metadata = load_session_metadata(args.session_id)
    if not metadata:
        print(f"Session not found: {args.session_id}")
        return

    # Count samples since start
    engine = create_engine(settings.DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        start_seq = metadata.get("start_sequence", 0)
        count = db.query(func.count(SensorRecord.id)).filter(
            SensorRecord.device_id == metadata["device_id"],
            SensorRecord.sequence >= start_seq,
        ).scalar()
        metadata["sample_count"] = count
    finally:
        db.close()

    metadata["end_time"] = __import__("datetime").datetime.utcnow().isoformat()
    save_session_metadata(metadata)

    print(f"Session stopped: {args.session_id}")
    print(f"Samples recorded: {metadata['sample_count']}")


def cmd_list(args):
    sessions = list_sessions()
    if not sessions:
        print("No sessions found.")
        return
    print(f"\n{'='*70}")
    print(f"  Recording Sessions ({len(sessions)} total)")
    print(f"{'='*70}")
    for s in sessions:
        status = "COMPLETE" if s.get("end_time") else "RECORDING"
        print(f"\n  {s['session_id']}")
        print(f"    Status:   {status}")
        print(f"    Patient:  {s.get('patient_id')}")
        print(f"    Device:   {s.get('device_id')}")
        print(f"    Label:    {s.get('activity_label')}")
        print(f"    Start:    {s.get('start_time')}")
        print(f"    Samples:  {s.get('sample_count', '?')}")
    print(f"\n{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="Session recording")
    sub = parser.add_subparsers(dest="command")

    start_p = sub.add_parser("start", help="Start a recording session")
    start_p.add_argument("--patient-id", required=True)
    start_p.add_argument("--device-id", required=True)
    start_p.add_argument("--label", default="unknown", choices=ACTIVITY_LABELS)
    start_p.add_argument("--hand-placement", default="unknown")
    start_p.add_argument("--shoe-placement", default="unknown")
    start_p.add_argument("--notes", default="")

    stop_p = sub.add_parser("stop", help="Stop a recording session")
    stop_p.add_argument("--session-id", required=True)

    sub.add_parser("list", help="List all sessions")

    args = parser.parse_args()
    if args.command == "start":
        cmd_start(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
