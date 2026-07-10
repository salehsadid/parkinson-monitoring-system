import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.preprocessing import FOGPreprocessingConfig, FOGPreprocessingPipeline

def main():
    input_dir = Path("data/interim/daphnet")
    base_output_dir = Path("data/processed/daphnet")
    
    modes = ["none", "causal", "offline_zero_phase"]
    
    for mode in modes:
        output_dir = base_output_dir / mode
        print(f"\n{'='*50}")
        print(f"Starting FOG Preprocessing for mode: {mode}")
        print(f"Input: {input_dir}")
        print(f"Output: {output_dir}")
        
        config = FOGPreprocessingConfig(filter_mode=mode)
        pipeline = FOGPreprocessingPipeline(config)
        
        try:
            report = pipeline.run(input_dir, output_dir)
            print(f"\nPipeline Complete for mode {mode}! Final Report:")
            print(json.dumps(report, indent=2))
            
            # Give explicit recommendations
            if "recommended_class_weights" in report:
                print("\nRecommended Class Weights for Training:")
                print(json.dumps(report["recommended_class_weights"], indent=2))
        except Exception as e:
            print(f"Error during preprocessing mode {mode}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
