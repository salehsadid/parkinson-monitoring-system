"""
Database Growth Analysis — Measure and project storage requirements.

Usage:
    python tools/analyze_database_growth.py
    python tools/analyze_database_growth.py --patient-id P001
"""

import argparse
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord
from pc_backend.app.analysis.storage_analysis import analyze_storage, format_bytes


def main():
    parser = argparse.ArgumentParser(description="Database growth analysis")
    parser.add_argument("--patient-id", type=str, default=None)
    parser.add_argument("--device-id", type=str, default=None)
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

        total_rows = query.count()

        if total_rows == 0:
            print("No records found.")
            return

        oldest = query.order_by(SensorRecord.timestamp_ms.asc()).first()
        newest = query.order_by(SensorRecord.timestamp_ms.desc()).first()

        duration_ms = newest.timestamp_ms - oldest.timestamp_ms
        duration_sec = duration_ms / 1000.0

        db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("./", "")
        db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0

        declared_rate = session.query(SensorRecord.sampling_rate_hz).first()
        rate = declared_rate[0] if declared_rate else 50

        analysis = analyze_storage(total_rows, db_size, duration_sec, rate)

        print(f"\n{'='*60}")
        print(f"  Database Growth Analysis")
        print(f"{'='*60}")
        print(f"\n  MEASURED:")
        print(f"    Total rows:         {analysis.total_rows:,}")
        print(f"    Database size:      {format_bytes(analysis.database_size_bytes)}")
        print(f"    Avg bytes/row:      {analysis.avg_bytes_per_row:.1f}")
        print(f"    Duration:           {analysis.measured_duration_seconds:.1f}s ({analysis.measured_duration_seconds/60:.1f} min)")
        print(f"    Rows/second:        {analysis.rows_per_second:.2f}")
        print(f"    Rows/minute:        {analysis.rows_per_minute:.0f}")
        print(f"    Rows/hour:          {analysis.rows_per_hour:.0f}")
        print(f"\n  PROJECTED (at {analysis.declared_rate_hz} Hz):")
        print(f"    Rows/day:           {analysis.projected_rows_per_day:,.0f}")
        print(f"    Rows/72 hours:      {analysis.projected_rows_per_72h:,.0f}")
        print(f"    Size/day:           {format_bytes(analysis.projected_size_per_day_bytes)}")
        print(f"    Size/72 hours:      {format_bytes(analysis.projected_size_per_72h_bytes)}")
        print(f"\n  72-HOUR STORAGE FEASIBILITY:")
        if analysis.projected_size_per_72h_bytes < 500 * 1024 * 1024:
            print(f"    Status: FEASIBLE (projected < 500 MB)")
        elif analysis.projected_size_per_72h_bytes < 2 * 1024 * 1024 * 1024:
            print(f"    Status: MANAGEABLE (projected < 2 GB)")
        else:
            print(f"    Status: LARGE (projected > 2 GB, consider downsampling)")
        print(f"{'='*60}\n")

    finally:
        session.close()


if __name__ == "__main__":
    main()
