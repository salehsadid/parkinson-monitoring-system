import sys
import random
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

import numpy as np
import pandas as pd

def main():
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib is not installed. Please run `pip install matplotlib` to use the visual QA tool.")
        sys.exit(1)
        
    base_dir = Path("data/processed/daphnet")
    output_dir = Path("data/qa")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    modes = ["none", "causal", "offline_zero_phase"]
    
    # Load metadata from 'none' to find a suitable window
    try:
        df_meta = pd.read_csv(base_dir / "none" / "window_metadata.csv")
    except FileNotFoundError:
        print("Processed data not found. Run `python tools/run_fog_preprocessing.py` first.")
        sys.exit(1)
        
    train_meta = df_meta[df_meta["subject_id"].isin(["S01", "S03", "S04", "S05", "S08", "S09"])]
    
    fog_indices = train_meta[train_meta["label"] == 1].index.tolist()
    nofog_indices = train_meta[train_meta["label"] == 0].index.tolist()
    
    if len(fog_indices) == 0 or len(nofog_indices) == 0:
        print("Cannot plot: Need at least one FOG and one NO_FOG window in training set.")
        sys.exit(1)
        
    random.seed(42)
    fog_idx = random.choice(fog_indices)
    nofog_idx = random.choice(nofog_indices)
    
    def plot_comparison(window_idx, label_name):
        fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
        fig.suptitle(f"{label_name} Window (Normalized) - Index {window_idx} Comparison")
        
        colors = {"none": "black", "causal": "red", "offline_zero_phase": "blue"}
        styles = {"none": "dashed", "causal": "solid", "offline_zero_phase": "dotted"}
        
        for mode in modes:
            # We must map the absolute window index in metadata to the X_train index
            # The indices in X_train correspond strictly to the order of train_meta
            # Wait, X_train is strictly filtered by train_mask.
            # So the index in X_train is the rank of the index in train_meta
            train_idx = list(train_meta.index).index(window_idx)
            
            X_train = np.load(base_dir / mode / "X_train.npy")
            window = X_train[train_idx]
            
            axes[0].plot(window[:, 0], color=colors[mode], linestyle=styles[mode], label=f'Accel X ({mode})')
            axes[1].plot(window[:, 1], color=colors[mode], linestyle=styles[mode], label=f'Accel Y ({mode})')
            axes[2].plot(window[:, 2], color=colors[mode], linestyle=styles[mode], label=f'Accel Z ({mode})')
            
        for ax in axes:
            ax.legend(loc="upper right", fontsize='small')
            ax.grid(True)
        axes[2].set_xlabel("Samples (50 Hz)")
        
        plt.tight_layout()
        save_path = output_dir / f"compare_{label_name.lower()}_window.png"
        plt.savefig(save_path)
        print(f"Saved {save_path}")
        plt.close()
        
    plot_comparison(fog_idx, "FOG")
    plot_comparison(nofog_idx, "NO_FOG")

if __name__ == "__main__":
    main()
