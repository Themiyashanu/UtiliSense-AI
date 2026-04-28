"""
Data Understanding Module - Auto-detect dataset, print schema, identify target.
For Smart Utility Expense Prediction System.
Python 3.13 compatible.
"""
import json
from pathlib import Path

import pandas as pd

from .config import DATA_RAW, DATA_PROCESSED, TARGET_COLUMN_PREFERENCE


def find_dataset() -> Path | None:
    """
    Auto-detect dataset file in data/raw.
    Priority: My Home dataset new 1.xlsx > any .xlsx > any .csv
    """
    if not DATA_RAW.exists():
        return None

    # Specific file first
    specific = DATA_RAW / "My Home dataset new 1.xlsx"
    if specific.exists():
        return specific

    # Any xlsx
    for f in DATA_RAW.glob("*.xlsx"):
        return f

    # Any csv
    for f in DATA_RAW.glob("*.csv"):
        return f

    return None


def load_data(path: Path | None = None) -> pd.DataFrame:
    """Load dataset from path or auto-detected file."""
    if path is None:
        path = find_dataset()
    if path is None:
        raise FileNotFoundError(
            f"No dataset found in {DATA_RAW}. "
            "Place 'My Home dataset new 1.xlsx' or any .csv/.xlsx in data/raw/"
        )

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    return df


def infer_target_column(df: pd.DataFrame) -> str | None:
    """Identify target column. Prefer Total_LKR if present; otherwise infer."""
    cols_lower = {c.lower(): c for c in df.columns}

    for pref in TARGET_COLUMN_PREFERENCE:
        if pref.lower() in cols_lower:
            return cols_lower[pref.lower()]

    # Fallback: column with 'total' in name
    for c in df.columns:
        if "total" in c.lower() and df[c].dtype in ["int64", "float64"]:
            return c

    return None


def print_schema_report(df: pd.DataFrame) -> dict:
    """
    Print and return schema: column types, missing values, target.
    """
    report = {
        "shape": list(df.shape),
        "columns": list(df.columns),
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "target": infer_target_column(df),
    }

    print("=" * 60)
    print("DATA SCHEMA REPORT")
    print("=" * 60)
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"\nColumns: {list(df.columns)}")
    print("\nColumn types:")
    for c in df.columns:
        print(f"  {c}: {df[c].dtype}")
    print("\nMissing values:")
    for c in df.columns:
        miss = df[c].isnull().sum()
        if miss > 0:
            print(f"  {c}: {miss} ({miss/len(df)*100:.1f}%)")
    print(f"\nInferred target column: {report['target']}")
    print("=" * 60)

    return report


def save_data_dictionary(report: dict, output_path: Path | None = None) -> Path:
    """Write data_dictionary.md describing each column."""
    if output_path is None:
        output_path = DATA_PROCESSED.parent / "data_dictionary.md"

    lines = [
        "# Data Dictionary",
        "",
        "## Dataset Overview",
        f"- Rows: {report['shape'][0]}",
        f"- Columns: {report['shape'][1]}",
        f"- Target variable: {report.get('target', 'Not inferred')}",
        "",
        "## Column Descriptions",
        "",
        "| Column | Type | Missing % | Description |",
        "|--------|------|-----------|-------------|",
    ]

    desc_map = {
        "month": "Billing month (e.g., 2024-01)",
        "electricity": "CEB electricity bill amount (LKR)",
        "water": "NWSDB water bill amount (LKR)",
        "telecom": "Dialog/Mobitel/SLT telecom bill amount (LKR)",
        "total": "Total utility expense (LKR)",
    }

    for col in report["columns"]:
        dtype = report["dtypes"].get(str(col), "unknown")
        miss = report["missing_pct"].get(col, 0)
        desc = "Other"
        for key, val in desc_map.items():
            if key in col.lower():
                desc = val
                break
        lines.append(f"| {col} | {dtype} | {miss}% | {desc} |")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def run_data_understanding() -> tuple[pd.DataFrame, dict]:
    """
    Full data understanding pipeline.
    Returns (DataFrame, report dict).
    """
    path = find_dataset()
    if path is None:
        raise FileNotFoundError(
            f"No dataset in {DATA_RAW}. Add 'My Home dataset new 1.xlsx' or .csv/.xlsx"
        )

    df = load_data(path)
    report = print_schema_report(df)
    save_data_dictionary(report)
    return df, report


if __name__ == "__main__":
    df, report = run_data_understanding()
    print("\nData loaded successfully.")
    print(df.head())
