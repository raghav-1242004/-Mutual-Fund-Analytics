"""
run_pipeline.py
Bluestock Fintech – Mutual Fund Analytics Platform
Master orchestrator: runs ETL → Metrics → Recommender in sequence.
"""

import logging
import sys
import time
from pathlib import Path

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from etl_pipeline    import run as run_etl
from compute_metrics import compute_fund_scorecard
from recommender     import recommend

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/run_pipeline.log", mode="a"),
    ],
)
log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"


def main():
    start = time.time()
    log.info("╔══════════════════════════════════════════╗")
    log.info("║  Bluestock MF Capstone – Full Pipeline   ║")
    log.info("╚══════════════════════════════════════════╝")

    # Step 1 – ETL
    log.info("STEP 1: Running ETL pipeline …")
    cleaned = run_etl()
    log.info("ETL complete.\n")

    # Step 2 – Compute metrics
    log.info("STEP 2: Computing fund performance scorecard …")
    try:
        nav   = cleaned["nav_history"]
        bench = cleaned["benchmark_indices"]
        scorecard = compute_fund_scorecard(nav, bench)
        scorecard.to_csv(PROC / "fund_scorecard.csv", index=False)
        log.info(f"Scorecard saved ({len(scorecard)} funds).\n")
    except Exception as e:
        log.error(f"Scorecard computation failed: {e}")

    # Step 3 – Recommendations
    log.info("STEP 3: Generating fund recommendations …")
    for appetite in ["Low", "Moderate", "High"]:
        try:
            recs = recommend(appetite)
            out  = PROC / f"recommendations_{appetite.lower()}.csv"
            recs.to_csv(out, index=True, index_label="rank")
            log.info(f"  [{appetite}] Top 3 recommendations saved → {out.name}")
        except Exception as e:
            log.warning(f"  [{appetite}] Recommendation failed: {e}")
    log.info("")

    elapsed = time.time() - start
    log.info(f"╔══════════════════════════════════════════╗")
    log.info(f"║  Pipeline COMPLETE in {elapsed:.1f}s              ║")
    log.info(f"╚══════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
