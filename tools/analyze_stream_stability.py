"""
Stream Stability Analysis — Measure long-running stream quality.

Usage:
    python tools/analyze_stream_stability.py --minutes 10
    python tools/analyze_stream_stability.py --patient-id P001 --device-id ESP32_001
"""

import argparse
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord
from pc_backend.app.analysis.stream_quality import (
    compute_sampling_metrics,
    detect_sequence_gaps,
    compute_jitter_metrics,
    detect_sessions,
    compute_arrival_offset,
)


def main():
    parser = argparse.ArgumentParser(description="Stream stability analysis")
    parser.add_argument("--patient-id", type=str, default=None)
    parser.add_argument("--device-id", type=str, default=None)
    parser.add_argument("--limit", type=int, default=100000)
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

        declared = dicts[0].get("sampling_rate_hz", 50) if dicts else 50
        sampling = compute_sampling_metrics(dicts, declared)
        gaps = detect_sequence_gaps(dicts)
        jitter_dev = compute_jitter_metrics(dicts, use_server_timestamps=False)
        jitter_srv = compute_jitter_metrics(dicts, use_server_timestamps=True)
        offset = compute_arrival_offset(dicts)
        sessions = detect_sessions(dicts)

        print(f"\n{'='*60}")
        print(f"  Stream Stability Analysis")
        print(f"{'='*60}")
        print(f"\n  STREAM:")
        print(f"    Records:            {sampling.record_count:,}")
        print(f"    Duration:           {sampling.duration_ms/1000:.1f}s ({sampling.duration_ms/60000:.1f} min)")
        print(f"    Declared rate:      {sampling.declared_rate_hz} Hz")
        print(f"    Observed rate:      {sampling.observed_device_rate_hz} Hz (device)")
        print(f"    Mean interval:      {sampling.mean_interval_ms:.2f} ms")
        print(f"    Median interval:    {sampling.median_interval_ms:.2f} ms")
        print(f"    Std interval:       {sampling.std_interval_ms:.2f} ms")
        print(f"    P95 interval:       {sampling.p95_interval_ms:.2f} ms")
        print(f"    P99 interval:       {sampling.p99_interval_ms:.2f} ms")

        print(f"\n  SEQUENCE:")
        print(f"    First:              {gaps.first_sequence}")
        print(f"    Last:               {gaps.last_sequence}")
        print(f"    Expected:           {gaps.expected_count}")
        print(f"    Received:           {gaps.received_count}")
        print(f"    Missing:            {gaps.missing_count}")
        print(f"    Duplicates:         {gaps.duplicate_count}")
        print(f"    Out-of-order:       {gaps.out_of_order_count}")
        print(f"    Est. packet loss:   {gaps.estimated_loss_pct:.4f}%")
        print(f"    Reset detected:     {gaps.reset_detected}")

        print(f"\n  DEVICE JITTER:")
        print(f"    Mean:               {jitter_dev.mean_delta_ms:.2f} ms")
        print(f"    Std:                {jitter_dev.std_delta_ms:.2f} ms")
        print(f"    Min:                {jitter_dev.min_delta_ms:.2f} ms")
        print(f"    Max:                {jitter_dev.max_delta_ms:.2f} ms")
        print(f"    P95:                {jitter_dev.p95_delta_ms:.2f} ms")
        print(f"    P99:                {jitter_dev.p99_delta_ms:.2f} ms")
        print(f"    MAD:                {jitter_dev.mean_absolute_deviation_ms:.2f} ms")

        print(f"\n  SERVER JITTER:")
        print(f"    Mean:               {jitter_srv.mean_delta_ms:.2f} ms")
        print(f"    Std:                {jitter_srv.std_delta_ms:.2f} ms")

        print(f"\n  DEVICE-SERVER OFFSET:")
        print(f"    Mean:               {offset['mean_ms']:.2f} ms")
        print(f"    Std:                {offset['std_ms']:.2f} ms")
        print(f"    Note:               Includes clock offset + network + processing")

        print(f"\n  SESSIONS DETECTED:  {len(sessions)}")
        for i, s in enumerate(sessions[:10]):
            dur = (s.end_timestamp_ms - s.start_timestamp_ms) / 1000.0
            print(f"    Session {i+1}: {s.record_count} records, {dur:.1f}s, reason={s.reason}")

        print(f"\n{'='*60}\n")

    finally:
        session.close()


if __name__ == "__main__":
    main()
