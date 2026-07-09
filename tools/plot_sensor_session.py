"""
Offline Session Plot — Generate plots from stored records.

Usage:
    python tools/plot_sensor_session.py --patient-id P001 --device-id ESP32_001
    python tools/plot_sensor_session.py --limit 1000 --output plots/
    python tools/plot_sensor_session.py --mode all --save
"""

import argparse
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord


def main():
    parser = argparse.ArgumentParser(description="Offline session plot")
    parser.add_argument("--patient-id", type=str, default=None)
    parser.add_argument("--device-id", type=str, default=None)
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--mode", choices=["hand_accel", "hand_gyro", "shoe_accel", "shoe_gyro", "magnitudes", "all"], default="all")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--output", type=str, default="data/plots")
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

        print(f"Loaded {len(records)} records")

        timestamps = [r.timestamp_ms / 1000.0 for r in records]
        t0 = timestamps[0]
        times = [t - t0 for t in timestamps]

        plots = []
        if args.mode in ("hand_accel", "all"):
            plots.append(("Hand Acceleration", "hand_ax,hand_ay,hand_az",
                          ["AX", "AY", "AZ"], "m/s²"))
        if args.mode in ("hand_gyro", "all"):
            plots.append(("Hand Gyroscope", "hand_gx,hand_gy,hand_gz",
                          ["GX", "GY", "GZ"], "deg/s"))
        if args.mode in ("shoe_accel", "all"):
            plots.append(("Shoe Acceleration", "shoe_ax,shoe_ay,shoe_az",
                          ["AX", "AY", "AZ"], "m/s²"))
        if args.mode in ("shoe_gyro", "all"):
            plots.append(("Shoe Gyroscope", "shoe_gx,shoe_gy,shoe_gz",
                          ["GX", "GY", "GZ"], "deg/s"))
        if args.mode in ("magnitudes", "all"):
            h_mag = [(r.hand_ax**2 + r.hand_ay**2 + r.hand_az**2)**0.5 for r in records]
            s_mag = [(r.shoe_ax**2 + r.shoe_ay**2 + r.shoe_az**2)**0.5 for r in records]
            plots.append(("Magnitudes", None, None, None, custom_data=("Hand Mag", "Shoe Mag"), custom_values=(h_mag, s_mag)))

        fig, axes = plt.subplots(len(plots), 1, figsize=(14, 3 * len(plots)), squeeze=False)
        fig.canvas.manager.set_window_title("Session Plot")

        for idx, (title, fields_str, labels, unit, *rest) in enumerate(plots):
            ax = axes[idx][0]
            if rest and rest[0].get("custom_data"):
                vals = rest[0]
                ax.plot(times, vals["custom_values"][0], linewidth=0.8, label=vals["custom_data"][0])
                ax.plot(times, vals["custom_values"][1], linewidth=0.8, label=vals["custom_data"][1])
                ax.set_ylabel("Magnitude")
            else:
                fields = fields_str.split(",")
                colors = ["#2196F3", "#FF9800", "#4CAF50"]
                for i, field in enumerate(fields):
                    vals = [getattr(r, field) for r in records]
                    ax.plot(times, vals, color=colors[i], linewidth=0.8, label=labels[i])
                ax.set_ylabel(unit)

            ax.set_title(title)
            ax.legend(loc="upper right")
            ax.grid(True, alpha=0.3)

        axes[-1][0].set_xlabel("Time (seconds)")
        plt.tight_layout()

        if args.save:
            os.makedirs(args.output, exist_ok=True)
            path = os.path.join(args.output, f"session_{args.patient_id}_{args.device_id}.png")
            plt.savefig(path, dpi=150)
            print(f"Saved: {path}")

        plt.show()

    finally:
        session.close()


if __name__ == "__main__":
    main()
