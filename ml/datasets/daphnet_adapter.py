import csv
import logging
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseDatasetAdapter
from .schemas import DaphnetCanonicalRecord

logger = logging.getLogger(__name__)

class DaphnetAdapter(BaseDatasetAdapter):
    
    def audit(self) -> Dict[str, Any]:
        dataset_dir = self.raw_data_dir / "dataset"
        if not dataset_dir.exists():
            return {"error": "dataset folder not found in daphnet"}
            
        files = list(dataset_dir.glob("*.txt"))
        
        report = {
            "total_files": len(files),
            "subjects": set(),
            "recordings": set(),
            "total_rows": 0,
            "annotation_0_count": 0,
            "annotation_1_count": 0,
            "annotation_2_count": 0,
            "malformed_rows": 0,
            "missing_values": 0,
        }
        
        for file_path in files:
            subject_id = file_path.name[:3]
            recording_id = file_path.name[3:6]
            report["subjects"].add(subject_id)
            report["recordings"].add(file_path.name)
            
            with open(file_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f):
                    parts = line.strip().split()
                    if not parts:
                        continue
                    if len(parts) != 11:
                        report["malformed_rows"] += 1
                        continue
                        
                    report["total_rows"] += 1
                    
                    try:
                        annotation = int(parts[10])
                        if annotation == 0:
                            report["annotation_0_count"] += 1
                        elif annotation == 1:
                            report["annotation_1_count"] += 1
                        elif annotation == 2:
                            report["annotation_2_count"] += 1
                    except ValueError:
                        report["missing_values"] += 1
                        
        report["subjects"] = sorted(list(report["subjects"]))
        report["recordings"] = sorted(list(report["recordings"]))
        return report
        
    def import_data(self, output_dir: Path) -> None:
        dataset_dir = self.raw_data_dir / "dataset"
        if not dataset_dir.exists():
            raise FileNotFoundError("dataset folder not found in daphnet")
            
        output_dir.mkdir(parents=True, exist_ok=True)
        files = list(dataset_dir.glob("*.txt"))
        
        for file_path in files:
            subject_id = file_path.name[:3]
            recording_id = file_path.name[3:6]
            
            out_file = output_dir / f"{file_path.stem}.csv"
            
            with open(file_path, "r", encoding="utf-8") as f_in, \
                 open(out_file, "w", encoding="utf-8", newline="") as f_out:
                 
                writer = csv.writer(f_out)
                # Write header
                header = list(DaphnetCanonicalRecord.model_fields.keys())
                writer.writerow(header)
                
                for line in f_in:
                    parts = line.strip().split()
                    if len(parts) != 11:
                        continue
                        
                    try:
                        timestamp = float(parts[0])
                        ankle_ax = float(parts[1])
                        ankle_ay = float(parts[2])
                        ankle_az = float(parts[3])
                        raw_annotation = int(parts[10])
                        
                        if raw_annotation == 0:
                            continue  # Exclude from training candidates
                        
                        fog_label = 1 if raw_annotation == 2 else 0
                        
                        record = DaphnetCanonicalRecord(
                            subject_id=subject_id,
                            recording_id=recording_id,
                            source_file=file_path.name,
                            timestamp=timestamp,
                            ankle_ax=ankle_ax,
                            ankle_ay=ankle_ay,
                            ankle_az=ankle_az,
                            raw_annotation=raw_annotation,
                            fog_label=fog_label
                        )
                        
                        writer.writerow([
                            record.dataset_name,
                            record.dataset_version,
                            record.subject_id,
                            record.recording_id,
                            record.source_file,
                            record.timestamp,
                            record.ankle_ax,
                            record.ankle_ay,
                            record.ankle_az,
                            record.raw_annotation,
                            record.fog_label
                        ])
                    except ValueError:
                        pass
