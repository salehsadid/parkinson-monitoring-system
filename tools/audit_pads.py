import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.datasets.pads_adapter import PADSAdapter

def main():
    raw_dir = Path("data/raw/pads")
    try:
        adapter = PADSAdapter(raw_dir)
        report = adapter.audit()
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(f"Error auditing PADS: {e}")

if __name__ == "__main__":
    main()
