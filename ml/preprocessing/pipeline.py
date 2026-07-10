import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
from scipy import signal
from scipy.interpolate import interp1d
from sklearn.preprocessing import StandardScaler

from .config import FOGPreprocessingConfig

logger = logging.getLogger(__name__)

class FOGPreprocessingPipeline:
    def __init__(self, config: FOGPreprocessingConfig):
        self.config = config
        
    def run(self, input_dir: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Executes the full preprocessing pipeline.
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        csv_files = list(input_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {input_dir}")
            
        all_windows = []
        all_labels = []
        all_metadata = []
        
        for file_path in csv_files:
            logger.info(f"Processing {file_path.name}...")
            
            # Step 1: Input Validation
            df = pd.read_csv(file_path)
            required_cols = ["subject_id", "recording_id", "timestamp", "ankle_ax", "ankle_ay", "ankle_az", "fog_label"]
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing required column {col} in {file_path.name}")
                    
            if df[required_cols].isna().any().any():
                logger.warning(f"Dropping rows with NaN in {file_path.name}")
                df = df.dropna(subset=required_cols)
                
            if len(df) == 0:
                continue
                
            subject_id = str(df["subject_id"].iloc[0])
            recording_id = str(df["recording_id"].iloc[0])
            
            # Verify binary fog_labels
            unique_labels = df["fog_label"].unique()
            if not set(unique_labels).issubset({0, 1}):
                raise ValueError(f"Invalid fog_label values found: {unique_labels}")
                
            # Step 2: Unit Conversion (milli-g to m/s^2)
            accel_cols = ["ankle_ax", "ankle_ay", "ankle_az"]
            data_accel = df[accel_cols].values * 0.00980665
            labels = df["fog_label"].values
            timestamps = df["timestamp"].values
            
            # Step 3: Resampling (64Hz to 50Hz)
            # Use interpolate for precise resampling based on original rate
            original_duration = len(data_accel) / self.config.original_sampling_rate_hz
            num_target_samples = int(original_duration * self.config.target_sampling_rate_hz)
            
            # Continuous data interpolation
            orig_time = np.linspace(0, original_duration, len(data_accel))
            target_time = np.linspace(0, original_duration, num_target_samples)
            
            interpolator = interp1d(orig_time, data_accel, axis=0, kind='linear', fill_value="extrapolate")
            resampled_accel = interpolator(target_time)
            
            # Categorical label interpolation (nearest neighbor)
            label_interpolator = interp1d(orig_time, labels, kind='nearest', fill_value="extrapolate")
            resampled_labels = label_interpolator(target_time).astype(int)
            
            # Step 4: Filtering
            if self.config.filter_mode == "offline_zero_phase":
                nyq = 0.5 * self.config.target_sampling_rate_hz
                normal_cutoff = self.config.filter_cutoff_hz / nyq
                b, a = signal.butter(self.config.filter_order, normal_cutoff, btype='low', analog=False)
                resampled_accel = signal.filtfilt(b, a, resampled_accel, axis=0)
            elif self.config.filter_mode == "causal":
                nyq = 0.5 * self.config.target_sampling_rate_hz
                normal_cutoff = self.config.filter_cutoff_hz / nyq
                sos = signal.butter(self.config.filter_order, normal_cutoff, btype='low', analog=False, output='sos')
                
                # Initialize state to minimize startup transients using the first sample
                zi = signal.sosfilt_zi(sos)
                
                filtered_accel = np.zeros_like(resampled_accel)
                for i in range(resampled_accel.shape[1]):
                    # Scale zi by the first data point of the channel
                    zi_scaled = zi * resampled_accel[0, i]
                    filtered_accel[:, i], _ = signal.sosfilt(sos, resampled_accel[:, i], zi=zi_scaled)
                    
                resampled_accel = filtered_accel
            elif self.config.filter_mode == "none":
                pass
            else:
                raise ValueError(f"Unknown filter_mode: {self.config.filter_mode}")
                
            # Step 5: Windowing & Labeling
            ws = self.config.window_samples
            stride = self.config.stride_samples
            
            for start_idx in range(0, len(resampled_accel) - ws + 1, stride):
                end_idx = start_idx + ws
                window_data = resampled_accel[start_idx:end_idx]
                window_labels = resampled_labels[start_idx:end_idx]
                
                fog_fraction = np.sum(window_labels) / ws
                final_label = 1 if fog_fraction >= self.config.fog_fraction_threshold else 0
                
                all_windows.append(window_data)
                all_labels.append(final_label)
                all_metadata.append({
                    "subject_id": subject_id,
                    "recording_id": recording_id,
                    "window_index": len(all_metadata),
                    "fog_fraction": float(fog_fraction),
                    "label": int(final_label)
                })
                
        # Stack everything
        X = np.array(all_windows)
        y = np.array(all_labels)
        df_meta = pd.DataFrame(all_metadata)
        
        # Step 6: Subject-wise Splitting
        train_mask = df_meta["subject_id"].isin(self.config.train_subjects)
        val_mask = df_meta["subject_id"].isin(self.config.val_subjects)
        test_mask = df_meta["subject_id"].isin(self.config.test_subjects)
        
        X_train, y_train = X[train_mask], y[train_mask]
        X_val, y_val = X[val_mask], y[val_mask]
        X_test, y_test = X[test_mask], y[test_mask]
        
        # Verify no overlap
        assert len(set(self.config.train_subjects).intersection(self.config.val_subjects)) == 0
        assert len(set(self.config.train_subjects).intersection(self.config.test_subjects)) == 0
        
        # Step 7: Normalization
        scaler = StandardScaler()
        # Fit on train data reshaped to 2D
        X_train_flat = X_train.reshape(-1, X_train.shape[-1])
        scaler.fit(X_train_flat)
        
        # Apply to all
        X_train = scaler.transform(X_train_flat).reshape(X_train.shape)
        if len(X_val) > 0:
            X_val = scaler.transform(X_val.reshape(-1, X_val.shape[-1])).reshape(X_val.shape)
        if len(X_test) > 0:
            X_test = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)
            
        # Step 8: Save Outputs
        np.save(output_dir / "X_train.npy", X_train)
        np.save(output_dir / "y_train.npy", y_train)
        np.save(output_dir / "X_val.npy", X_val)
        np.save(output_dir / "y_val.npy", y_val)
        np.save(output_dir / "X_test.npy", X_test)
        np.save(output_dir / "y_test.npy", y_test)
        
        df_meta.to_csv(output_dir / "window_metadata.csv", index=False)
        
        scaler_data = {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist()
        }
        with open(output_dir / "scaler.json", "w") as f:
            json.dump(scaler_data, f, indent=2)
            
        with open(output_dir / "preprocessing_config.json", "w") as f:
            json.dump(self.config.model_dump(), f, indent=2)
            
        # Compile Report
        report = {
            "total_windows": len(X),
            "train": {
                "windows": len(X_train),
                "fog_count": int(np.sum(y_train)),
                "no_fog_count": int(len(y_train) - np.sum(y_train)),
                "subjects": self.config.train_subjects
            },
            "val": {
                "windows": len(X_val),
                "fog_count": int(np.sum(y_val)),
                "no_fog_count": int(len(y_val) - np.sum(y_val)),
                "subjects": self.config.val_subjects
            },
            "test": {
                "windows": len(X_test),
                "fog_count": int(np.sum(y_test)),
                "no_fog_count": int(len(y_test) - np.sum(y_test)),
                "subjects": self.config.test_subjects
            }
        }
        
        # Calculate class weight recommendation for train
        if report["train"]["fog_count"] > 0:
            weight_0 = 1.0
            weight_1 = report["train"]["no_fog_count"] / report["train"]["fog_count"]
            report["recommended_class_weights"] = {
                "0": weight_0,
                "1": weight_1
            }
        
        with open(output_dir / "manifest.json", "w") as f:
            json.dump(report, f, indent=2)
            
        return report
