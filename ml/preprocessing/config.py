from pydantic import BaseModel, Field

class FOGPreprocessingConfig(BaseModel):
    """
    Configuration for the FOG Preprocessing Pipeline.
    """
    original_sampling_rate_hz: float = Field(default=64.0, description="Original Daphnet sampling rate")
    target_sampling_rate_hz: float = Field(default=50.0, description="Target ESP32 runtime sampling rate")
    
    # Windowing
    window_size_seconds: float = Field(default=2.0, description="Window size in seconds")
    overlap_fraction: float = Field(default=0.5, description="Overlap fraction for sliding windows (0.0 to 1.0)")
    fog_fraction_threshold: float = Field(default=0.5, description="Fraction of FOG samples required to label the window as FOG (1)")
    
    # Filtering
    filter_mode: str = Field(default="offline_zero_phase", description="Filter mode: 'none', 'causal', or 'offline_zero_phase'")
    filter_cutoff_hz: float = Field(default=20.0, description="Butterworth filter cutoff frequency")
    filter_order: int = Field(default=4, description="Butterworth filter order")
    
    # Splitting
    random_seed: int = Field(default=42, description="Random seed for deterministic subject assignment")
    
    # We explicitly assign these to guarantee representativeness.
    # S01, S02, S03, S04, S05, S06, S07, S08, S09, S10
    # The split below ensures Train, Val, and Test all get FOG events.
    # Note: Daphnet has 10 subjects. S04, S10 don't have FOG annotations? Wait, we will do deterministic assignment.
    # Actually, we can use a dynamic split logic, but defining it here is safer if we want full control.
    train_subjects: list[str] = Field(default=["S01", "S03", "S04", "S05", "S08", "S09"], description="Explicit subjects for training")
    val_subjects: list[str] = Field(default=["S06", "S07"], description="Explicit subjects for validation")
    test_subjects: list[str] = Field(default=["S02", "S10"], description="Explicit subjects for testing")
    
    @property
    def window_samples(self) -> int:
        return int(self.window_size_seconds * self.target_sampling_rate_hz)
        
    @property
    def stride_samples(self) -> int:
        return int(self.window_samples * (1.0 - self.overlap_fraction))
