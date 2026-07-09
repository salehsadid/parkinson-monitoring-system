import pytest
import shutil
from pathlib import Path
from ml.datasets.daphnet_adapter import DaphnetAdapter

@pytest.fixture
def mock_daphnet_dir(tmp_path):
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    
    # Create a dummy Daphnet file S01R01.txt
    dummy_file = dataset_dir / "S01R01.txt"
    with open(dummy_file, "w", encoding="utf-8") as f:
        # 11 columns: Time, AnkleX, AnkleY, AnkleZ, ThighX, ThighY, ThighZ, TrunkX, TrunkY, TrunkZ, Annotation
        f.write("15 100 200 300 400 500 600 700 800 900 1\n") # no freeze
        f.write("31 101 201 301 401 501 601 701 801 901 2\n") # freeze
        f.write("46 102 202 302 402 502 602 702 802 902 0\n") # outside experiment
        
    return tmp_path

def test_daphnet_audit(mock_daphnet_dir):
    adapter = DaphnetAdapter(mock_daphnet_dir)
    report = adapter.audit()
    
    assert report["total_files"] == 1
    assert report["subjects"] == ["S01"]
    assert report["recordings"] == ["S01R01.txt"]
    assert report["total_rows"] == 3
    assert report["annotation_1_count"] == 1
    assert report["annotation_2_count"] == 1
    assert report["annotation_0_count"] == 1

def test_daphnet_import(mock_daphnet_dir):
    adapter = DaphnetAdapter(mock_daphnet_dir)
    out_dir = mock_daphnet_dir / "out"
    adapter.import_data(out_dir)
    
    out_file = out_dir / "S01R01.csv"
    assert out_file.exists()
    
    with open(out_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    assert len(lines) == 3 # header + 2 valid rows (annotation 0 is skipped)
    assert "ankle_ax" in lines[0]
    
    # Check first valid row (annotation 1 -> fog_label 0)
    parts = lines[1].strip().split(",")
    assert parts[2] == "S01"
    assert parts[3] == "R01"
    assert parts[6] == "100.0" # ankle_ax
    assert parts[-2] == "1" # raw_annotation
    assert parts[-1] == "0" # fog_label
    
    # Check second valid row (annotation 2 -> fog_label 1)
    parts2 = lines[2].strip().split(",")
    assert parts2[-2] == "2" # raw_annotation
    assert parts2[-1] == "1" # fog_label
