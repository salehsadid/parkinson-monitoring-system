import pytest
from pathlib import Path
from ml.datasets.pads_adapter import PADSAdapter

@pytest.fixture
def mock_pads_dir(tmp_path):
    timeseries_dir = tmp_path / "movement" / "timeseries"
    timeseries_dir.mkdir(parents=True)
    
    # Create right wrist file
    rw_file = timeseries_dir / "001_CrossArms_RightWrist.txt"
    with open(rw_file, "w", encoding="utf-8") as f:
        # Time, AccX, AccY, AccZ, GyroX, GyroY, GyroZ
        f.write("0.0,1.0,2.0,3.0,4.0,5.0,6.0\n")
        f.write("0.01,1.1,2.1,3.1,4.1,5.1,6.1\n")
        
    # Create left wrist file
    lw_file = timeseries_dir / "001_CrossArms_LeftWrist.txt"
    with open(lw_file, "w", encoding="utf-8") as f:
        f.write("0.0,9.0,9.0,9.0,9.0,9.0,9.0\n")
        
    return tmp_path

def test_pads_audit(mock_pads_dir):
    adapter = PADSAdapter(mock_pads_dir)
    report = adapter.audit()
    
    assert report["total_files"] == 2
    assert report["right_wrist_files"] == 1
    assert report["left_wrist_files"] == 1
    assert report["participants"] == ["001"]
    assert report["tasks"] == ["CrossArms"]
    assert report["total_right_wrist_rows"] == 2

def test_pads_import(mock_pads_dir):
    adapter = PADSAdapter(mock_pads_dir)
    out_dir = mock_pads_dir / "out"
    adapter.import_data(out_dir)
    
    out_file = out_dir / "001_CrossArms_RightWrist.csv"
    assert out_file.exists()
    
    # Left wrist should NOT be imported
    lw_out_file = out_dir / "001_CrossArms_LeftWrist.csv"
    assert not lw_out_file.exists()
    
    with open(out_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    assert len(lines) == 3 # header + 2 rows
    assert "right_ax" in lines[0]
    
    parts = lines[1].strip().split(",")
    assert parts[2] == "001" # participant_id
    assert parts[4] == "CrossArms" # task_id
    assert parts[7] == "1.0" # right_ax
    assert parts[10] == "4.0" # right_gx
