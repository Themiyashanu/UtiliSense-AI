# Quick Start Guide

## 1. How to Run EDA Notebook

1. Ensure the cleaned dataset exists:
   ```bash
   python -c "from src.data_preprocessing import run_preprocessing; run_preprocessing()"
   ```
   Or run the full pipeline first (step 3 below).

2. Open Jupyter:
   ```bash
   jupyter notebook notebooks/01_EDA.ipynb
   ```
   Or in VS Code: open `notebooks/01_EDA.ipynb` and run all cells.

3. EDA outputs (charts) are saved to `reports/figures/`.

---

## 2. How to Run Training Pipeline (train.py)

**Option A – Full pipeline (recommended):**
```bash
python scripts/run_pipeline.py
```
This runs: data understanding → preprocessing → training → evaluation.

**Option B – Training only:**
```bash
python -c "from src.train import run_training; run_training()"
```
Or:
```bash
cd src && python train.py
```

**Prerequisites:**
- Dataset in `data/raw/` (e.g. `My Home dataset new 1.xlsx`)
- `data/processed/cleaned.csv` exists (run preprocessing first if not)

**Outputs:**
- `models/best_model.pkl`
- `models/scaler.pkl`
- `models/feature_columns.json`
- `models/training_config.json`
- `reports/model_comparison.csv`

---

## 3. How to Evaluate Models (evaluate.py)

**After training:**
```bash
python -c "from src.evaluate import run_evaluation; run_evaluation()"
```
Or:
```bash
cd src && python evaluate.py
```

**Outputs:**
- `reports/metrics.json` (MAE, RMSE, R2)
- `reports/figures/residual_analysis.png`

---

## 4. How to Start Flask App

```bash
python run.py
```
Then open: **http://localhost:5000**

**First-time setup:**
```bash
python scripts/create_admin.py
```
Creates an admin user (default: admin / admin123).

---

## 5. How the Prediction API is Called from the Web App

- **Route:** `POST /predict/api`
- **Behavior:**
  1. If the request has no JSON body (or empty), the app uses the last 3 bills from the database.
  2. If the request includes `user_recent_bills` (array of `{month, electricity, water, telecom, total}`), those are used instead.
- **Flow:**
  1. Frontend (Predict page) calls `fetch('/predict/api', { method: 'POST', body: '{}' })`.
  2. Backend loads the user’s recent bills from the DB.
  3. `src.predict.predict_next_month(user_recent_bills)` is called.
  4. Result (total, electricity, water, telecom, confidence) is returned as JSON.
- **Cold start:** With no bills, the API returns a default prediction and low confidence.

---

## Summary Checklist

| Step | Command |
|------|---------|
| 1. Install | `pip install -r requirements.txt` |
| 2. Add data | Copy dataset to `data/raw/` |
| 3. Pipeline | `python scripts/run_pipeline.py` |
| 4. Admin | `python scripts/create_admin.py` |
| 5. Run app | `python run.py` |
