"""
Live Database Monitor for Parkinson's Monitoring System.

Polls database and shows new records in near real-time.
Useful for watching sensor data arrive as you move sensors.

Usage:
    python tools/watch_sensor_data.py
    python tools/watch_sensor_data.py --interval 1.0
    python tools/watch_sensor_data.py --patient-id P001
"""

import argparse
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from pc_backend.app.database.base import Base, SensorRecord


def get_db_session():
    """Create database session."""
    from pc_backend.app.core.config import settings
    engine = create_engine(settings.DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def watch_records(interval: float = 0.5, patient_id: str = None, device_id: str = None):
    """Poll database and display new records."""
    session = get_db_session()
    last_id = 0

    # Find current max ID
    try:
        max_record = session.query(SensorRecord).order_by(desc(SensorRecord.id)).first()
        if max_record:
            last_id = max_record.id
            print(f"Starting from record #{last_id}. Watching for new records...")
        else:
            print("No records yet. Waiting for data...")
    except Exception as e:
        print(f"Database error: {e}")
        print("Make sure the database exists and backend has been started.")
        session.close()
        return

    print(f"Polling every {interval}s. Press Ctrl+C to stop.\n")

    try:
        while True:
            try:
                query = session.query(SensorRecord).filter(SensorRecord.id > last_id)

                if patient_id:
                    query = query.filter(SensorRecord.patient_id == patient_id)
                if device_id:
                    query = query.filter(SensorRecord.device_id == device_id)

                new_records = query.order_by(SensorRecord.id).all()

                for record in new_records:
                    hand_mag = (record.hand_ax**2 + record.hand_ay**2 + record.hand_az**2)**0.5
                    shoe_mag = (record.shoe_ax**2 + record.shoe_ay**2 + record.shoe_az**2)**0.5

                    print(f"[#{record.id}] seq={record.sequence:5d} | "
                          f"Hand: {hand_mag:5.1f} m/s² | "
                          f"Shoe: {shoe_mag:5.1f} m/s² | "
                          f"t={record.server_received_at_ms}")

                    last_id = record.id

                session.expire_all()
                time.sleep(interval)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped watching.")


def main():
    parser = argparse.ArgumentParser(description="Watch sensor data in real-time")
    parser.add_argument("--interval", type=float, default=0.5, help="Poll interval in seconds (default: 0.5)")
    parser.add_argument("--patient-id", type=str, default=None, help="Filter by patient ID")
    parser.add_argument("--device-id", type=str, default=None, help="Filter by device ID")
    args = parser.parse_args()

    watch_records(args.interval, args.patient_id, args.device_id)


if __name__ == "__main__":
    main()
