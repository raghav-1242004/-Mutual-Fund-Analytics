"""
etl_pipeline.py
Bluestock Fintech – Mutual Fund Analytics Platform
Complete ETL Pipeline: Load → Validate → Clean → Transform → Save → SQLite
"""

import os
import logging
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/etl_pipeline.log", mode="a", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE   = Path(__file__).resolve().parent.parent
RAW    = BASE / "data" / "raw"
PROC   = BASE / "data" / "processed"
DB     = BASE / "data" / "db" / "bluestock_mf.db"
os.makedirs(PROC, exist_ok=True)
os.makedirs(DB.parent, exist_ok=True)
os.makedirs(BASE / "logs", exist_ok=True)

# ── File registry ─────────────────────────────────────────────────────────────
FILES = {
    "fund_master":          "01_fund_master.csv",
    "nav_history":          "02_nav_history.csv",
    "aum_by_fund_house":    "03_aum_by_fund_house.csv",
    "monthly_sip_inflows":  "04_monthly_sip_inflows.csv",
    "category_inflows":     "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance":   "07_scheme_performance.csv",
    "investor_transactions":"08_investor_transactions.csv",
    "portfolio_holdings":   "09_portfolio_holdings.csv",
    "benchmark_indices":    "10_benchmark_indices.csv",
}

# ── Helper utilities ──────────────────────────────────────────────────────────

def load_csv(name: str, filename: str) -> pd.DataFrame:
    path = RAW / filename
    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")
    df = pd.read_csv(path, low_memory=False)
    log.info(f"Loaded {name}: {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


def validate_columns(df: pd.DataFrame, required: list, table: str) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"[{table}] Missing columns: {missing}")
    log.info(f"[{table}] Column validation passed.")


def drop_duplicates(df: pd.DataFrame, table: str) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        log.warning(f"[{table}] Dropped {removed} duplicate rows.")
    return df


def fill_numeric_nulls(df: pd.DataFrame, cols: list, fill=0) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(fill)
    return df


def to_date(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def save_processed(df: pd.DataFrame, name: str) -> None:
    out = PROC / f"{name}_clean.csv"
    df.to_csv(out, index=False)
    log.info(f"Saved processed file: {out.name}  ({len(df):,} rows)")


# ── Per-table cleaners ────────────────────────────────────────────────────────

def clean_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["amfi_code","fund_house","scheme_name","category","risk_category"], "fund_master")
    df = drop_duplicates(df, "fund_master")
    df = to_date(df, ["launch_date"])
    df = fill_numeric_nulls(df, ["expense_ratio_pct","exit_load_pct","min_sip_amount","min_lumpsum_amount"])
    df["scheme_name"] = df["scheme_name"].str.strip()
    df["fund_house"]  = df["fund_house"].str.strip()
    df["risk_category"] = df["risk_category"].str.strip().str.title()
    log.info("fund_master cleaned.")
    return df


def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["amfi_code","date","nav"], "nav_history")
    df = drop_duplicates(df, "nav_history")
    df = to_date(df, ["date"])
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["nav","date"])
    df = df.sort_values(["amfi_code","date"])
    # daily return
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
    log.info("nav_history cleaned.")
    return df


def clean_aum(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["date","fund_house","aum_crore"], "aum_by_fund_house")
    df = drop_duplicates(df, "aum_by_fund_house")
    df = to_date(df, ["date"])
    df = fill_numeric_nulls(df, ["aum_lakh_crore","aum_crore","num_schemes"])
    log.info("aum_by_fund_house cleaned.")
    return df


def clean_sip(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["month","sip_inflow_crore"], "monthly_sip_inflows")
    df = drop_duplicates(df, "monthly_sip_inflows")
    df = to_date(df, ["month"])
    numeric = ["sip_inflow_crore","active_sip_accounts_crore","new_sip_accounts_lakh",
                "sip_aum_lakh_crore","yoy_growth_pct"]
    df = fill_numeric_nulls(df, numeric)
    log.info("monthly_sip_inflows cleaned.")
    return df


def clean_category_inflows(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["month","category","net_inflow_crore"], "category_inflows")
    df = drop_duplicates(df, "category_inflows")
    df = to_date(df, ["month"])
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce").fillna(0)
    log.info("category_inflows cleaned.")
    return df


def clean_folio(df: pd.DataFrame) -> pd.DataFrame:
    df = drop_duplicates(df, "industry_folio_count")
    df = to_date(df, ["month"])
    numeric_cols = [c for c in df.columns if c != "month"]
    df = fill_numeric_nulls(df, numeric_cols)
    log.info("industry_folio_count cleaned.")
    return df


def clean_scheme_performance(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["amfi_code","scheme_name","return_1yr_pct","sharpe_ratio"], "scheme_performance")
    df = drop_duplicates(df, "scheme_performance")
    numeric_cols = ["return_1yr_pct","return_3yr_pct","return_5yr_pct","benchmark_3yr_pct",
                    "alpha","beta","sharpe_ratio","sortino_ratio","std_dev_ann_pct",
                    "max_drawdown_pct","aum_crore","expense_ratio_pct","morningstar_rating"]
    df = fill_numeric_nulls(df, numeric_cols, fill=np.nan)
    df["risk_grade"] = df["risk_grade"].fillna("Unknown")
    log.info("scheme_performance cleaned.")
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["investor_id","transaction_date","amfi_code","transaction_type","amount_inr"], "investor_transactions")
    df = drop_duplicates(df, "investor_transactions")
    df = to_date(df, ["transaction_date"])
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df = df.dropna(subset=["amount_inr","transaction_date"])
    df["state"]   = df["state"].str.strip().fillna("Unknown")
    df["gender"]  = df["gender"].str.strip().str.title().fillna("Unknown")
    df["kyc_status"] = df["kyc_status"].str.strip().fillna("Unknown")
    log.info("investor_transactions cleaned.")
    return df


def clean_holdings(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["amfi_code","stock_symbol","sector","weight_pct"], "portfolio_holdings")
    df = drop_duplicates(df, "portfolio_holdings")
    df = to_date(df, ["portfolio_date"])
    df = fill_numeric_nulls(df, ["weight_pct","market_value_cr","current_price_inr"])
    df["sector"] = df["sector"].str.strip().fillna("Others")
    log.info("portfolio_holdings cleaned.")
    return df


def clean_benchmark(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, ["date","index_name","close_value"], "benchmark_indices")
    df = drop_duplicates(df, "benchmark_indices")
    df = to_date(df, ["date"])
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    df = df.dropna(subset=["close_value","date"])
    df = df.sort_values(["index_name","date"])
    df["daily_return_pct"] = df.groupby("index_name")["close_value"].pct_change() * 100
    log.info("benchmark_indices cleaned.")
    return df


# ── SQLite Loader ─────────────────────────────────────────────────────────────

def load_to_sqlite(cleaned: dict) -> None:
    log.info(f"Loading data into SQLite: {DB}")
    conn = sqlite3.connect(DB)
    for table_name, df in cleaned.items():
        # Convert datetime cols to strings for SQLite compatibility
        for col in df.select_dtypes(include=["datetime64[ns]","datetimetz"]).columns:
            df[col] = df[col].astype(str)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        log.info(f"  -> {table_name}: {len(df):,} rows loaded")
    conn.close()
    log.info("SQLite load complete.")


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run() -> dict:
    log.info("=" * 60)
    log.info("Bluestock MF Capstone - ETL Pipeline START")
    log.info("=" * 60)

    raw = {name: load_csv(name, fname) for name, fname in FILES.items()}

    cleaners = {
        "fund_master":           clean_fund_master,
        "nav_history":           clean_nav_history,
        "aum_by_fund_house":     clean_aum,
        "monthly_sip_inflows":   clean_sip,
        "category_inflows":      clean_category_inflows,
        "industry_folio_count":  clean_folio,
        "scheme_performance":    clean_scheme_performance,
        "investor_transactions": clean_transactions,
        "portfolio_holdings":    clean_holdings,
        "benchmark_indices":     clean_benchmark,
    }

    cleaned = {}
    for name, df in raw.items():
        try:
            cleaned[name] = cleaners[name](df.copy())
            save_processed(cleaned[name], name)
        except Exception as e:
            log.error(f"[{name}] ETL FAILED: {e}")
            raise

    load_to_sqlite(cleaned)

    log.info("=" * 60)
    log.info("ETL Pipeline COMPLETE")
    log.info("=" * 60)
    return cleaned


if __name__ == "__main__":
    run()
