import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.datasets.pads_adapter import PADSAdapter

def main():
    raw_dir = Path("data/raw/pads")
    out_dir = Path("data/interim/pads")
    try:
        adapter = PADSAdapter(raw_dir)
        print("Importing PADS Right Wrist data...")
        adapter.import_data(out_dir)
        print(f"Import complete. Canonical data saved to {out_dir}")
    except Exception as e:
        print(f"Error importing PADS: {e}")

if __name__ == "__main__":
    main()
