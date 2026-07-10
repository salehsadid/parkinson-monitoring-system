import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import signal
from ml.preprocessing import FOGPreprocessingConfig, FOGPreprocessingPipeline

@pytest.fixture
def mock_daphnet_csv(tmp_path):
    interim_dir = tmp_path / "interim"
    interim_dir.mkdir(parents=True)
    
    # Create mock CSV for Subject S01, Recording R01
    file_path = interim_dir / "S01R01.csv"
    
    # 64Hz for 4 seconds = 256 samples
    n_samples = 256
    timestamps = np.linspace(0, 4000, n_samples)
    
    # Create alternating FOG labels (0 for first 2 seconds, 1 for next 2 seconds)
    labels = np.zeros(n_samples)
    labels[128:] = 1
    
    df = pd.DataFrame({
        "dataset_name": ["Daphnet"] * n_samples,
        "dataset_version": ["1.0"] * n_samples,
        "subject_id": ["S01"] * n_samples,
        "recording_id": ["R01"] * n_samples,
        "source_file": ["S01R01.txt"] * n_samples,
        "timestamp": timestamps,
        "ankle_ax": np.random.randn(n_samples) * 1000, # milli-g
        "ankle_ay": np.random.randn(n_samples) * 1000,
        "ankle_az": np.random.randn(n_samples) * 1000,
        "raw_annotation": labels + 1,
        "fog_label": labels
    })
    
    df.to_csv(file_path, index=False)
    
    # Create a second subject S07
    file_path2 = interim_dir / "S07R01.csv"
    df["subject_id"] = "S07"
    df.to_csv(file_path2, index=False)
    
    return interim_dir

@pytest.mark.parametrize("mode", ["none", "causal", "offline_zero_phase"])
def test_preprocessing_pipeline_modes(mock_daphnet_csv, tmp_path, mode):
    output_dir = tmp_path / f"processed_{mode}"
    
    config = FOGPreprocessingConfig(
        filter_mode=mode,
        target_sampling_rate_hz=50.0,
        window_size_seconds=2.0,
        overlap_fraction=0.5,
        fog_fraction_threshold=0.5,
        train_subjects=["S01"],
        val_subjects=["S07"],
        test_subjects=[]
    )
    
    pipeline = FOGPreprocessingPipeline(config)
    report = pipeline.run(mock_daphnet_csv, output_dir)
    
    # Assert output files exist
    assert (output_dir / "X_train.npy").exists()
    assert (output_dir / "y_train.npy").exists()
    assert (output_dir / "X_val.npy").exists()
    assert (output_dir / "y_val.npy").exists()
    assert (output_dir / "scaler.json").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "window_metadata.csv").exists()
    assert (output_dir / "preprocessing_config.json").exists()
    
    # Verify Window Shapes
    X_train = np.load(output_dir / "X_train.npy")
    y_train = np.load(output_dir / "y_train.npy")
    
    assert X_train.shape == (3, 100, 3)
    assert y_train.shape == (3,)
    assert not np.isnan(X_train).any()
    
    # Verify leakage prevention
    df_meta = pd.read_csv(output_dir / "window_metadata.csv")
    assert len(df_meta[df_meta["subject_id"] == "S01"]) == 3
    assert len(df_meta[df_meta["subject_id"] == "S07"]) == 3
    
    # Verify categorical labels
    assert y_train[0] == 0
    assert y_train[1] == 1
    assert y_train[2] == 1

def test_filtering_differences(mock_daphnet_csv, tmp_path):
    # Process with 'none'
    config_none = FOGPreprocessingConfig(filter_mode="none", train_subjects=["S01"], val_subjects=[], test_subjects=[])
    FOGPreprocessingPipeline(config_none).run(mock_daphnet_csv, tmp_path / "none")
    X_none = np.load(tmp_path / "none" / "X_train.npy")
    
    # Process with 'causal'
    config_causal = FOGPreprocessingConfig(filter_mode="causal", train_subjects=["S01"], val_subjects=[], test_subjects=[])
    FOGPreprocessingPipeline(config_causal).run(mock_daphnet_csv, tmp_path / "causal")
    X_causal = np.load(tmp_path / "causal" / "X_train.npy")
    
    # Process with 'offline_zero_phase'
    config_offline = FOGPreprocessingConfig(filter_mode="offline_zero_phase", train_subjects=["S01"], val_subjects=[], test_subjects=[])
    FOGPreprocessingPipeline(config_offline).run(mock_daphnet_csv, tmp_path / "offline")
    X_offline = np.load(tmp_path / "offline" / "X_train.npy")
    
    # Assert they are different due to filtering
    assert not np.allclose(X_none, X_causal)
    assert not np.allclose(X_none, X_offline)
    assert not np.allclose(X_causal, X_offline)
    
    # Verify causal vs offline output means they are distinct algorithms
    # We do not assert exact values because it depends on random data, but they must be structurally valid arrays
    assert X_none.shape == X_causal.shape == X_offline.shape
