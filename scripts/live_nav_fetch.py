"""
live_nav_fetch.py
Bluestock Fintech – Mutual Fund Analytics Platform
Fetches live NAV data from mfapi.in for all AMFI codes in fund_master.
"""

import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path

import urllib.request
import urllib.error

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/live_nav_fetch.log", mode="a"),
    ],
)
log = logging.getLogger(__name__)

BASE_URL = "https://api.mfapi.in/mf"
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

OUTPUT_LATEST = BASE_DIR / "data" / "processed" / "live_nav_latest.csv"
OUTPUT_HIST   = BASE_DIR / "data" / "processed" / "live_nav_history.csv"


def fetch_fund_data(amfi_code: int, retries: int = 3, delay: float = 1.0) -> dict | None:
    """
    Fetch NAV data for a single fund from mfapi.in.

    Returns parsed JSON dict or None on failure.
    """
    url = f"{BASE_URL}/{amfi_code}"
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BluestockMF/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read()
            data = json.loads(raw)
            log.debug(f"Fetched AMFI {amfi_code} – status: {data.get('status')}")
            return data
        except urllib.error.HTTPError as e:
            log.warning(f"HTTP {e.code} for AMFI {amfi_code} (attempt {attempt})")
        except urllib.error.URLError as e:
            log.warning(f"URL error for AMFI {amfi_code}: {e.reason} (attempt {attempt})")
        except Exception as e:
            log.error(f"Unexpected error for AMFI {amfi_code}: {e}")
        if attempt < retries:
            time.sleep(delay * attempt)
    return None


def parse_latest(amfi_code: int, data: dict) -> dict | None:
    """Extract the latest NAV record from mfapi response."""
    try:
        meta  = data.get("meta", {})
        navs  = data.get("data", [])
        if not navs:
            return None
        latest = navs[0]
        return {
            "amfi_code":   amfi_code,
            "scheme_name": meta.get("scheme_name", ""),
            "fund_house":  meta.get("fund_house", ""),
            "scheme_type": meta.get("scheme_type", ""),
            "nav":         latest.get("nav", ""),
            "date":        latest.get("date", ""),
            "fetched_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        log.error(f"Parse error for AMFI {amfi_code}: {e}")
        return None


def parse_history(amfi_code: int, data: dict) -> list[dict]:
    """Extract full NAV history from mfapi response."""
    try:
        navs = data.get("data", [])
        rows = []
        for entry in navs:
            rows.append({
                "amfi_code": amfi_code,
                "date":      entry.get("date", ""),
                "nav":       entry.get("nav", ""),
            })
        return rows
    except Exception as e:
        log.error(f"History parse error for AMFI {amfi_code}: {e}")
        return []


def get_amfi_codes() -> list[int]:
    """Read AMFI codes from fund_master CSV."""
    path = RAW_DIR / "01_fund_master.csv"
    codes = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                codes.append(int(row["amfi_code"]))
            except (ValueError, KeyError):
                pass
    log.info(f"Found {len(codes)} AMFI codes in fund_master.")
    return codes


def fetch_all(save_history: bool = False, rate_limit: float = 0.3) -> None:
    """
    Main function: fetch live NAV for all funds and save results.

    Parameters
    ----------
    save_history  : If True, also saves full historical NAV data (large file).
    rate_limit    : Seconds to sleep between API calls to avoid throttling.
    """
    codes = get_amfi_codes()
    latest_rows = []
    hist_rows   = []

    log.info(f"Starting NAV fetch for {len(codes)} funds …")
    for i, code in enumerate(codes, 1):
        data = fetch_fund_data(code)
        if data:
            rec = parse_latest(code, data)
            if rec:
                latest_rows.append(rec)
            if save_history:
                hist_rows.extend(parse_history(code, data))
        if i % 10 == 0:
            log.info(f"Progress: {i}/{len(codes)} funds processed")
        time.sleep(rate_limit)

    # Write latest NAV
    if latest_rows:
        keys = list(latest_rows[0].keys())
        with open(OUTPUT_LATEST, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(latest_rows)
        log.info(f"Latest NAV saved: {OUTPUT_LATEST}  ({len(latest_rows)} records)")

    # Write full history (optional)
    if save_history and hist_rows:
        keys = list(hist_rows[0].keys())
        with open(OUTPUT_HIST, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(hist_rows)
        log.info(f"Full history saved: {OUTPUT_HIST}  ({len(hist_rows)} records)")

    log.info("Live NAV fetch complete.")


if __name__ == "__main__":
    fetch_all(save_history=True)
