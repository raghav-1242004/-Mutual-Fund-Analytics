# Bluestock MF Platform – Power BI Dashboard Guide

## Overview

This document describes the four-page Power BI dashboard design for the Bluestock Fintech Mutual Fund Analytics Platform. All source data files are located in `data/processed/`.

---

## Data Sources (Power BI)

| File | Used In |
|------|---------|
| `powerbi_investor_fund_flat.csv` | Pages 1, 3, 4 |
| `powerbi_sip_trends.csv` | Pages 1, 4 |
| `scheme_performance_clean.csv` | Pages 1, 2 |
| `aum_by_fund_house_clean.csv` | Page 1 |
| `category_inflows_clean.csv` | Pages 1, 4 |
| `industry_folio_count_clean.csv` | Pages 1, 4 |
| `fund_scorecard.csv` | Page 2 |
| `benchmark_indices_clean.csv` | Pages 2, 4 |

---

## Page 1 – Industry Overview

**Purpose:** Executive snapshot of the Indian mutual fund industry.

### KPI Cards (Top Row)
- Total Industry AUM (₹ Lakh Crore) — latest month
- Total Active SIP Accounts (Crore)
- Total Unique Investors (from transactions)
- Monthly SIP Inflow (₹ Crore)
- YoY AUM Growth %

### Visuals
1. **Line Chart** – Industry AUM trend (monthly, last 3 years)
2. **Clustered Bar** – Top 10 Fund Houses by AUM
3. **Stacked Area** – Folio count growth (Equity/Debt/Hybrid)
4. **Bar Chart** – Monthly SIP Inflows with YoY growth line
5. **Pie Chart** – Fund category share by AUM

### Filters
- Date Range Slicer
- Fund House Slicer

---

## Page 2 – Fund Performance

**Purpose:** Deep-dive into fund-level risk and return metrics.

### KPI Cards
- Average 3Y Return (%)
- Average Sharpe Ratio
- Average Max Drawdown (%)
- No. of 5-Star Rated Funds

### Visuals
1. **Scatter Chart** – CAGR vs Sharpe Ratio (size = AUM, color = risk grade)
2. **Table** – Fund Ranking Scorecard (top 20: returns, Sharpe, Sortino, drawdown)
3. **Bar Chart** – Alpha Distribution by Category
4. **Line Chart** – Benchmark vs Top Fund NAV (normalised, base 100)
5. **Gauge** – Market Beta distribution

### Filters
- Fund Category
- Risk Grade
- Fund House
- Morningstar Rating

---

## Page 3 – Investor Analytics

**Purpose:** Understand investor demographics, geography, and behaviour.

### KPI Cards
- Total Unique Investors
- Avg Transaction Size (₹)
- SIP Renewal Rate (%)
- Top State by Investment Volume

### Visuals
1. **Map / Filled Map** – State-wise investment heatmap
2. **Donut Chart** – Gender split (Investment ₹)
3. **Bar Chart** – Age Group distribution
4. **Stacked Bar** – Transaction type by city tier
5. **Cohort Heatmap** – Investor retention by acquisition month
6. **Line Chart** – Monthly new investor acquisition trend

### Filters
- State / City Tier
- Age Group
- Gender
- Transaction Type

---

## Page 4 – SIP & Market Trends

**Purpose:** SIP ecosystem analysis and market trend overlays.

### KPI Cards
- Total SIP Inflows Last 12M (₹ Cr)
- SIP AUM (₹ Lakh Cr)
- New SIPs Registered (Lakh)
- Category with Highest Net Inflows

### Visuals
1. **Dual-Axis Line** – SIP Inflow (bar) + YoY Growth % (line)
2. **Stacked Bar** – Category Net Inflows monthly (last 12M)
3. **Area Chart** – NIFTY 50 vs SENSEX performance overlay
4. **Bar Chart** – SIP investor tenure distribution
5. **KPI Trend** – Active SIP accounts growth

### Filters
- Date Range
- Fund Category
- Benchmark Index

---

## Design Guidelines

| Element | Specification |
|---------|--------------|
| Primary Color | #1E3A5F (Bluestock Navy) |
| Accent Color | #F5A623 (Gold) |
| Background | #F8F9FA (Light Grey) |
| Font | Segoe UI, 10-12pt body |
| Chart Border | None (clean style) |
| Grid Lines | Light grey (#E0E0E0) |
| Tooltip | Enabled on all visuals |
| Mobile Layout | Enabled (portrait 360×780) |

---

## Refresh Setup

1. Open Power BI Desktop
2. Get Data → Text/CSV → select each file from `data/processed/`
3. Set up relationships via `amfi_code` (fund_master as central dimension)
4. Schedule refresh if uploading to Power BI Service

---

## Measures (DAX Examples)

```dax
Total AUM (Cr) = SUM(aum_by_fund_house_clean[aum_crore])

Avg Sharpe = AVERAGE(scheme_performance_clean[sharpe_ratio])

SIP YoY Growth % = 
    DIVIDE(
        SUM(monthly_sip_inflows_clean[sip_inflow_crore]) -
        CALCULATE(SUM(monthly_sip_inflows_clean[sip_inflow_crore]),
                  SAMEPERIODLASTYEAR(monthly_sip_inflows_clean[month])),
        CALCULATE(SUM(monthly_sip_inflows_clean[sip_inflow_crore]),
                  SAMEPERIODLASTYEAR(monthly_sip_inflows_clean[month]))
    ) * 100

Outperforming Funds = 
    COUNTROWS(FILTER(scheme_performance_clean,
        scheme_performance_clean[return_3yr_pct] > scheme_performance_clean[benchmark_3yr_pct]
    ))
```
