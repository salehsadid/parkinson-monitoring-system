"""
CSV Export — Export sensor records to CSV.

Usage:
    python tools/export_sensor_session.py --patient-id P001 --device-id ESP32_001 --output data/raw/session.csv
    python tools/export_sensor_session.py --limit 5000 --output data/raw/recent.csv
"""

import argparse
import csv
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord

CSV_COLUMNS = [
    "id", "patient_id", "device_id", "sequence",
    "timestamp_ms", "server_received_at_ms", "sampling_rate_hz",
    "hand_ax", "hand_ay", "hand_az", "hand_gx", "hand_gy", "hand_gz",
    "shoe_ax", "shoe_ay", "shoe_az", "shoe_gx", "shoe_gy", "shoe_gz",
    "created_at",
]


def main():
    parser = argparse.ArgumentParser(description="Export sensor data to CSV")
    parser.add_argument("--patient-id", type=str, default=None)
    parser.add_argument("--device-id", type=str, default=None)
    parser.add_argument("--limit", type=int, default=10000)
    parser.add_argument("--output", type=str, default="data/raw/export.csv")
    args = parser.parse_args()

    engine = create_engine(settings.DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        query = session.query(SensorRecord)
        if args.patient_id:
            query = query.filter(SensorRecord.patient_id == args.patient_id)
        if args.device_id:
            query = query.filter(SensorRecord.device_id == args.device_id)

        records = query.order_by(SensorRecord.id.asc()).limit(args.limit).all()

        if not records:
            print("No records found.")
            return

        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

        with open(args.output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)

            for r in records:
                writer.writerow([
                    r.id, r.patient_id, r.device_id, r.sequence,
                    r.timestamp_ms, r.server_received_at_ms, r.sampling_rate_hz,
                    r.hand_ax, r.hand_ay, r.hand_az, r.hand_gx, r.hand_gy, r.hand_gz,
                    r.shoe_ax, r.shoe_ay, r.shoe_az, r.shoe_gx, r.shoe_gy, r.shoe_gz,
                    r.created_at,
                ])

        print(f"Exported {len(records)} records to {args.output}")
        print(f"Columns: {len(CSV_COLUMNS)} (including all 12 IMU channels)")

    finally:
        session.close()


if __name__ == "__main__":
    main()
