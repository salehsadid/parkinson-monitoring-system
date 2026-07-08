"""
Database Count Tool for Parkinson's Monitoring System.

Shows record counts and basic statistics.

Usage:
    python tools/count_sensor_records.py
    python tools/count_sensor_records.py --patient-id P001
"""

import argparse
import os
import sys
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from pc_backend.app.database.base import Base, SensorRecord, Patient, Device


def get_db_session():
    """Create database session."""
    from pc_backend.app.core.config import settings
    engine = create_engine(settings.DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def show_stats(patient_id: str = None, device_id: str = None):
    """Display database statistics."""
    session = get_db_session()

    try:
        query = session.query(SensorRecord)

        if patient_id:
            query = query.filter(SensorRecord.patient_id == patient_id)
        if device_id:
            query = query.filter(SensorRecord.device_id == device_id)

        total = query.count()

        if total == 0:
            print("No sensor records found.")
            return

        oldest = query.order_by(SensorRecord.id.asc()).first()
        newest = query.order_by(SensorRecord.id.desc()).first()

        print(f"\n{'='*50}")
        print(f"  Sensor Record Statistics")
        print(f"{'='*50}")

        if patient_id:
            print(f"  Patient:      {patient_id}")
        else:
            print(f"  Patient:      ALL")

        if device_id:
            print(f"  Device:       {device_id}")
        else:
            print(f"  Device:       ALL")

        print(f"  Total records: {total}")
        print()

        if oldest:
            print(f"  Oldest record:")
            print(f"    ID:           {oldest.id}")
            print(f"    Sequence:     {oldest.sequence}")
            print(f"    Device time:  {oldest.timestamp_ms}")
            print(f"    Server time:  {oldest.server_received_at_ms}")
            print(f"    Created at:   {oldest.created_at}")

        if newest:
            print(f"  Newest record:")
            print(f"    ID:           {newest.id}")
            print(f"    Sequence:     {newest.sequence}")
            print(f"    Device time:  {newest.timestamp_ms}")
            print(f"    Server time:  {newest.server_received_at_ms}")
            print(f"    Created at:   {newest.created_at}")

        if oldest and newest and oldest.id != newest.id:
            time_span = newest.server_received_at_ms - oldest.server_received_at_ms
            print(f"\n  Time span:     {time_span/1000:.1f} seconds")

        print(f"{'='*50}\n")

    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Show sensor record statistics")
    parser.add_argument("--patient-id", type=str, default=None, help="Filter by patient ID")
    parser.add_argument("--device-id", type=str, default=None, help="Filter by device ID")
    args = parser.parse_args()

    show_stats(args.patient_id, args.device_id)


if __name__ == "__main__":
    main()
