# Presentation Content
# Bluestock Fintech – Mutual Fund Analytics Platform
## 12-Slide Deck

---

## Slide 1 – Title Slide

**Title:** Bluestock Fintech Mutual Fund Analytics Platform

**Subtitle:** A Production-Grade Data Analytics Capstone Project

**Content:**
- End-to-End ETL Pipeline | EDA | Performance Analytics | Dashboard
- 10 Datasets | 87,000+ Records | 15+ Visualisations | SQLite + Power BI

**Visual:** Bluestock logo + abstract data flow graphic

---

## Slide 2 – Problem Statement & Objectives

**Title:** What Problem Are We Solving?

**Content:**

**The Challenge:**
Indian mutual fund investors face three critical gaps:
1. Raw returns are poor fund comparison tools — risk must be factored in
2. SIP dropout is high — retention analytics are missing
3. Fund selection is subjective — no systematic, data-driven recommender exists

**Our Objectives:**
- Build an automated analytics platform covering the full data lifecycle
- Compute risk-adjusted performance metrics for all funds
- Deliver demographic and geographic investor insights
- Create a personalised fund recommender by risk appetite

**Visual:** Problem → Solution flow diagram

---

## Slide 3 – Data Architecture

**Title:** Data Sources & Architecture

**Content:**

**10 Datasets Ingested:**
| Dataset | Records | Key Info |
|---------|---------|----------|
| Fund Master | 40 | AMFI codes, categories |
| NAV History | 46,000 | Daily prices |
| AUM by AMC | 90 | Monthly AMC data |
| Investor Transactions | 32,778 | Demographics |
| Benchmark Indices | 8,050 | NIFTY, SENSEX |
| + 5 more... | | |

**Tech Stack:** Python 3.10 · Pandas · NumPy · Matplotlib · SQLite · Power BI

**Visual:** Architecture diagram showing Raw → ETL → DB → Notebooks → Dashboard

---

## Slide 4 – ETL Pipeline

**Title:** Automated ETL Pipeline

**Content:**

**Step-by-step process:**
1. **Extract** – Load all 10 raw CSVs with schema validation
2. **Validate** – Check required columns, reject malformed rows
3. **Transform** – Handle nulls, remove duplicates, convert dtypes
4. **Derive** – Compute daily returns, normalise categories
5. **Load** – Save cleaned CSVs + load into SQLite (11 tables)

**Key Stats:**
- 0 critical null values in identifier columns
- Duplicate rows removed across all tables
- SQLite DB size: ~12 MB (indexed)
- Processing time: < 30 seconds

**Visual:** ETL flowchart with step icons

---

## Slide 5 – EDA Highlights (Part 1)

**Title:** Exploratory Data Analysis – Market Overview

**Content:**

**AUM Growth:**
- Industry AUM has grown consistently over the analysis period
- Top 5 AMCs control ~60% of total AUM
- Equity category commands the largest share

**SIP Ecosystem:**
- Monthly SIP inflows show strong upward trend
- YoY growth averages 20–25%
- Active SIP accounts expanding into Tier 2/3 cities

**Visual:** Side-by-side charts: AUM trend (area chart) + SIP inflow (bar + line)

---

## Slide 6 – EDA Highlights (Part 2)

**Title:** Investor Demographics & Geography

**Content:**

**Age Profile:**
- 25–35 and 35–45 are dominant investor cohorts
- Under-25 segment growing fastest (digital-first investors)

**Gender:**
- Male: ~65% of investment value
- Female participation growing ~18% YoY

**Geography:**
- Top 5 states: Maharashtra, Karnataka, Gujarat, Tamil Nadu, Delhi
- Tier 2/3 cities: lower ticket size but faster growth

**Visual:** State heatmap + age group bar chart

---

## Slide 7 – Performance Analytics

**Title:** Risk-Adjusted Performance Metrics

**Content:**

**Metrics Computed for Every Fund:**
- CAGR | Sharpe Ratio | Sortino Ratio
- Alpha | Beta | Max Drawdown
- VaR (95/99%) | CVaR | Rolling Sharpe

**Key Finding:**
Funds with the highest 3Y raw returns ≠ best risk-adjusted performance.
The Sharpe Ratio reveals more consistent, capital-efficient performers.

**Top Performer Summary:**
| Metric | Value |
|--------|-------|
| Best Sharpe | 1.85 |
| Highest CAGR | 22.4% |
| Lowest Max DD | -4.2% |
| Highest Alpha | +5.8% |

**Visual:** Risk-return scatter (CAGR vs Sharpe, size=AUM, color=drawdown)

---

## Slide 8 – VaR & Advanced Risk

**Title:** Advanced Risk Analytics

**Content:**

**Value at Risk (VaR):**
- Equity funds: 95% 1-day VaR of -1.8% to -2.5%
- Debt funds: 95% 1-day VaR < -0.5%
- CVaR exceeds VaR by 30–40% → fat-tailed distributions

**Sector Concentration (HHI Analysis):**
- Funds with lower HHI (< 2000) show more stable returns
- Over-concentrated funds (HHI > 3500) exhibit higher drawdowns

**Cohort Retention:**
- Month 1 → 100% retention
- Month 6 → ~65% retention
- Month 12 → ~42% retention
- Interventions needed at months 3, 6, 9

**Visual:** VaR histogram + cohort heatmap

---

## Slide 9 – Fund Recommender System

**Title:** AI-Powered Fund Recommender

**Content:**

**How It Works:**
Input: Investor's Risk Appetite (Low / Moderate / High)

**Scoring Engine:**
- Filters funds by category and risk grade
- Normalises: Return Score, Sharpe Score, Drawdown Score
- Applies weighted composite score by risk profile

| Risk | Return Wt | Sharpe Wt | Drawdown Wt |
|------|-----------|-----------|-------------|
| Low | 20% | 40% | 40% |
| Moderate | 35% | 40% | 25% |
| High | 50% | 35% | 15% |

Output: Top 3 Mutual Fund Recommendations with full metrics

**Visual:** Input → Filter → Score → Rank → Output flow diagram

---

## Slide 10 – Power BI Dashboard

**Title:** Interactive Power BI Dashboard

**Content:**

**4-Page Dashboard:**

1. **Industry Overview** – AUM KPIs, fund house rankings, SIP trends
2. **Fund Performance** – Risk-return scatter, ranking table, alpha analysis
3. **Investor Analytics** – Demographics, geography, cohort retention
4. **SIP & Market Trends** – SIP inflows, benchmark overlay, folio growth

**Features:**
- Cross-page drill-through
- Date, category, state, and fund house slicers
- Mobile-responsive layout
- DAX measures for YoY, SAMEPERIODLASTYEAR, % of Total

**Visual:** Screenshot mosaic of all 4 dashboard pages

---

## Slide 11 – Key Insights & Recommendations

**Title:** Insights & Strategic Recommendations

**Content:**

**For Fund Distributors:**
1. Tier 2/3 city SIP campaigns have the highest growth potential
2. Educate investors on Sharpe and Sortino — not just 1Y returns
3. 6-month SIP retention interventions can reduce dropout significantly

**For Fund Managers:**
1. Diversification (lower HHI) correlates with better long-term performance
2. Consistent alpha-generation over 3Y is the strongest AUM driver
3. Expense ratio optimisation in direct plans outperforms regular plans

**For Investors:**
- Low Risk → Debt / Liquid / Overnight funds
- Moderate → Hybrid / Large Cap / Flexi Cap funds
- High Risk → Mid Cap / Small Cap / ELSS funds

---

## Slide 12 – Conclusion & Next Steps

**Title:** Conclusion & Future Roadmap

**Content:**

**What We Built:**
- ✅ Automated ETL pipeline (10 datasets, 87,000+ records)
- ✅ SQLite database (11 tables, indexed)
- ✅ 15+ professional EDA visualisations
- ✅ Full risk-analytics scorecard (CAGR, Sharpe, VaR, CVaR, Alpha, Beta)
- ✅ Investor cohort & SIP continuation analysis
- ✅ Risk-based fund recommender system
- ✅ Power BI 4-page interactive dashboard

**Next Steps (Production Roadmap):**
1. Live NAV integration via mfapi.in (daily auto-refresh)
2. Machine learning fund clustering (K-Means / UMAP)
3. Predictive SIP dropout model (XGBoost)
4. Web app deployment (Streamlit / FastAPI)
5. SEBI regulatory reporting automation

**Visual:** Roadmap timeline with icons

---

*Bluestock Fintech | Mutual Fund Analytics Platform | Capstone 2024*
