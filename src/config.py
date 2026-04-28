"""
Configuration and paths for the Smart Utility Expense Prediction system.
Python 3.13 compatible.
"""
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data paths
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_FIGURES = REPORTS_DIR / "figures"

# Ensure directories exist
for d in [DATA_RAW, DATA_PROCESSED, MODELS_DIR, REPORTS_DIR, REPORTS_FIGURES]:
    d.mkdir(parents=True, exist_ok=True)

# Dataset detection: priority order
DATASET_PRIORITY = [
    "My Home dataset new 1.xlsx",
    "*.xlsx",
    "*.csv",
]

# Target column preference
TARGET_COLUMN_PREFERENCE = ["Total_LKR", "Total", "total_lkr", "total"]

# Reproducibility
RANDOM_SEED = 42
