# Bluestock Fintech – Mutual Fund Analytics Platform
### Capstone Project | Data Analytics & Fintech

---

## Project Overview

A production-grade end-to-end data analytics platform for Indian mutual fund analysis. The platform ingests 10 structured datasets, applies a complete ETL pipeline, performs deep exploratory and performance analytics, and delivers an interactive Power BI-ready dashboard layer.

---

## Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/                     # 10 original CSV datasets
│   ├── processed/               # Cleaned & transformed CSVs + scorecard
│   └── db/
│       └── bluestock_mf.db      # SQLite database (all tables)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py          # Full ETL: load → clean → save → SQLite
│   ├── compute_metrics.py       # CAGR, Sharpe, Sortino, Alpha, Beta, VaR
│   ├── live_nav_fetch.py        # Live NAV from mfapi.in
│   ├── recommender.py           # Risk-based fund recommender
│   └── run_pipeline.py          # Master orchestrator
├── sql/
│   ├── schema.sql               # SQLite schema for all 11 tables
│   └── queries.sql              # 15 analytical queries
├── dashboard/
│   └── dashboard_guide.md       # Power BI dashboard documentation
├── reports/
│   └── *.png                    # 15+ auto-generated charts
├── requirements.txt
├── README.md
├── .gitignore
└── setup_project.bat
```

---

## Datasets

| # | File | Description | Rows |
|---|------|-------------|------|
| 01 | fund_master.csv | Fund metadata, AMC, category, risk | 40 |
| 02 | nav_history.csv | Daily NAV for all funds | ~46,000 |
| 03 | aum_by_fund_house.csv | Monthly AUM by AMC | 90 |
| 04 | monthly_sip_inflows.csv | SIP inflow + folio stats | 48 |
| 05 | category_inflows.csv | Net inflows by fund category | 144 |
| 06 | industry_folio_count.csv | Total industry folios | 21 |
| 07 | scheme_performance.csv | Fund risk/return metrics | 40 |
| 08 | investor_transactions.csv | Individual investor transactions | ~32,778 |
| 09 | portfolio_holdings.csv | Fund stock-level holdings | 322 |
| 10 | benchmark_indices.csv | NIFTY / SENSEX daily data | ~8,050 |

---

## Quick Start

### 1. Setup Environment
```bash
# Windows
setup_project.bat

# Linux / macOS
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Full Pipeline
```bash
cd scripts
python run_pipeline.py
```

### 3. Launch Notebooks
```bash
cd notebooks
jupyter notebook
```

### 4. Fetch Live NAV (requires internet)
```bash
cd scripts
python live_nav_fetch.py
```

### 5. Get Fund Recommendations
```bash
cd scripts
python recommender.py Moderate     # Low | Moderate | High
```

---

## Key Analytics

### Performance Metrics Computed
- **CAGR** – Compound Annual Growth Rate
- **Sharpe Ratio** – Risk-adjusted return vs risk-free rate
- **Sortino Ratio** – Downside deviation-adjusted return
- **Alpha** – Excess return vs benchmark (Jensen's Alpha)
- **Beta** – Market sensitivity
- **Max Drawdown** – Worst peak-to-trough loss
- **VaR @ 95/99%** – Value at Risk (Historical)
- **CVaR** – Conditional VaR / Expected Shortfall
- **Rolling Sharpe** – 63-day rolling window

### Visualisations (15+)
1. NAV Trend – Top 5 Funds by AUM
2. Industry AUM Growth Trend
3. Monthly SIP Inflow & YoY Growth
4. Category Net Inflows
5. Investor Age Distribution
6. Gender Investment Split
7. State-wise Investment Heatmap
8. Portfolio Sector Allocation
9. Correlation Matrix – Fund Metrics
10. AUM by Fund House
11. Risk Category Distribution
12. Benchmark Performance (Normalised)
13. Transaction Type Breakdown
14. Folio Count Growth (Stacked)
15. Return Distribution (1Y vs 3Y)
+ Performance analytics charts

---

## Fund Recommender

The rule-based recommender maps investor risk appetite to optimal fund categories and scores funds on a composite metric:

| Risk | Category Focus | Scoring Weights |
|------|---------------|-----------------|
| Low | Debt, Liquid, Overnight | Drawdown 40%, Sharpe 40%, Return 20% |
| Moderate | Hybrid, Large Cap, Flexi Cap | Sharpe 40%, Return 35%, Drawdown 25% |
| High | Mid/Small Cap, ELSS, Thematic | Return 50%, Sharpe 35%, Drawdown 15% |

---

## Power BI Dashboard Pages

1. **Industry Overview** – AUM, folio count, SIP growth KPIs
2. **Fund Performance** – Return rankings, Sharpe, drawdown
3. **Investor Analytics** – Demographics, geography, cohort
4. **SIP & Market Trends** – SIP inflows, benchmark overlay

---

## Technologies

| Layer | Stack |
|-------|-------|
| Data Processing | Python 3.10, Pandas 2.x, NumPy |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Database | SQLite 3 |
| Notebooks | Jupyter Notebook 7.x |
| Dashboard | Power BI Desktop |
| API | mfapi.in (free, no key required) |

---

## Author

**Bluestock Fintech Capstone Project**  
Mutual Fund Analytics Platform  
© 2024 Bluestock Fintech
