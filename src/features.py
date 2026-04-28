"""
Feature Engineering Module.
Smart Utility Expense Prediction System - Python 3.13.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import MODELS_DIR, RANDOM_SEED

FEATURE_COLUMNS_PATH = MODELS_DIR / "feature_columns.json"


def create_time_features(month_series: pd.Series) -> pd.DataFrame:
    """
    Create time-based features from month (Period or datetime).
    Returns DataFrame with month_num, quarter, sin_month, cos_month.
    """
    dt = pd.to_datetime(month_series.astype(str))
    month_num = dt.dt.month
    return pd.DataFrame({
        "month_num": month_num,
        "quarter": dt.dt.quarter,
        "sin_month": np.sin(2 * np.pi * month_num / 12),
        "cos_month": np.cos(2 * np.pi * month_num / 12),
    }, index=month_series.index)


def add_lag_features(df: pd.DataFrame, target_col: str, lags: list[int] = (1, 2, 3)) -> pd.DataFrame:
    """Add lag features (1, 2, 3 months back)."""
    df = df.copy().sort_values("month_parsed").reset_index(drop=True)
    for lag in lags:
        df[f"{target_col}_lag_{lag}"] = df[target_col].shift(lag)
    return df


def add_rolling_mean_features(
    df: pd.DataFrame, target_col: str, windows: list[int] = (3,)
) -> pd.DataFrame:
    """Add rolling mean features (e.g., 3-month rolling average)."""
    df = df.copy().sort_values("month_parsed").reset_index(drop=True)
    for w in windows:
        df[f"{target_col}_rolling_{w}"] = df[target_col].shift(1).rolling(window=w, min_periods=1).mean()
    return df


def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add simple trend (row index as time step)."""
    df = df.copy().sort_values("month_parsed").reset_index(drop=True)
    df["trend"] = np.arange(len(df))
    return df


def build_features(
    df: pd.DataFrame,
    target_col: str = "total",
    lags: tuple[int, ...] = (1, 2, 3),
    rolling_windows: tuple[int, ...] = (3,),
) -> pd.DataFrame:
    """
    Full feature engineering pipeline.
    Returns DataFrame with all features + target.
    """
    df = df.copy()

    # Ensure month_parsed exists
    if "month_parsed" not in df.columns and "month" in df.columns:
        df["month_parsed"] = pd.to_datetime(df["month"].astype(str)).dt.to_period("M")
    elif "month_parsed" not in df.columns:
        raise ValueError("Need 'month_parsed' or 'month' column")

    df = df.sort_values("month_parsed").reset_index(drop=True)

    # Time features
    time_feats = create_time_features(df["month_parsed"])
    df = pd.concat([df, time_feats], axis=1)

    # Lag features for target
    df = add_lag_features(df, target_col, list(lags))

    # Rolling mean
    df = add_rolling_mean_features(df, target_col, list(rolling_windows))

    # Trend
    df = add_trend_features(df)

    return df


def get_feature_columns(target_col: str = "total") -> list[str]:
    """
    Return list of feature column names (excludes target and identifiers).
    """
    base = [
        "month_num", "quarter", "sin_month", "cos_month",
        "trend",
        f"{target_col}_lag_1", f"{target_col}_lag_2", f"{target_col}_lag_3",
        f"{target_col}_rolling_3",
    ]
    return base


def scale_features(
    X: pd.DataFrame,
    scaler=None,
    fit: bool = True,
):
    """
    Scale features. Uses StandardScaler if scaler not provided.
    Returns (X_scaled, scaler).
    """
    from sklearn.preprocessing import StandardScaler

    if scaler is None:
        scaler = StandardScaler()
    if fit:
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = scaler.transform(X)
    return X_scaled, scaler


def save_feature_columns(columns: list[str], path: Path | None = None) -> Path:
    """Save feature column list to models/feature_columns.json"""
    if path is None:
        path = FEATURE_COLUMNS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(columns, indent=2), encoding="utf-8")
    return path


def load_feature_columns(path: Path | None = None) -> list[str]:
    """Load feature columns from JSON."""
    if path is None:
        path = FEATURE_COLUMNS_PATH
    if not path.exists():
        return get_feature_columns()
    return json.loads(path.read_text(encoding="utf-8"))
