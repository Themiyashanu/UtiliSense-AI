# Smart Utility Expense Prediction, Budget Alert, and Bill Payment Tracking System

A final-year project for Sri Lankan households to manage **Electricity (CEB)**, **Water (NWSDB)**, and **Telecom (Dialog/Mobitel/SLT)** expenses using ML forecasting and a Flask web application.

## Features

- **Machine Learning**: Regression/time-series forecasting (Linear, Random Forest, Gradient Boosting, XGBoost)
- **Web App**: Register, add bills, predict next month, set budget, payment tracking, export reports
- **Budget Alerts**: Notifications when predicted bill exceeds budget
- **Data Science Pipeline**: EDA, feature engineering, model comparison, saved artifacts

## Project Structure

```
utility/
├── app/                 # Flask application
│   ├── routes/          # Blueprints (auth, bills, predict, budget, etc.)
│   └── models.py        # SQLAlchemy models
├── src/                 # Data science pipeline
│   ├── data_understanding.py
│   ├── data_preprocessing.py
│   ├── features.py
│   ├── train.py
│   ├── evaluate.py
│   └── predict.py
├── data/
│   ├── raw/             # Place "My Home dataset new 1.xlsx" here
│   └── processed/       # cleaned.csv
├── models/              # best_model.pkl, scaler.pkl, etc.
├── notebooks/           # 01_EDA.ipynb
├── reports/figures/     # EDA charts, residual plots
├── database/            # schema.sql
├── templates/
├── scripts/
│   ├── run_pipeline.py  # Full ML pipeline
│   └── create_admin.py  # Create admin user
├── run.py               # Start Flask app
└── requirements.txt
```

## Prerequisites

- **Python 3.13**
- Place your dataset: `data/raw/My Home dataset new 1.xlsx` (or any `.csv`/`.xlsx` in `data/raw/`)

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place dataset**
   - Copy `My Home dataset new 1.xlsx` to `data/raw/`

3. **Run ML pipeline**
   ```bash
   python scripts/run_pipeline.py
   ```

4. **Create admin user**
   ```bash
   python scripts/create_admin.py
   ```

5. **Start Flask app**
   ```bash
   python run.py
   ```
   Open http://localhost:5000

## Detailed Run Instructions

See [QUICKSTART.md](QUICKSTART.md) for step-by-step execution guide.

## Dataset

The system auto-detects CSV or Excel files in `data/raw/`. Expected columns (flexible naming):

- **Month** (YYYY-MM)
- **Electricity** (LKR)
- **Water** (LKR)
- **Telecom** (LKR)
- **Total** or **Total_LKR** (target)

## License

Educational / Final Year Project.
