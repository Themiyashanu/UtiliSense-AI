"""
Prediction Service - Next month bill prediction.
Handles cold start (1-3 months history) gracefully.
Smart Utility Expense Prediction System - Python 3.13.
"""
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from .config import MODELS_DIR
from .features import build_features, load_feature_columns


def load_artifacts():
    """Load model, scaler, config."""
    with open(MODELS_DIR / "best_model.pkl", "rb") as f:
        model = pickle.load(f)
    scaler = None
    if (MODELS_DIR / "scaler.pkl").exists():
        with open(MODELS_DIR / "scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
    config = json.loads((MODELS_DIR / "training_config.json").read_text(encoding="utf-8"))
    feat_cols = config.get("feat_cols") or load_feature_columns()
    return model, scaler, feat_cols


def _ensure_month_format(month: str) -> str:
    """Normalize month to YYYY-MM."""
    if hasattr(month, "strftime"):
        return month.strftime("%Y-%m")
    s = str(month).strip()
    if len(s) == 7 and s[4] == "-":
        return s
    try:
        dt = pd.to_datetime(s)
        return dt.strftime("%Y-%m")
    except Exception:
        return s


def predict_next_month(
    user_recent_bills: list[dict],
    return_breakdown: bool = True,
) -> dict:
    """
    Predict next month's bill.

    user_recent_bills: List of dicts with keys like month, electricity, water, telecom, total.
        Minimum 1 month, up to 3 months. More history = better prediction.

    Returns dict with:
        - total: predicted total (LKR)
        - electricity, water, telecom: if breakdown requested and columns exist
        - confidence: 'high' | 'medium' | 'low' based on history length
    """
    if not user_recent_bills:
        return _cold_start_prediction(return_breakdown)

    df = pd.DataFrame(user_recent_bills)
    # Standardize column names
    col_map = {
        "Month": "month", "month": "month",
        "Electricity": "electricity", "electricity": "electricity",
        "Water": "water", "water": "water",
        "Telecom": "telecom", "telecom": "telecom",
        "Total": "total", "Total_LKR": "total", "total": "total",
    }
    df = df.rename(columns={c: col_map.get(c, c) for c in df.columns if c in col_map})

    # Ensure total exists
    if "total" not in df.columns:
        df["total"] = (
            df.get("electricity", 0).fillna(0) +
            df.get("water", 0).fillna(0) +
            df.get("telecom", 0).fillna(0)
        )
    df["month_parsed"] = pd.to_datetime(df["month"].astype(str)).dt.to_period("M")
    df = df.sort_values("month_parsed").reset_index(drop=True)

    try:
        model, scaler, feat_cols = load_artifacts()
    except FileNotFoundError:
        return _fallback_prediction(df, return_breakdown)

    # Build features for "next" row
    df_feat = build_features(df, target_col="total")
    # Last row has features for predicting next month
    last = df_feat.iloc[[-1]]
    X = last[feat_cols].fillna(0) if all(c in last.columns for c in feat_cols) else None

    if X is None or X.isnull().all().any():
        return _fallback_prediction(df, return_breakdown)

    if scaler is not None:
        X_s = scaler.transform(X)
    else:
        X_s = X.values

    pred_total = float(model.predict(X_s)[0])
    pred_total = max(0, pred_total)

    # Breakdown: use last known proportions if available
    result = {"total": round(pred_total, 2), "confidence": _confidence(len(df))}
    if return_breakdown:
        if all(c in df.columns for c in ["electricity", "water", "telecom"]):
            ratios = df[["electricity", "water", "telecom"]].sum()
            total_sum = ratios.sum()
            if total_sum > 0:
                result["electricity"] = round(pred_total * (ratios["electricity"] / total_sum), 2)
                result["water"] = round(pred_total * (ratios["water"] / total_sum), 2)
                result["telecom"] = round(pred_total * (ratios["telecom"] / total_sum), 2)
            else:
                result["electricity"] = round(pred_total / 3, 2)
                result["water"] = round(pred_total / 3, 2)
                result["telecom"] = round(pred_total - result["electricity"] - result["water"], 2)
        else:
            result["electricity"] = round(pred_total / 3, 2)
            result["water"] = round(pred_total / 3, 2)
            result["telecom"] = round(pred_total - result["electricity"] - result["water"], 2)

    return result


def _confidence(n_months: int) -> str:
    if n_months >= 3:
        return "high"
    if n_months >= 2:
        return "medium"
    return "low"


def _cold_start_prediction(return_breakdown: bool) -> dict:
    """When no history: use simple default or load from training data."""
    try:
        config = json.loads((MODELS_DIR / "training_config.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {
            "total": 0,
            "electricity": 0,
            "water": 0,
            "telecom": 0,
            "confidence": "low",
            "message": "No history and no trained model. Add bills and train the model.",
        }

    # Fallback: use mean from training (we don't have it saved, use reasonable default)
    default_total = 15000  # LKR typical household
    result = {
        "total": default_total,
        "confidence": "low",
        "message": "Prediction based on default. Add more bill history for better accuracy.",
    }
    if return_breakdown:
        result["electricity"] = round(default_total * 0.5, 2)
        result["water"] = round(default_total * 0.2, 2)
        result["telecom"] = round(default_total * 0.3, 2)
    return result


def _fallback_prediction(df: pd.DataFrame, return_breakdown: bool) -> dict:
    """When model fails: use last month or average."""
    total_col = "total" if "total" in df.columns else None
    if total_col is None and "electricity" in df.columns:
        df["total"] = df["electricity"].fillna(0) + df.get("water", 0).fillna(0) + df.get("telecom", 0).fillna(0)
        total_col = "total"

    if total_col and len(df) > 0:
        pred = float(df[total_col].iloc[-1])
    else:
        pred = 15000

    result = {"total": round(pred, 2), "confidence": "low"}
    if return_breakdown:
        if all(c in df.columns for c in ["electricity", "water", "telecom"]):
            last = df.iloc[-1]
            result["electricity"] = round(float(last.get("electricity", pred / 3)), 2)
            result["water"] = round(float(last.get("water", pred / 3)), 2)
            result["telecom"] = round(float(last.get("telecom", pred / 3)), 2)
        else:
            result["electricity"] = round(pred / 3, 2)
            result["water"] = round(pred / 3, 2)
            result["telecom"] = round(pred - result["electricity"] - result["water"], 2)
    return result
