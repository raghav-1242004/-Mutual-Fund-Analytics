"""
compute_metrics.py
Bluestock Fintech – Mutual Fund Analytics Platform
Computes: CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, VaR, CVaR
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path

log = logging.getLogger(__name__)

RISK_FREE_RATE_ANNUAL = 0.065   # 6.5% – RBI repo rate proxy
TRADING_DAYS          = 252


# ── Core metrics ──────────────────────────────────────────────────────────────

def cagr(start_nav: float, end_nav: float, years: float) -> float:
    """Compound Annual Growth Rate."""
    if start_nav <= 0 or years <= 0:
        return np.nan
    return ((end_nav / start_nav) ** (1 / years) - 1) * 100


def sharpe_ratio(returns: pd.Series, risk_free_annual: float = RISK_FREE_RATE_ANNUAL) -> float:
    """Annualised Sharpe Ratio from daily % returns."""
    returns = returns.dropna()
    if len(returns) < 20:
        return np.nan
    rf_daily  = risk_free_annual / TRADING_DAYS
    excess    = returns / 100 - rf_daily
    if excess.std() == 0:
        return np.nan
    return (excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS)


def sortino_ratio(returns: pd.Series, risk_free_annual: float = RISK_FREE_RATE_ANNUAL) -> float:
    """Annualised Sortino Ratio from daily % returns."""
    returns = returns.dropna()
    if len(returns) < 20:
        return np.nan
    rf_daily     = risk_free_annual / TRADING_DAYS
    excess       = returns / 100 - rf_daily
    downside     = excess[excess < 0]
    downside_std = downside.std()
    if downside_std == 0 or np.isnan(downside_std):
        return np.nan
    return (excess.mean() / downside_std) * np.sqrt(TRADING_DAYS)


def max_drawdown(nav_series: pd.Series) -> float:
    """Maximum drawdown in %."""
    nav_series = nav_series.dropna()
    if len(nav_series) < 2:
        return np.nan
    rolling_max = nav_series.cummax()
    drawdown    = (nav_series - rolling_max) / rolling_max * 100
    return drawdown.min()


def beta(fund_returns: pd.Series, bench_returns: pd.Series) -> float:
    """Beta vs benchmark."""
    df = pd.DataFrame({"f": fund_returns, "b": bench_returns}).dropna()
    if len(df) < 20:
        return np.nan
    cov  = np.cov(df["f"], df["b"])
    var_b = cov[1, 1]
    if var_b == 0:
        return np.nan
    return cov[0, 1] / var_b


def alpha(fund_returns: pd.Series, bench_returns: pd.Series,
          risk_free_annual: float = RISK_FREE_RATE_ANNUAL) -> float:
    """Jensen's Alpha (annualised)."""
    b    = beta(fund_returns, bench_returns)
    rf_d = risk_free_annual / TRADING_DAYS
    df   = pd.DataFrame({"f": fund_returns / 100, "b": bench_returns / 100}).dropna()
    if len(df) < 20 or np.isnan(b):
        return np.nan
    alpha_daily = df["f"].mean() - (rf_d + b * (df["b"].mean() - rf_d))
    return alpha_daily * TRADING_DAYS * 100   # annualised %


def value_at_risk(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical VaR at given confidence level (%)."""
    returns = returns.dropna()
    if len(returns) < 30:
        return np.nan
    return np.percentile(returns, (1 - confidence) * 100)


def conditional_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical CVaR (Expected Shortfall) at given confidence level (%)."""
    returns = returns.dropna()
    if len(returns) < 30:
        return np.nan
    var_threshold = value_at_risk(returns, confidence)
    tail = returns[returns <= var_threshold]
    return tail.mean() if len(tail) > 0 else np.nan


def rolling_sharpe(returns: pd.Series, window: int = 63,
                   risk_free_annual: float = RISK_FREE_RATE_ANNUAL) -> pd.Series:
    """Rolling Sharpe Ratio over a given window (default 63 days ≈ 3 months)."""
    rf_daily = risk_free_annual / TRADING_DAYS
    excess   = returns / 100 - rf_daily
    roll_mean = excess.rolling(window).mean()
    roll_std  = excess.rolling(window).std()
    return (roll_mean / roll_std) * np.sqrt(TRADING_DAYS)


# ── Fund-level scorecard ──────────────────────────────────────────────────────

def compute_fund_scorecard(nav_df: pd.DataFrame,
                           bench_df: pd.DataFrame,
                           bench_name: str = "NIFTY 50") -> pd.DataFrame:
    """
    Compute a full scorecard for all funds.

    Parameters
    ----------
    nav_df   : cleaned nav_history DataFrame (amfi_code, date, nav, daily_return_pct)
    bench_df : cleaned benchmark_indices DataFrame
    bench_name : index to use as market benchmark

    Returns
    -------
    DataFrame with one row per fund with all risk/return metrics
    """
    bench = bench_df[bench_df["index_name"] == bench_name].copy()
    bench["date"] = pd.to_datetime(bench["date"])
    bench = bench.set_index("date")["daily_return_pct"].dropna()

    nav_df["date"] = pd.to_datetime(nav_df["date"])
    records = []

    for code, grp in nav_df.groupby("amfi_code"):
        grp = grp.sort_values("date").set_index("date")
        returns = grp["daily_return_pct"].dropna()
        navs    = grp["nav"].dropna()

        if len(navs) < 2:
            continue

        # Date range
        start_date = navs.index.min()
        end_date   = navs.index.max()
        years      = max((end_date - start_date).days / 365.25, 0.01)

        # Align benchmark
        common_idx = returns.index.intersection(bench.index)
        f_ret = returns.reindex(common_idx)
        b_ret = bench.reindex(common_idx)

        row = {
            "amfi_code":       code,
            "start_date":      start_date.date(),
            "end_date":        end_date.date(),
            "start_nav":       round(navs.iloc[0], 4),
            "end_nav":         round(navs.iloc[-1], 4),
            "cagr_pct":        round(cagr(navs.iloc[0], navs.iloc[-1], years), 2),
            "sharpe_ratio":    round(sharpe_ratio(returns), 4),
            "sortino_ratio":   round(sortino_ratio(returns), 4),
            "max_drawdown_pct":round(max_drawdown(navs), 2),
            "beta":            round(beta(f_ret, b_ret), 4),
            "alpha_pct":       round(alpha(f_ret, b_ret), 4),
            "var_95_pct":      round(value_at_risk(returns), 4),
            "cvar_95_pct":     round(conditional_var(returns), 4),
            "volatility_ann_pct": round(returns.std() * np.sqrt(TRADING_DAYS), 4),
            "num_observations":len(returns),
        }
        records.append(row)

    scorecard = pd.DataFrame(records)
    log.info(f"Scorecard computed for {len(scorecard)} funds.")
    return scorecard


# ── Standalone run ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-8s | %(message)s")
    BASE  = Path(__file__).resolve().parent.parent
    PROC  = BASE / "data" / "processed"

    nav   = pd.read_csv(PROC / "nav_history_clean.csv")
    bench = pd.read_csv(PROC / "benchmark_indices_clean.csv")

    scorecard = compute_fund_scorecard(nav, bench)
    out = PROC / "fund_scorecard.csv"
    scorecard.to_csv(out, index=False)
    print(f"Scorecard saved to {out}")
    print(scorecard.head())
