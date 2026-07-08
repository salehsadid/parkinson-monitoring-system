"""
Database Inspection Tool for Parkinson's Monitoring System.

Displays stored sensor readings from SQLite database.
Useful for verifying real hardware data.

Usage:
    python tools/inspect_sensor_data.py
    python tools/inspect_sensor_data.py --limit 20
    python tools/inspect_sensor_data.py --patient-id P001
    python tools/inspect_sensor_data.py --device-id ESP32_001
"""

import argparse
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from pc_backend.app.database.base import Base, SensorRecord


def get_db_session():
    """Create database session using project configuration."""
    from pc_backend.app.core.config import settings
    engine = create_engine(settings.DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def inspect_records(limit: int = 10, patient_id: str = None, device_id: str = None):
    """Query and display sensor records."""
    session = get_db_session()

    try:
        query = session.query(SensorRecord)

        if patient_id:
            query = query.filter(SensorRecord.patient_id == patient_id)
        if device_id:
            query = query.filter(SensorRecord.device_id == device_id)

        records = query.order_by(desc(SensorRecord.id)).limit(limit).all()

        if not records:
            print("No records found.")
            return

        print(f"\n{'='*80}")
        print(f"  Sensor Records (showing {len(records)} of {query.count()})")
        print(f"{'='*80}\n")

        for record in reversed(records):
            print(f"--- Record #{record.id} ---")
            print(f"  Patient:     {record.patient_id}")
            print(f"  Device:      {record.device_id}")
            print(f"  Sequence:    {record.sequence}")
            print(f"  Device time: {record.timestamp_ms}")
            print(f"  Server time: {record.server_received_at_ms}")
            print(f"  Created at:  {record.created_at}")
            print(f"  Sample rate: {record.sampling_rate_hz} Hz")
            print()
            print(f"  HAND:")
            print(f"    AX={record.hand_ax:+.2f}  AY={record.hand_ay:+.2f}  AZ={record.hand_az:+.2f} m/s²")
            print(f"    GX={record.hand_gx:+.2f}  GY={record.hand_gy:+.2f}  GZ={record.hand_gz:+.2f} deg/s")
            print()
            print(f"  SHOE:")
            print(f"    AX={record.shoe_ax:+.2f}  AY={record.shoe_ay:+.2f}  AZ={record.shoe_az:+.2f} m/s²")
            print(f"    GX={record.shoe_gx:+.2f}  GY={record.shoe_gy:+.2f}  GZ={record.shoe_gz:+.2f} deg/s")
            print()

        print(f"{'='*80}\n")

    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Inspect stored sensor readings")
    parser.add_argument("--limit", type=int, default=10, help="Number of records to show (default: 10)")
    parser.add_argument("--patient-id", type=str, default=None, help="Filter by patient ID")
    parser.add_argument("--device-id", type=str, default=None, help="Filter by device ID")
    args = parser.parse_args()

    inspect_records(args.limit, args.patient_id, args.device_id)


if __name__ == "__main__":
    main()
