"""
Run full data science pipeline: preprocess -> train -> evaluate.
Usage: python scripts/run_pipeline.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def main():
    print("=" * 50)
    print("1. Data Understanding & Preprocessing")
    print("=" * 50)
    from src.data_understanding import run_data_understanding
    run_data_understanding()
    from src.data_preprocessing import run_preprocessing
    run_preprocessing()

    print("\n" + "=" * 50)
    print("2. Model Training")
    print("=" * 50)
    from src.train import run_training
    run_training()

    print("\n" + "=" * 50)
    print("3. Model Evaluation")
    print("=" * 50)
    from src.evaluate import run_evaluation
    run_evaluation()

    print("\nPipeline complete. Artifacts in /models and /reports")

if __name__ == "__main__":
    main()
