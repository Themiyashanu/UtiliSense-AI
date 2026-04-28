"""
Model Training Module - Multiple models comparison.
Smart Utility Expense Prediction System - Python 3.13.
"""
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .config import DATA_PROCESSED, MODELS_DIR, RANDOM_SEED
from .features import (
    build_features,
    get_feature_columns,
    save_feature_columns,
    scale_features,
    load_feature_columns,
)


def time_aware_split(
    df: pd.DataFrame,
    target_col: str = "total",
    test_size: int = 3,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Train on older months, test on newer months.
    test_size: number of most recent months for test.
    """
    df = df.sort_values("month_parsed").reset_index(drop=True)
    n = len(df)
    if n <= test_size:
        train_end = max(1, n - 1)
        test_start = train_end
    else:
        train_end = n - test_size
        test_start = train_end

    train_df = df.iloc[:train_end]
    test_df = df.iloc[test_start:]

    feat_cols = [c for c in get_feature_columns(target_col) if c in train_df.columns]
    X_train = train_df[feat_cols].fillna(0)
    y_train = train_df[target_col]
    X_test = test_df[feat_cols].fillna(0)
    y_test = test_df[target_col]

    return X_train, y_train, X_test, y_test


def train_models(
    df: pd.DataFrame,
    target_col: str = "total",
    use_scaling: bool = True,
) -> dict:
    """
    Train Linear Regression, Random Forest, and optionally XGBoost.
    Returns dict with models, metrics, scaler.
    """
    df_feat = build_features(df, target_col=target_col)
    feat_cols = [c for c in get_feature_columns(target_col) if c in df_feat.columns]
    save_feature_columns(feat_cols)

    X_train, y_train, X_test, y_test = time_aware_split(df_feat, target_col=target_col)

    scaler = None
    if use_scaling:
        X_train_s, scaler = scale_features(X_train, fit=True)
        X_test_s, _ = scale_features(X_test, scaler=scaler, fit=False)
    else:
        X_train_s = X_train.fillna(0).values
        X_test_s = X_test.fillna(0).values

    y_train = y_train.values
    y_test = y_test.values

    models = {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=RANDOM_SEED
        ),
    }

    # Try XGBoost if available
    try:
        from xgboost import XGBRegressor
        models["XGBRegressor"] = XGBRegressor(
            n_estimators=100, max_depth=6, random_state=RANDOM_SEED
        )
    except ImportError:
        pass

    # Try GradientBoosting (sklearn)
    from sklearn.ensemble import GradientBoostingRegressor
    models["GradientBoostingRegressor"] = GradientBoostingRegressor(
        n_estimators=100, max_depth=5, random_state=RANDOM_SEED
    )

    results = {}
    best_model = None
    best_r2 = -np.inf

    for name, model in models.items():
        model.fit(X_train_s, y_train)
        y_pred = model.predict(X_test_s)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results[name] = {
            "MAE": float(mae),
            "RMSE": float(rmse),
            "R2": float(r2),
        }
        if r2 > best_r2:
            best_r2 = r2
            best_model = (name, model)

    # K-Fold / TimeSeriesSplit cross-validation on best model
    cv = TimeSeriesSplit(n_splits=5)
    best_name, best_m = best_model
    cv_scores = cross_val_score(
        best_m, X_train_s, y_train, cv=cv, scoring="r2"
    )
    results[best_name]["CV_R2_mean"] = float(cv_scores.mean())
    results[best_name]["CV_R2_std"] = float(cv_scores.std())

    return {
        "models": {k: v for k, v in models.items()},
        "results": results,
        "best_model_name": best_name,
        "scaler": scaler,
        "feat_cols": feat_cols,
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
    }


def save_artifacts(
    train_output: dict,
    models_dir: Path | None = None,
) -> None:
    """Save best_model.pkl, scaler.pkl, training_config.json"""
    if models_dir is None:
        models_dir = MODELS_DIR
    models_dir.mkdir(parents=True, exist_ok=True)

    best_name = train_output["best_model_name"]
    best_model = train_output["models"][best_name]

    with open(models_dir / "best_model.pkl", "wb") as f:
        pickle.dump(best_model, f)

    if train_output.get("scaler") is not None:
        with open(models_dir / "scaler.pkl", "wb") as f:
            pickle.dump(train_output["scaler"], f)

    config = {
        "random_seed": RANDOM_SEED,
        "best_model": best_name,
        "target_col": "total",
        "feat_cols": train_output["feat_cols"],
        "use_scaling": train_output.get("scaler") is not None,
    }
    (models_dir / "training_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    save_feature_columns(train_output["feat_cols"], models_dir / "feature_columns.json")


def run_training() -> dict:
    """Full training pipeline: load cleaned data -> train -> save artifacts."""
    df = pd.read_csv(DATA_PROCESSED / "cleaned.csv")
    if "month_parsed" not in df.columns and "month" in df.columns:
        df["month_parsed"] = pd.to_datetime(df["month"].astype(str)).dt.to_period("M")

    out = train_models(df, target_col="total", use_scaling=True)
    save_artifacts(out)
    print(f"Best model: {out['best_model_name']}")
    print("Results:", out["results"])
    return out


if __name__ == "__main__":
    run_training()
