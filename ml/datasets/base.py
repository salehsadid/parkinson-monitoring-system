import abc
from pathlib import Path
from typing import Dict, Any

class BaseDatasetAdapter(abc.ABC):
    """
    Base class for dataset adapters. 
    Defines the contract for auditing and importing datasets.
    """
    
    def __init__(self, raw_data_dir: Path):
        self.raw_data_dir = Path(raw_data_dir)
        if not self.raw_data_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {self.raw_data_dir}")
            
    @abc.abstractmethod
    def audit(self) -> Dict[str, Any]:
        """
        Perform a read-only audit of the dataset and return a summary report.
        """
        pass
        
    @abc.abstractmethod
    def import_data(self, output_dir: Path) -> None:
        """
        Convert raw dataset into canonical format and save to output_dir.
        """
        pass
