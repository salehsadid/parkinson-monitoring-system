"""
Live Signal Plot — Real-time matplotlib visualization of sensor streams.

Usage:
    python tools/live_signal_plot.py
    python tools/live_signal_plot.py --mode hand_accel
    python tools/live_signal_plot.py --mode magnitudes --window 60
    python tools/live_signal_plot.py --patient-id P001 --device-id ESP32_001
"""

import argparse
import os
import sys
import time
from collections import deque

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord

MODES = {
    "hand_accel": (["hand_ax", "hand_ay", "hand_az"], "Hand Acceleration (m/s²)", ["AX", "AY", "AZ"]),
    "hand_gyro": (["hand_gx", "hand_gy", "hand_gz"], "Hand Gyroscope (deg/s)", ["GX", "GY", "GZ"]),
    "shoe_accel": (["shoe_ax", "shoe_ay", "shoe_az"], "Shoe Acceleration (m/s²)", ["AX", "AY", "AZ"]),
    "shoe_gyro": (["shoe_gx", "shoe_gy", "shoe_gz"], "Shoe Gyroscope (deg/s)", ["GX", "GY", "GZ"]),
    "magnitudes": (None, "Signal Magnitudes", None),
}

MAG_FIELDS = {
    "hand_accel": "hand_ax,hand_ay,hand_az",
    "hand_gyro": "hand_gx,hand_gy,hand_gz",
    "shoe_accel": "shoe_ax,shoe_ay,shoe_az",
    "shoe_gyro": "shoe_gx,shoe_gy,shoe_gz",
}


def compute_magnitude(row, prefix):
    ax = getattr(row, f"{prefix}_ax")
    ay = getattr(row, f"{prefix}_ay")
    az = getattr(row, f"{prefix}_az")
    return (ax ** 2 + ay ** 2 + az ** 2) ** 0.5


def main():
    parser = argparse.ArgumentParser(description="Live signal plot")
    parser.add_argument("--mode", choices=list(MODES.keys()), default="hand_accel")
    parser.add_argument("--window", type=int, default=30, help="Rolling window seconds")
    parser.add_argument("--refresh", type=float, default=0.2, help="Refresh interval seconds")
    parser.add_argument("--patient-id", type=str, default=None)
    parser.add_argument("--device-id", type=str, default=None)
    parser.add_argument("--max-rows", type=int, default=5000, help="Max rows to query")
    args = parser.parse_args()

    engine = create_engine(settings.DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.canvas.manager.set_window_title(f"Live Signal — {args.mode}")

    data_buffers = {i: deque(maxlen=2000) for i in range(3)}
    time_buffer = deque(maxlen=2000)
    last_id = [0]
    start_time = [time.time()]

    def update(frame):
        session = Session()
        try:
            query = session.query(SensorRecord).filter(SensorRecord.id > last_id[0])
            if args.patient_id:
                query = query.filter(SensorRecord.patient_id == args.patient_id)
            if args.device_id:
                query = query.filter(SensorRecord.device_id == args.device_id)

            rows = query.order_by(SensorRecord.id.asc()).limit(args.max_rows).all()

            if rows:
                for row in rows:
                    t = row.timestamp_ms / 1000.0
                    time_buffer.append(t)

                    if args.mode == "magnitudes":
                        for i, prefix in enumerate(["hand", "shoe"]):
                            mag = compute_magnitude(row, prefix)
                            data_buffers[i].append(mag)
                        data_buffers[2].clear()
                    else:
                        fields, _, _ = MODES[args.mode]
                        for i, field in enumerate(fields):
                            data_buffers[i].append(getattr(row, field))

                    last_id[0] = row.id

            ax.clear()
            colors = ["#2196F3", "#FF9800", "#4CAF50"]

            if args.mode == "magnitudes":
                labels = ["Hand Mag", "Shoe Mag"]
            else:
                _, title, labels = MODES[args.mode]
                labels = labels

            for i in range(3):
                if data_buffers[i]:
                    ax.plot(list(data_buffers[i]), color=colors[i],
                            linewidth=1, label=labels[i] if i < len(labels) else "")

            ax.set_title(f"Live Signal — {args.mode}")
            ax.set_xlabel("Samples")
            ax.legend(loc="upper right")
            ax.grid(True, alpha=0.3)

        finally:
            session.close()

    ani = FuncAnimation(fig, update, interval=args.refresh * 1000, cache_frame_data=False)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
