"""
Data Preparation & Cleaning Module.
Smart Utility Expense Prediction System - Python 3.13.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA_PROCESSED, RANDOM_SEED
from .data_understanding import find_dataset, infer_target_column, load_data as load_raw_data

# Standardize column names for consistency
COLUMN_MAPPING = {
    "month": ["month", "Month", "MONTH", "date", "Date"],
    "electricity": ["electricity", "Electricity", "CEB", "electricity_lkr"],
    "water": ["water", "Water", "NWSDB", "water_lkr"],
    "telecom": ["telecom", "Telecom", "Dialog", "Mobitel", "SLT", "telecom_lkr"],
    "total": ["total", "Total", "Total_LKR", "total_lkr", "TOTAL"],
}


def _map_column(df: pd.DataFrame, canonical: str) -> str | None:
    """Return actual column name for canonical name, or None."""
    cols = list(df.columns)
    for alias in COLUMN_MAPPING.get(canonical, [canonical]):
        if alias in cols:
            return alias
    # Fuzzy: any column containing the keyword
    for c in cols:
        if canonical.lower() in str(c).lower():
            return c
    return None


def load_data() -> pd.DataFrame:
    """Load raw dataset (auto-detect)."""
    return load_raw_data()


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse month/date column to datetime. Handles formats like 2024-01, Jan-2024, etc.
    """
    df = df.copy()
    month_col = _map_column(df, "month")
    if month_col is None:
        return df

    col = df[month_col]
    if pd.api.types.is_datetime64_any_dtype(col):
        df["month_parsed"] = pd.to_datetime(col).dt.to_period("M")
        return df

    # Try common formats
    for fmt in ["%Y-%m", "%m/%Y", "%b-%Y", "%B-%Y", "%Y/%m", "%d/%m/%Y"]:
        try:
            df["month_parsed"] = pd.to_datetime(col.astype(str), format=fmt).dt.to_period("M")
            return df
        except (ValueError, TypeError):
            continue

    # Fallback: coerce
    df["month_parsed"] = pd.to_datetime(col.astype(str), errors="coerce").dt.to_period("M")
    return df


def handle_missing_values(df: pd.DataFrame, strategy: str = "forward_fill") -> pd.DataFrame:
    """
    Handle missing values. Default: forward fill for time series.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for c in numeric_cols:
        if df[c].isnull().any():
            if strategy == "forward_fill":
                df[c] = df[c].ffill().bfill()  # fill remaining with bfill
            elif strategy == "mean":
                df[c] = df[c].fillna(df[c].mean())
            elif strategy == "zero":
                df[c] = df[c].fillna(0)

    return df


def outlier_handling(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: str = "iqr",
    factor: float = 1.5,
) -> pd.DataFrame:
    """
    Handle outliers using IQR or cap. Default: IQR-based capping.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if columns:
        numeric_cols = [c for c in columns if c in df.columns]

    for c in numeric_cols:
        if method == "iqr":
            q1 = df[c].quantile(0.25)
            q3 = df[c].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - factor * iqr
            upper = q3 + factor * iqr
            df[c] = df[c].clip(lower=lower, upper=upper)
        elif method == "none":
            pass

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline: parse dates, handle missing, outliers,
    standardize column names.
    """
    df = df.copy()

    # Parse dates
    df = parse_dates(df)

    # Standardize numeric columns (electricity, water, telecom, total)
    for canonical in ["electricity", "water", "telecom", "total"]:
        actual = _map_column(df, canonical)
        if actual:
            df[canonical] = pd.to_numeric(df[actual], errors="coerce")

    # Ensure total exists - compute if missing
    if "total" not in df.columns or df["total"].isnull().all():
        comp = 0
        for c in ["electricity", "water", "telecom"]:
            if c in df.columns:
                comp = comp + df[c].fillna(0)
        df["total"] = comp
    else:
        df["total"] = pd.to_numeric(df["total"], errors="coerce")

    # Handle missing
    df = handle_missing_values(df, strategy="forward_fill")

    # Outlier handling (cap extreme values)
    df = outlier_handling(df, method="iqr", factor=1.5)

    # Sort by time
    if "month_parsed" in df.columns:
        df = df.sort_values("month_parsed").reset_index(drop=True)

    return df


def save_clean_dataset(df: pd.DataFrame, path: Path | None = None) -> Path:
    """Save cleaned dataset to data/processed/cleaned.csv"""
    if path is None:
        path = DATA_PROCESSED / "cleaned.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def run_preprocessing() -> pd.DataFrame:
    """
    Full preprocessing pipeline: load -> clean -> save.
    """
    df = load_data()
    df = clean_data(df)
    save_clean_dataset(df)
    print(f"Cleaned dataset saved to {DATA_PROCESSED / 'cleaned.csv'}")
    print(f"Shape: {df.shape}")
    return df


if __name__ == "__main__":
    run_preprocessing()
