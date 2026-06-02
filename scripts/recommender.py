"""
recommender.py
Bluestock Fintech – Mutual Fund Analytics Platform
Rule-based + scoring mutual fund recommender.

Input  : Risk Appetite (Low / Moderate / High)
Output : Top 3 Mutual Fund Recommendations with rationale
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path

log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"

# ── Risk profile mappings ──────────────────────────────────────────────────────
RISK_PROFILE = {
    "Low": {
        "categories":       ["Debt", "Liquid", "Overnight", "Ultra Short Duration",
                             "Low Duration", "Money Market", "Arbitrage"],
        "risk_grades":      ["Low", "Moderately Low"],
        "max_std_dev":      8.0,
        "min_sharpe":       None,
        "return_weight":    0.2,
        "sharpe_weight":    0.4,
        "drawdown_weight":  0.4,
    },
    "Moderate": {
        "categories":       ["Hybrid", "Balanced Advantage", "Equity Savings",
                             "Conservative Hybrid", "Multi Asset Allocation",
                             "Flexi Cap", "Large Cap"],
        "risk_grades":      ["Moderately Low", "Moderate", "Moderately High"],
        "max_std_dev":      18.0,
        "min_sharpe":       0.3,
        "return_weight":    0.35,
        "sharpe_weight":    0.40,
        "drawdown_weight":  0.25,
    },
    "High": {
        "categories":       ["Equity", "Mid Cap", "Small Cap", "Sectoral",
                             "Thematic", "ELSS", "Value", "Contra",
                             "Large & Mid Cap", "Multi Cap"],
        "risk_grades":      ["Moderately High", "High", "Very High"],
        "max_std_dev":      None,
        "min_sharpe":       0.5,
        "return_weight":    0.50,
        "sharpe_weight":    0.35,
        "drawdown_weight":  0.15,
    },
}


def load_data():
    """Load scheme performance and fund master data."""
    try:
        perf = pd.read_csv(PROC / "scheme_performance_clean.csv")
    except FileNotFoundError:
        perf = pd.read_csv(BASE / "data" / "raw" / "07_scheme_performance.csv")

    try:
        master = pd.read_csv(PROC / "fund_master_clean.csv")
    except FileNotFoundError:
        master = pd.read_csv(BASE / "data" / "raw" / "01_fund_master.csv")

    df = perf.merge(master[["amfi_code","risk_category","launch_date"]],
                    on="amfi_code", how="left")
    return df


def filter_by_risk(df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    """Filter funds based on risk profile."""
    filtered = df.copy()

    # Category filter (broad match)
    cats = profile["categories"]
    cat_mask = filtered["category"].str.contains("|".join(cats), case=False, na=False)
    filtered = filtered[cat_mask]

    # Risk grade filter
    if profile["risk_grades"]:
        grade_mask = filtered["risk_grade"].str.contains(
            "|".join(profile["risk_grades"]), case=False, na=False
        )
        filtered = filtered[grade_mask]

    # Std dev cap
    if profile["max_std_dev"] is not None:
        filtered = filtered[
            (filtered["std_dev_ann_pct"].isna()) |
            (filtered["std_dev_ann_pct"] <= profile["max_std_dev"])
        ]

    # Minimum Sharpe
    if profile["min_sharpe"] is not None:
        filtered = filtered[
            (filtered["sharpe_ratio"].isna()) |
            (filtered["sharpe_ratio"] >= profile["min_sharpe"])
        ]

    return filtered


def score_funds(df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    """Compute composite score for filtered funds."""
    df = df.copy()

    # Normalise key metrics to [0, 1] range
    def norm(series: pd.Series, ascending: bool = True) -> pd.Series:
        mn, mx = series.min(), series.max()
        if mx == mn:
            return pd.Series(0.5, index=series.index)
        normalized = (series - mn) / (mx - mn)
        return normalized if ascending else 1 - normalized

    rw = profile["return_weight"]
    sw = profile["sharpe_weight"]
    dw = profile["drawdown_weight"]

    df["return_score"]   = norm(df["return_3yr_pct"].fillna(df["return_1yr_pct"].fillna(0)))
    df["sharpe_score"]   = norm(df["sharpe_ratio"].fillna(0))
    df["drawdown_score"] = norm(df["max_drawdown_pct"].fillna(-20), ascending=False)  # less negative = better

    df["composite_score"] = (
        rw * df["return_score"] +
        sw * df["sharpe_score"] +
        dw * df["drawdown_score"]
    )

    return df.sort_values("composite_score", ascending=False)


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    """
    Main recommendation function.

    Parameters
    ----------
    risk_appetite : "Low", "Moderate", or "High"
    top_n         : Number of recommendations to return (default 3)

    Returns
    -------
    DataFrame with top_n fund recommendations and rationale columns
    """
    risk_appetite = risk_appetite.strip().title()
    if risk_appetite not in RISK_PROFILE:
        raise ValueError(f"Invalid risk appetite '{risk_appetite}'. Choose: Low, Moderate, High")

    profile = RISK_PROFILE[risk_appetite]
    df      = load_data()

    filtered = filter_by_risk(df, profile)
    if filtered.empty:
        log.warning("No funds matched filters – relaxing category constraint.")
        filtered = df  # fallback to all funds

    scored = score_funds(filtered, profile)
    top    = scored.head(top_n).copy()

    # Build output
    output_cols = [
        "amfi_code", "scheme_name", "fund_house", "category", "plan",
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "sharpe_ratio", "sortino_ratio", "max_drawdown_pct",
        "aum_crore", "expense_ratio_pct", "morningstar_rating",
        "risk_grade", "composite_score",
    ]
    output_cols = [c for c in output_cols if c in top.columns]
    result = top[output_cols].reset_index(drop=True)
    result.index += 1   # 1-based ranking

    return result


def print_recommendations(risk_appetite: str) -> None:
    """Pretty-print recommendations to console."""
    print(f"\n{'='*60}")
    print(f"  Bluestock MF Recommender – Risk Appetite: {risk_appetite.upper()}")
    print(f"{'='*60}")

    try:
        recs = recommend(risk_appetite)
    except Exception as e:
        print(f"  Error: {e}")
        return

    for rank, row in recs.iterrows():
        print(f"\n  #{rank}  {row.get('scheme_name','N/A')}")
        print(f"       Fund House   : {row.get('fund_house','N/A')}")
        print(f"       Category     : {row.get('category','N/A')} ({row.get('plan','N/A')})")
        print(f"       1Y / 3Y Ret  : {row.get('return_1yr_pct','–')}% / {row.get('return_3yr_pct','–')}%")
        print(f"       Sharpe Ratio : {row.get('sharpe_ratio','–')}")
        print(f"       Max Drawdown : {row.get('max_drawdown_pct','–')}%")
        print(f"       AUM (Cr)     : ₹{row.get('aum_crore','–'):,}")
        print(f"       Score        : {row.get('composite_score',0):.4f}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    appetite = sys.argv[1] if len(sys.argv) > 1 else "Moderate"
    print_recommendations(appetite)
    # Also save CSV
    recs = recommend(appetite)
    out  = PROC / f"recommendations_{appetite.lower()}.csv"
    recs.to_csv(out, index=True, index_label="rank")
    print(f"Recommendations saved: {out}")
