import csv
import logging
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseDatasetAdapter
from .schemas import PADSCanonicalRecord

logger = logging.getLogger(__name__)

class PADSAdapter(BaseDatasetAdapter):
    
    def audit(self) -> Dict[str, Any]:
        timeseries_dir = self.raw_data_dir / "movement" / "timeseries"
        if not timeseries_dir.exists():
            return {"error": "timeseries folder not found in PADS"}
            
        files = list(timeseries_dir.glob("*.txt"))
        
        report = {
            "total_files": len(files),
            "right_wrist_files": 0,
            "left_wrist_files": 0,
            "participants": set(),
            "tasks": set(),
            "total_right_wrist_rows": 0,
            "malformed_rows": 0,
        }
        
        for file_path in files:
            parts = file_path.stem.split("_")
            if len(parts) >= 3:
                participant_id = parts[0]
                task_id = "_".join(parts[1:-1])
                location = parts[-1]
                
                report["participants"].add(participant_id)
                report["tasks"].add(task_id)
                
                if location == "RightWrist":
                    report["right_wrist_files"] += 1
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            vals = line.strip().split(",")
                            if len(vals) == 7:
                                report["total_right_wrist_rows"] += 1
                            else:
                                report["malformed_rows"] += 1
                elif location == "LeftWrist":
                    report["left_wrist_files"] += 1
                    
        report["participants"] = sorted(list(report["participants"]))
        report["tasks"] = sorted(list(report["tasks"]))
        return report
        
    def import_data(self, output_dir: Path) -> None:
        timeseries_dir = self.raw_data_dir / "movement" / "timeseries"
        if not timeseries_dir.exists():
            raise FileNotFoundError("timeseries folder not found in PADS")
            
        output_dir.mkdir(parents=True, exist_ok=True)
        files = list(timeseries_dir.glob("*_RightWrist.txt"))
        
        for file_path in files:
            parts = file_path.stem.split("_")
            if len(parts) < 3:
                continue
                
            participant_id = parts[0]
            task_id = "_".join(parts[1:-1])
            
            out_file = output_dir / f"{file_path.stem}.csv"
            
            with open(file_path, "r", encoding="utf-8") as f_in, \
                 open(out_file, "w", encoding="utf-8", newline="") as f_out:
                 
                writer = csv.writer(f_out)
                # Write header
                header = list(PADSCanonicalRecord.model_fields.keys())
                writer.writerow(header)
                
                for line in f_in:
                    vals = line.strip().split(",")
                    if len(vals) != 7:
                        continue
                        
                    try:
                        timestamp = float(vals[0])
                        ax = float(vals[1])
                        ay = float(vals[2])
                        az = float(vals[3])
                        gx = float(vals[4])
                        gy = float(vals[5])
                        gz = float(vals[6])
                        
                        record = PADSCanonicalRecord(
                            participant_id=participant_id,
                            recording_id=file_path.stem,
                            task_id=task_id,
                            source_file=file_path.name,
                            timestamp=timestamp,
                            right_ax=ax,
                            right_ay=ay,
                            right_az=az,
                            right_gx=gx,
                            right_gy=gy,
                            right_gz=gz
                        )
                        
                        writer.writerow([
                            record.dataset_name,
                            record.dataset_version,
                            record.participant_id,
                            record.recording_id,
                            record.task_id,
                            record.source_file,
                            record.timestamp,
                            record.right_ax,
                            record.right_ay,
                            record.right_az,
                            record.right_gx,
                            record.right_gy,
                            record.right_gz
                        ])
                    except ValueError:
                        pass
