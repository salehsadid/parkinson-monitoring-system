import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.datasets.daphnet_adapter import DaphnetAdapter

def main():
    raw_dir = Path("data/raw/daphnet")
    try:
        adapter = DaphnetAdapter(raw_dir)
        report = adapter.audit()
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(f"Error auditing Daphnet: {e}")

if __name__ == "__main__":
    main()
