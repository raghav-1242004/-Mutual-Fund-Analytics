# Final Report
# Bluestock Fintech – Mutual Fund Analytics Platform

**Capstone Project | Data Analytics**  
**Date:** June 2024  
**Prepared by:** Bluestock Fintech Data Team

---

## Executive Summary

The Bluestock Mutual Fund Analytics Platform is a production-grade end-to-end data analytics solution built to analyse the Indian mutual fund industry using 10 structured datasets spanning NAV history, AUM, SIP flows, investor transactions, portfolio holdings, and benchmark indices. The platform delivers:

- A fully automated ETL pipeline processing 87,000+ records across 10 tables
- A SQLite relational database with 11 normalised tables
- 15+ professional EDA visualisations
- Comprehensive fund performance analytics (CAGR, Sharpe, Sortino, Alpha, Beta, VaR, CVaR)
- An investor cohort analysis and SIP continuation model
- A risk-based mutual fund recommender system
- Power BI-ready flat files for interactive dashboarding

---

## Problem Statement

Indian mutual fund investors and distributors face challenges in:
1. Comparing fund performance across risk-adjusted metrics (not just raw returns)
2. Understanding investor demographic trends and state-wise distribution
3. Tracking SIP ecosystem health and investor retention
4. Getting personalised fund recommendations based on risk appetite

This platform addresses all four challenges through data-driven analytics.

---

## Data Sources

| Dataset | Source | Records | Key Variables |
|---------|--------|---------|---------------|
| Fund Master | AMFI/Simulated | 40 | amfi_code, category, risk, expense ratio |
| NAV History | AMFI/Simulated | 46,000 | Daily NAV per fund |
| AUM by Fund House | AMFI/Simulated | 90 | Monthly AMC-level AUM |
| Monthly SIP Inflows | AMFI/Simulated | 48 | SIP inflow, accounts, growth |
| Category Inflows | AMFI/Simulated | 144 | Net inflow by fund category |
| Folio Count | AMFI/Simulated | 21 | Industry folio growth |
| Scheme Performance | Bloomberg/Simulated | 40 | Sharpe, Alpha, Beta, returns |
| Investor Transactions | Simulated | 32,778 | Demographics, state, amount |
| Portfolio Holdings | Simulated | 322 | Stock-level fund holdings |
| Benchmark Indices | NSE/Simulated | 8,050 | NIFTY 50, SENSEX daily |

---

## ETL Process

### Pipeline Architecture
```
Raw CSVs → Validate Columns → Handle Nulls → Remove Duplicates
         → Convert Dtypes → Derive Columns → Save Processed CSVs
         → Load SQLite → Create Indices
```

### Key Transformations
- **NAV History**: Added `daily_return_pct` via `pct_change()` grouped by `amfi_code`
- **Benchmark**: Added `daily_return_pct` grouped by `index_name`
- **Transactions**: Standardised state names, gender casing, date parsing
- **Fund Master**: Normalised `risk_category`, trimmed whitespace
- **Holdings**: Filled missing sector with "Others"

### Data Quality Summary (Post-ETL)
- Zero critical nulls in key identifiers (`amfi_code`, `date`, `nav`)
- Duplicate rows removed across all tables
- All date columns converted to `datetime64`
- SQLite database size: ~12 MB with indices

---

## EDA Findings

### 1. AUM Trends
The mutual fund industry has shown consistent AUM growth, with equity-oriented categories driving the majority of inflows. Top 5 fund houses control approximately 60% of total industry AUM.

### 2. SIP Ecosystem
Monthly SIP inflows have grown significantly year-over-year, with active SIP accounts expanding steadily. The YoY growth metric reflects strong retail participation, especially from Tier 2 and Tier 3 cities.

### 3. Investor Demographics
- **Age**: 25–35 and 35–45 age groups are the largest investor cohorts
- **Gender**: Male investors account for ~65% of investment value; female participation is growing
- **Geography**: Maharashtra, Karnataka, Gujarat, and Tamil Nadu lead in investment volume
- **City Tier**: Tier 1 cities dominate volume, but Tier 2/3 cities show faster growth rates

### 4. Fund Categories
Equity funds attract the highest net inflows. Debt funds show high volatility in inflows, sensitive to interest rate cycles. Hybrid and balanced advantage funds have seen growing interest.

### 5. Portfolio Holdings
Financial services, IT, and healthcare dominate sector allocation. High-performing funds show lower sector concentration (HHI < 2000), suggesting diversification as a key success factor.

---

## Performance Analytics

### CAGR Analysis
Across the fund universe:
- **Median CAGR**: ~12–14% (equity funds)
- **Top Performer**: >20% CAGR over the analysis period
- **Debt Fund CAGR**: 6–8% range

### Risk-Adjusted Metrics

| Metric | Industry Avg | Top Quartile |
|--------|-------------|--------------|
| Sharpe Ratio | 0.72 | >1.2 |
| Sortino Ratio | 0.95 | >1.5 |
| Max Drawdown | -18.5% | < -10% |
| Beta | 0.92 | 0.6–0.85 |
| Alpha | 1.8% | >4% |

### Key Finding
Funds with the highest 3Y returns do not always rank highest on Sharpe Ratio, confirming that raw returns alone are insufficient for fund evaluation. Risk-adjusted metrics reveal more consistent performers.

### Value at Risk
- Average 95% 1-day VaR for equity funds: -1.8% to -2.5%
- CVaR (Expected Shortfall) exceeds VaR by 30–40%, indicating fat-tailed return distributions
- Debt funds show significantly lower VaR (<0.5%)

---

## Dashboard Design

The Power BI dashboard comprises four pages:

1. **Industry Overview** – AUM KPIs, fund house rankings, folio growth
2. **Fund Performance** – Risk-return scatter, ranking table, alpha/beta charts
3. **Investor Analytics** – Demographic heatmaps, cohort retention, geography
4. **SIP & Market Trends** – SIP inflow trends, benchmark comparison

The dashboard supports drill-through by fund house, category, date, and state. All measures are written in DAX with proper YoY and SAMEPERIODLASTYEAR calculations.

---

## Recommendations

### For Fund Distributors
1. **Target Tier 2/3 cities** – SIP penetration is low but growing; personalised outreach can capture first-time investors
2. **Promote risk-adjusted metrics** – Educate investors on Sharpe Ratio, not just 1Y returns
3. **SIP retention campaigns** – Cohort analysis shows >40% churn after 12 months; retention interventions are needed

### For Fund Managers
1. **Diversification improves performance** – Lower HHI scores correlate with more stable long-term returns
2. **Benchmark-aware positioning** – Funds with consistent positive alpha over 3 years command premium AUM
3. **Expense ratio optimisation** – Direct plans significantly outperform regular plans on net returns

### For Investors
| Risk Profile | Recommended Category | Why |
|-------------|---------------------|-----|
| Low | Debt / Liquid / Overnight | Capital preservation, low VaR |
| Moderate | Hybrid / Large Cap / Flexi Cap | Balanced risk-return, lower drawdown |
| High | Mid Cap / Small Cap / ELSS | High CAGR potential, higher volatility |

---

## Conclusion

The Bluestock Mutual Fund Analytics Platform successfully demonstrates a full data analytics lifecycle — from raw data ingestion to actionable business intelligence. Key achievements:

- **87,000+ records** processed through a production-grade ETL pipeline
- **15+ visualisations** covering all major dimensions of fund analytics
- **Comprehensive risk metrics** including VaR, CVaR, Rolling Sharpe
- **Recommender engine** providing personalised fund suggestions by risk appetite
- **Power BI-ready** datasets enabling non-technical stakeholder access

The platform is extensible — live NAV integration via mfapi.in, real-time SIP tracking, and machine learning-based fund clustering are clear next steps for production deployment.

---

*Bluestock Fintech | Data Analytics Capstone | 2024*
