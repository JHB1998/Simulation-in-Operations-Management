"""
Half-width analysis for FermaCore replication CSVs.
Usage:
    python halfwidth_analysis.py                          # baseline
    python halfwidth_analysis.py FermaCore_dryer2.csv    # any scenario CSV
"""

import sys
import math
import csv
from pathlib import Path

# ---------- configuration ----------
ALPHA = 0.05          # 95 % CI
REL_TARGET = 0.05     # 5 % relative half-width target for N-sizing

KPIS = [
    ("bottlesShipped",    "Bottles shipped",       "bottles"),
    ("batchesShipped",    "Batches shipped",        "batches"),
    ("batchesScrapped",   "Batches scrapped",       "batches"),
    ("scrapRate",         "Scrap rate",             "—"),
    ("meanFlowTime",      "Mean flow time",         "h"),
    ("maxFlowTime",       "Max flow time",          "h"),
    ("flowTimeStd",       "Flow time std dev",      "h"),
    ("avgWIP",            "Avg WIP",                "batches"),
    ("dryerUtil",         "Dryer utilisation",      "—"),
    ("cleaningTeamUtil",  "Cleaning team util.",    "—"),
    ("packagingUtil",     "Packaging util.",        "—"),
]

# ---------- t-table (two-tailed 95 %, df = n-1) ----------
# scipy not required — small lookup + fallback to 1.96
T_TABLE = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447,  7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980,
}

def t_crit(df):
    if df in T_TABLE:
        return T_TABLE[df]
    # linear interpolation between bracketing values
    keys = sorted(T_TABLE.keys())
    for i in range(len(keys) - 1):
        if keys[i] < df < keys[i + 1]:
            lo, hi = keys[i], keys[i + 1]
            frac = (df - lo) / (hi - lo)
            return T_TABLE[lo] + frac * (T_TABLE[hi] - T_TABLE[lo])
    return 1.96  # large df


def load_csv(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    return rows


def stats(values):
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return n, mean, 0.0, 0.0, 0.0, 0.0, None
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    s = math.sqrt(var)
    tc = t_crit(n - 1)
    hw = tc * s / math.sqrt(n)
    rel_hw = hw / abs(mean) if mean != 0 else float("inf")
    # N required for 5 % relative half-width (using current s as estimate)
    target_hw = REL_TARGET * abs(mean)
    n_req = math.ceil((tc * s / target_hw) ** 2) if target_hw > 0 else None
    return n, mean, s, tc, hw, rel_hw, n_req


def analyse(csv_path):
    rows = load_csv(csv_path)
    n_reps = len(rows)
    print(f"\n{'=' * 72}")
    print(f"  Half-width analysis  —  {Path(csv_path).name}  (N = {n_reps} reps)")
    print(f"  Confidence level: {int((1-ALPHA)*100)}%   |   Target: ±{int(REL_TARGET*100)}% of mean")
    print(f"{'=' * 72}")

    col_w = [28, 9, 11, 9, 9, 10, 8]
    header = (
        f"{'KPI':<{col_w[0]}}"
        f"{'Mean':>{col_w[1]}}"
        f"{'Std dev':>{col_w[2]}}"
        f"{'t*':>{col_w[3]}}"
        f"{'Half-w':>{col_w[4]}}"
        f"{'Rel h-w':>{col_w[5]}}"
        f"{'N req':>{col_w[6]}}"
    )
    print(header)
    print("-" * sum(col_w))

    results = {}
    for col, label, unit in KPIS:
        try:
            values = [float(r[col]) for r in rows]
        except KeyError:
            continue
        n, mean, s, tc, hw, rel_hw, n_req = stats(values)
        flag = "  <-- sizing KPI" if col == "bottlesShipped" else ""
        n_req_str = str(n_req) if n_req is not None else "—"
        print(
            f"{label:<{col_w[0]}}"
            f"{mean:>{col_w[1]}.2f}"
            f"{s:>{col_w[2]}.3f}"
            f"{tc:>{col_w[3]}.3f}"
            f"{hw:>{col_w[4]}.3f}"
            f"{rel_hw:>{col_w[5]}.1%}"
            f"{n_req_str:>{col_w[6]}}"
            f"{flag}"
        )
        results[col] = dict(n=n, mean=mean, s=s, hw=hw, rel_hw=rel_hw, n_req=n_req)

    print("-" * sum(col_w))
    print(f"\n  Current N={n_reps}. Sufficient if all N_req <= {n_reps}.")
    bottleneck_util = {
        "dryer":        results.get("dryerUtil",       {}).get("mean", 0),
        "cleaning team":results.get("cleaningTeamUtil",{}).get("mean", 0),
        "packaging":    results.get("packagingUtil",   {}).get("mean", 0),
    }
    bottleneck = max(bottleneck_util, key=bottleneck_util.get)
    print(f"  Bottleneck (highest mean util): {bottleneck} "
          f"({bottleneck_util[bottleneck]:.1%})")
    print()
    return results


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "test_data/FermaCore_baseline.csv"
    base = Path(__file__).parent / csv_file
    if not base.exists():
        print(f"File not found: {base}")
        sys.exit(1)
    analyse(str(base))
