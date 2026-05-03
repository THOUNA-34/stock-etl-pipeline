# 🚀 Stock Market ETL Pipeline
### *A Production-Style Data Engineering Project — Built from Scratch in Python*

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Dashboard-Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![yfinance](https://img.shields.io/badge/Data-Yahoo%20Finance-720E9E?style=flat-square&logo=yahoo&logoColor=white)
![Status](https://img.shields.io/badge/Pipeline-Passing-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Domain](https://img.shields.io/badge/Domain-Financial%20Data%20Science-FF6B6B?style=flat-square)

---

> **This is not a textbook ETL exercise.**
> This pipeline extracts *live* stock market data directly from Yahoo Finance, runs it through automated quality gates, engineers 14 financial and statistical features used in real ML models, stores everything in a structured data warehouse, and delivers a 6-chart interactive analytics dashboard — all from a single command.

---

## 📊 Dashboard Preview

![Dashboard](output/dashboard.png)

> *Dark-theme interactive dashboard generated automatically by the pipeline. Open `output/dashboard.html` in any browser to explore with hover, zoom, and pan.*

---

## 🧠 What This Project Is About

Most ETL pipelines just move data from point A to point B. This one is built from a **Data Science perspective** — every transformation stage is designed to make the data **ML-ready**, not just storage-ready.

The pipeline tracks **5 major US tech stocks** across the full calendar year 2024:

| Ticker | Company | Sector |
|--------|---------|--------|
| `AAPL` | Apple Inc. | Consumer Technology |
| `GOOGL` | Alphabet (Google) | Cloud & Advertising |
| `TSLA` | Tesla Inc. | EV & Clean Energy |
| `MSFT` | Microsoft | Enterprise Software |
| `AMZN` | Amazon.com | E-Commerce & Cloud |

Every feature engineered in the Transform stage — moving averages, RSI, volatility, anomaly scores — is a direct input to stock price prediction and portfolio risk models in real financial ML systems.

---

## 🏗️ Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     STOCK MARKET ETL PIPELINE v1.0                      │
└──────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐       ┌──────────────┐       ┌────────────────┐
  │   EXTRACT   │──────▶│   VALIDATE   │──────▶│   TRANSFORM    │
  │             │       │              │       │                │
  │ Yahoo Finance│      │  6 Quality   │       │ 14 Features    │
  │ Live API    │       │  Gate Checks │       │ Engineered     │
  │ 5 Stocks    │       │  Fail = HALT │       │ Cleaning +     │
  │ ~1,260 rows │       │  Pass = GO   │       │ Enrichment     │
  └─────────────┘       └──────────────┘       └───────┬────────┘
                                                        │
                                              ┌─────────▼────────┐
                                              │      LOAD        │
                                              │                  │
                                              │ SQLite Warehouse │
                                              │ stock_facts table│
                                              │ stock_summary view│
                                              └─────────┬────────┘
                                                        │
                                              ┌─────────▼────────┐
                                              │    DASHBOARD     │
                                              │                  │
                                              │ Interactive HTML │
                                              │ High-Res PNG     │
                                              │ 6 Chart Output   │
                                              └──────────────────┘
```

---

## 📦 Where the Data Comes From

**Source: Yahoo Finance Historical Market Data**
- Accessed via the `yfinance` Python library — no manual downloads, no static CSVs
- Pipeline fetches **live data every time it runs** — always current
- Data period: **January 1, 2024 → December 31, 2024** (full trading year)
- ~252 trading days × 5 stocks = **~1,260 raw rows** extracted

**Raw columns from Yahoo Finance:**

| Column | Description |
|--------|-------------|
| `date` | The trading day |
| `open` | Price at market open |
| `high` | Highest price of the day |
| `low` | Lowest price of the day |
| `close` | Price at market close ← primary metric |
| `volume` | Total shares traded that day |

---

## ⚙️ What Happens at Each Stage

### 🟡 Stage 1 — EXTRACT
- Connects to Yahoo Finance API for each of the 5 tickers
- Downloads full-year OHLCV data with a live animated progress bar
- Tags each row with `ticker` and `source` columns
- Merges all 5 stock dataframes into one unified dataset
- Logs row counts per stock to the audit log

### 🔵 Stage 2 — VALIDATE *(Data Quality Gate)*
The pipeline runs 6 automated checks. If **any check fails**, the pipeline halts immediately — no bad data enters the warehouse.

| Check | Threshold | Purpose |
|-------|-----------|---------|
| Minimum row count | ≥ 100 rows | Ensures extraction wasn't empty |
| Null rate — `close` | ≤ 2% | Closing price is the core metric |
| Null rate — `volume` | ≤ 2% | Volume validates market activity |
| Null rate — `ticker` | ≤ 2% | Every row must be identifiable |
| Negative prices | = 0 | Prices cannot be negative |
| All tickers present | All 5 | No stock was silently skipped |

### 🟣 Stage 3 — TRANSFORM *(Feature Engineering)*
This is the Data Science core of the pipeline. 10 transformation steps run in sequence:

**Data Cleaning:**
- Type casting — all columns enforced to correct dtypes
- Date parsing — invalid dates dropped
- Deduplication — same stock + same date = one row only
- Null handling — missing volumes filled with 0

**Financial Features Engineered:**

| Feature | Formula / Method | ML Use Case |
|---------|-----------------|-------------|
| `ma_7` | 7-day rolling mean of close | Short-term momentum signal |
| `ma_30` | 30-day rolling mean of close | Long-term trend direction |
| `rsi_14` | Relative Strength Index, 14-day | Overbought/oversold detection |
| `volatility_20d` | 20-day rolling standard deviation | Risk and uncertainty measure |
| `price_zscore` | Z-score vs 30-day rolling mean | Statistical outlier detection |
| `is_anomaly` | 1 if \|zscore\| > 3, else 0 | Extreme event flag |
| `daily_return` | Pct change in close day-over-day | Return distribution modelling |

**Time Features:**
`year`, `month`, `quarter`, `day_of_week` — extracted for seasonality analysis

**Audit:**
`etl_timestamp` — UTC timestamp of when this row was processed

### 🟢 Stage 4 — LOAD
- Writes all 1,260+ enriched rows to SQLite in 300-row chunks
- Creates `stock_facts` table — the main fact table
- Creates `stock_summary` analytics view — auto-aggregates:
  - Year high / low / average close
  - Average daily return %
  - Average volatility score
  - Average RSI reading
  - Total anomalies detected per stock

### 🔵 Stage 5 — DASHBOARD
Two outputs generated automatically:

**`output/dashboard.html`** — Interactive Plotly dashboard:
- Closing price + MA30 trend lines (all 5 stocks)
- Daily trading volume comparison
- RSI with overbought (70) / oversold (30) reference lines
- 20-day volatility curves
- Monthly average closing price heatmap
- Full-year % return by stock

**`output/dashboard.png`** — High-resolution 1600×1100px static image for reports

---

## ✨ Key Features

- **Live data, not static files** — fetches real market data on every run
- **Fail-fast quality gate** — bad data never reaches the warehouse
- **14 engineered features** — pipeline output is ML-ready, not just storage-ready
- **Colorful terminal UI** — stage-by-stage progress with `rich` library
- **Chunked database writes** — production-grade loading technique
- **Dual dashboard output** — interactive HTML + high-res PNG
- **Full audit logging** — every run timestamped in `logs/pipeline.log`
- **Modular architecture** — each stage is an independent, testable module

---

## 📁 Project Structure

```
stock-etl-pipeline/
│
├── config.py           # Central config — stocks, dates, paths, thresholds
├── extract.py          # Stage 1 — Live data pull from Yahoo Finance API
├── validate.py         # Stage 2 — Automated data quality gate (6 checks)
├── transform.py        # Stage 3 — Feature engineering (14 new columns)
├── load.py             # Stage 4 — SQLite warehouse loader + summary view
├── dashboard.py        # Stage 5 — Plotly dashboard generator (HTML + PNG)
├── run_pipeline.py     # Master orchestrator — runs all 5 stages in sequence
│
├── requirements.txt    # All Python dependencies
├── .gitignore          # Excludes venv, DB files, cache
│
├── output/
│   ├── dashboard.html  # Interactive dark-theme dashboard (open in browser)
│   ├── dashboard.png   # High-res static chart for reports
│   └── stock_warehouse.db  # SQLite data warehouse (gitignored)
│
└── logs/
    └── pipeline.log    # Audit trail — every stage, every run, timestamped
```

---

## 🗄️ Database Schema

**Table: `stock_facts`** — 1,260+ rows, 20 columns

```sql
SELECT date, ticker, open, high, low, close, volume,
       ma_7, ma_30, rsi_14, volatility_20d,
       price_zscore, is_anomaly, daily_return,
       year, month, quarter, day_of_week,
       source, etl_timestamp
FROM stock_facts;
```

**View: `stock_summary`** — auto-aggregated analytics per stock

```sql
SELECT ticker, total_trading_days,
       year_low, year_high, avg_close,
       avg_daily_return_pct, avg_volatility,
       avg_rsi, total_anomalies
FROM stock_summary;
```

---

## ⚡ Setup & Run

```bash
git clone https://github.com/YOUR_USERNAME/stock-etl-pipeline.git
cd stock-etl-pipeline

python3 -m venv venv
source venv/bin/activate          # Linux 
venv\Scripts\activate             # Windows

pip install -r requirements.txt

python3 run_pipeline.py

xdg-open output/dashboard.html   # Linux
```

---

## 📈 Pipeline Output Summary

| Metric | Value |
|--------|-------|
| Data Source | Yahoo Finance (Live API) |
| Stocks Tracked | 5 — AAPL, GOOGL, TSLA, MSFT, AMZN |
| Data Period | Full Year 2024 |
| Raw Rows Extracted | ~1,260 |
| Quality Checks Run | 6 automated gates |
| Features Engineered | 14 new columns |
| Final Rows Loaded | ~1,255 (after cleaning) |
| Dashboard Charts | 6 interactive charts |
| Typical Runtime | 4–8 seconds |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.10+ | Core pipeline |
| Data Source | `yfinance` | Live Yahoo Finance API |
| Data Processing | `pandas`, `numpy` | Cleaning & feature engineering |
| Terminal UI | `rich` | Colorful progress bars & panels |
| Visualization | `plotly` | Interactive dashboard |
| Database | SQLite | Lightweight data warehouse |
| Image Export | `kaleido` | PNG rendering from Plotly |
| IDE | VS Code | Development environment |

---

## 🔬 Why This is Data Science, Not Just ETL

| Standard ETL | This Pipeline |
|---|---|
| Moves data from A to B | Moves data AND makes it ML-ready |
| Clean = remove nulls | Clean = validate, engineer, enrich |
| Output = rows in a table | Output = feature store for models |
| End goal = storage | End goal = insight + model input |

Every engineered feature — RSI, moving averages, volatility, z-score anomaly detection — is a direct input to financial machine learning models for price prediction, portfolio optimization, and risk management.

---

## 👤 Author

**Thouna Khaidem**
B.E. — Artificial Intelligence & Data Science  
**Sreeram M**
B.E. — Artificial Intelligence & Data Science  
**Nivedhita**
B.E. — Artificial Intelligence & Data Science  
**Manjunath**
B.E. — Artificial Intelligence & Data Science


---

## 📄 License

This project is licensed under the MIT License — free to use, modify, and distribute with attribution.
