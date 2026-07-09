"""
Data Quality Report — Comprehensive stream quality assessment.

Usage:
    python tools/generate_data_quality_report.py
    python tools/generate_data_quality_report.py --patient-id P001 --device-id ESP32_001
    python tools/generate_data_quality_report.py --output report.json
"""

import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord
from pc_backend.app.analysis.stream_quality import (
    compute_sampling_metrics, detect_sequence_gaps,
    compute_jitter_metrics, detect_sessions, compute_arrival_offset,
)
from pc_backend.app.analysis.signal_quality import compute_signal_quality
from pc_backend.app.analysis.storage_analysis import analyze_storage, format_bytes


def main():
    parser = argparse.ArgumentParser(description="Generate data quality report")
    parser.add_argument("--patient-id", type=str, default=None)
    parser.add_argument("--device-id", type=str, default=None)
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--output", type=str, default=None, help="JSON output path")
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

        dicts = [{
            "sequence": r.sequence,
            "timestamp_ms": r.timestamp_ms,
            "server_received_at_ms": r.server_received_at_ms,
            "hand_ax": r.hand_ax, "hand_ay": r.hand_ay, "hand_az": r.hand_az,
            "hand_gx": r.hand_gx, "hand_gy": r.hand_gy, "hand_gz": r.hand_gz,
            "shoe_ax": r.shoe_ax, "shoe_ay": r.shoe_ay, "shoe_az": r.shoe_az,
            "shoe_gx": r.shoe_gx, "shoe_gy": r.shoe_gy, "shoe_gz": r.shoe_gz,
        } for r in records]

        sampling = compute_sampling_metrics(dicts)
        gaps = detect_sequence_gaps(dicts)
        jitter = compute_jitter_metrics(dicts)
        offset = compute_arrival_offset(dicts)
        signal = compute_signal_quality(dicts)
        sessions = detect_sessions(dicts)

        duration_sec = sampling.duration_ms / 1000.0
        db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("./", "")
        db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        total_rows = query.count()
        storage = analyze_storage(total_rows, db_size, duration_sec)

        report = {
            "stream": {
                "records": sampling.record_count,
                "duration_seconds": round(duration_sec, 2),
                "declared_rate_hz": sampling.declared_rate_hz,
                "observed_rate_hz": sampling.observed_device_rate_hz,
                "mean_interval_ms": sampling.mean_interval_ms,
                "std_interval_ms": sampling.std_interval_ms,
            },
            "sequence": {
                "first": gaps.first_sequence,
                "last": gaps.last_sequence,
                "received": gaps.received_count,
                "expected": gaps.expected_count,
                "missing": gaps.missing_count,
                "duplicates": gaps.duplicate_count,
                "out_of_order": gaps.out_of_order_count,
                "loss_pct": gaps.estimated_loss_pct,
                "reset_detected": gaps.reset_detected,
            },
            "jitter": {
                "device_mean_ms": jitter.mean_delta_ms,
                "device_std_ms": jitter.std_delta_ms,
                "device_p95_ms": jitter.p95_delta_ms,
                "device_p99_ms": jitter.p99_delta_ms,
                "device_mad_ms": jitter.mean_absolute_deviation_ms,
            },
            "offset": offset,
            "signal": {
                "hand_accel_magnitude_mean": signal.hand_accel_magnitude.mean,
                "hand_accel_magnitude_std": signal.hand_accel_magnitude.std,
                "shoe_accel_magnitude_mean": signal.shoe_accel_magnitude.mean,
                "shoe_accel_magnitude_std": signal.shoe_accel_magnitude.std,
                "hand_energy": signal.hand_movement_energy,
                "shoe_energy": signal.shoe_movement_energy,
            },
            "storage": {
                "total_rows": storage.total_rows,
                "database_size": format_bytes(storage.database_size_bytes),
                "avg_bytes_per_row": storage.avg_bytes_per_row,
                "rows_per_second": storage.rows_per_second,
                "projected_per_72h": format_bytes(storage.projected_size_per_72h_bytes),
            },
            "sessions": len(sessions),
        }

        print(f"\n{'='*60}")
        print(f"  DATA QUALITY REPORT")
        print(f"{'='*60}")
        print(f"\n  STREAM: {report['stream']['records']} records, {report['stream']['duration_seconds']}s")
        print(f"    Observed rate: {report['stream']['observed_rate_hz']} Hz")
        print(f"    Mean interval: {report['stream']['mean_interval_ms']} ms")

        print(f"\n  SEQUENCE: loss={report['sequence']['loss_pct']}%, "
              f"missing={report['sequence']['missing']}, "
              f"duplicates={report['sequence']['duplicates']}")

        print(f"\n  JITTER: mean={report['jitter']['device_mean_ms']}ms, "
              f"std={report['jitter']['device_std_ms']}ms, "
              f"P95={report['jitter']['device_p95_ms']}ms")

        print(f"\n  SIGNAL: hand_mag={report['signal']['hand_accel_magnitude_mean']:.2f}, "
              f"shoe_mag={report['signal']['shoe_accel_magnitude_mean']:.2f}")

        print(f"\n  STORAGE: {report['storage']['database_size']}, "
              f"72h projected: {report['storage']['projected_per_72h']}")

        print(f"{'='*60}\n")

        if args.output:
            os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"Report saved: {args.output}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
