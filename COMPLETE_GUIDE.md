# Complete Step-by-Step Guide

This guide walks you through building and running the Smart Utility Expense Prediction System **individually**, step by step.

---

## Step 0: Prerequisites

- **Python 3.13** installed
- Your dataset: `My Home dataset new 1.xlsx` in the project folder
- Terminal/Command Prompt

---

## Step 1: Setup Project

1. Open a terminal in the project folder: `c:\Users\USER\Desktop\utility`
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 2: Add Your Dataset

1. Create the folder if it doesn't exist: `data\raw\`
2. Copy your Excel file: `My Home dataset new 1.xlsx` into `data\raw\`
3. The system will auto-detect it. Supported: `.xlsx`, `.csv`

---

## Step 3: Data Understanding (Optional)

Run to print schema and create `data_dictionary.md`:
```bash
python -c "from src.data_understanding import run_data_understanding; run_data_understanding()"
```
- Prints: columns, types, missing values, target column
- Creates: `data\data_dictionary.md`

---

## Step 4: Data Preprocessing

```bash
python -c "from src.data_preprocessing import run_preprocessing; run_preprocessing()"
```
- Loads raw data, cleans, handles missing values and outliers
- Saves: `data\processed\cleaned.csv`

---

## Step 5: Exploratory Data Analysis (EDA)

1. Open Jupyter:
   ```bash
   jupyter notebook notebooks\01_EDA.ipynb
   ```
2. Run all cells (Cell → Run All)
3. Outputs in `reports\figures\`:
   - missing_heatmap.png
   - monthly_trends.png
   - distributions.png
   - correlation_heatmap.png
   - seasonality.png

---

## Step 6: Feature Engineering & Training

```bash
python -c "from src.train import run_training; run_training()"
```
- Builds features (lags, rolling means, time features)
- Trains: Linear Regression, Random Forest, Gradient Boosting, XGBoost
- Saves: `models\best_model.pkl`, `scaler.pkl`, `feature_columns.json`, `training_config.json`
- Saves: `reports\model_comparison.csv`

---

## Step 7: Model Evaluation

```bash
python -c "from src.evaluate import run_evaluation; run_evaluation()"
```
- Computes MAE, RMSE, R²
- Saves: `reports\metrics.json`, `reports\figures\residual_analysis.png`

---

## Step 8: Test Prediction API

```python
# In Python
from src.predict import predict_next_month
bills = [
    {"month": "2024-01", "electricity": 5000, "water": 800, "telecom": 2000, "total": 7800},
    {"month": "2024-02", "electricity": 5200, "water": 850, "telecom": 2100, "total": 8150},
]
result = predict_next_month(bills)
print(result)  # total, electricity, water, telecom, confidence
```

---

## Step 9: Database Setup

The Flask app creates the database automatically on first run. For manual setup:
```bash
# SQLite (default)
sqlite3 instance\utility.db < database\schema.sql
```

---

## Step 10: Create Admin User

```bash
python scripts\create_admin.py
```
- Username: admin (or your choice)
- Password: admin123 (or your choice)

---

## Step 11: Start the Web Application

```bash
python run.py
```
- Open: **http://localhost:5000**
- Register a new user or login as admin
- Add bills, set budget, run predictions, view reports

---

## Step 12: Using the Web App

| Feature | How to Use |
|---------|------------|
| **Add bills** | Bills → Add Bill |
| **Predict** | Predict → Get Prediction |
| **Budget** | Budget → Set monthly amount |
| **Pay** | Dashboard → Pay button on a bill |
| **Export** | Export dropdown → CSV or PDF |
| **Admin** | Login as admin → Admin menu |

---

## One-Command Pipeline

To run steps 3–7 in one go:
```bash
python scripts\run_pipeline.py
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No dataset found | Ensure `data\raw\My Home dataset new 1.xlsx` exists |
| Column not found | Check column names in your Excel; system supports flexible naming (Month, Electricity, etc.) |
| Model not found | Run `python -c "from src.train import run_training; run_training()"` first |
| Flask won't start | Check `pip install -r requirements.txt` completed |
