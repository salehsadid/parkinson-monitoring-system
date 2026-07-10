import sys
import json
import random
from pathlib import Path

# Try to import matplotlib; handle gracefully if not installed
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

import numpy as np

def main():
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib is not installed. Please run `pip install matplotlib` to use the visual QA tool.")
        sys.exit(1)
        
    processed_dir = Path("data/processed/daphnet")
    output_dir = Path("data/qa")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load training data
    try:
        X_train = np.load(processed_dir / "X_train.npy")
        y_train = np.load(processed_dir / "y_train.npy")
    except FileNotFoundError:
        print("Processed data not found. Run `python tools/run_fog_preprocessing.py` first.")
        sys.exit(1)
        
    fog_indices = np.where(y_train == 1)[0]
    nofog_indices = np.where(y_train == 0)[0]
    
    if len(fog_indices) == 0 or len(nofog_indices) == 0:
        print("Cannot plot: Need at least one FOG and one NO_FOG window in training set.")
        sys.exit(1)
        
    random.seed(42)
    fog_idx = random.choice(fog_indices)
    nofog_idx = random.choice(nofog_indices)
    
    fog_window = X_train[fog_idx]
    nofog_window = X_train[nofog_idx]
    
    # Plot FOG window
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(f"FOG Window (Normalized) - Index {fog_idx}")
    axes[0].plot(fog_window[:, 0], color='r', label='Accel X')
    axes[1].plot(fog_window[:, 1], color='g', label='Accel Y')
    axes[2].plot(fog_window[:, 2], color='b', label='Accel Z')
    for ax in axes:
        ax.legend(loc="upper right")
        ax.grid(True)
    axes[2].set_xlabel("Samples (50 Hz)")
    plt.tight_layout()
    plt.savefig(output_dir / "fog_window_sample.png")
    print(f"Saved {output_dir / 'fog_window_sample.png'}")
    plt.close()
    
    # Plot NO FOG window
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(f"NO_FOG Window (Normalized) - Index {nofog_idx}")
    axes[0].plot(nofog_window[:, 0], color='r', label='Accel X')
    axes[1].plot(nofog_window[:, 1], color='g', label='Accel Y')
    axes[2].plot(nofog_window[:, 2], color='b', label='Accel Z')
    for ax in axes:
        ax.legend(loc="upper right")
        ax.grid(True)
    axes[2].set_xlabel("Samples (50 Hz)")
    plt.tight_layout()
    plt.savefig(output_dir / "no_fog_window_sample.png")
    print(f"Saved {output_dir / 'no_fog_window_sample.png'}")
    plt.close()

if __name__ == "__main__":
    main()
