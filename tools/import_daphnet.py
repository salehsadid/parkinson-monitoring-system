import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.datasets.daphnet_adapter import DaphnetAdapter

def main():
    raw_dir = Path("data/raw/daphnet")
    out_dir = Path("data/interim/daphnet")
    try:
        adapter = DaphnetAdapter(raw_dir)
        print("Importing Daphnet data...")
        adapter.import_data(out_dir)
        print(f"Import complete. Canonical data saved to {out_dir}")
    except Exception as e:
        print(f"Error importing Daphnet: {e}")

if __name__ == "__main__":
    main()
