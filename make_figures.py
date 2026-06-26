"""
Generate the data-ready report figures for FermaCore (testV2.0).

Outputs (vector PDF, for Overleaf) to figures/ (copy into the report repo's figures/):
    fig_throughput.pdf   - bottlesShipped per scenario, 95 % CI error bars
    fig_utilisation.pdf  - dryer / cleaning / packaging utilisation per scenario
    fig_doe.pdf          - 2^3 DOE: Pareto of effects with significance line

Pure stdlib + matplotlib/numpy. Run from repo root:
    venv/bin/python make_figures.py
"""

import csv
import math
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- 95 % CI half-width (t-table, df = n-1) ----------
T_TABLE = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
    15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980,
}


def t_crit(df):
    if df in T_TABLE:
        return T_TABLE[df]
    keys = sorted(T_TABLE)
    for i in range(len(keys) - 1):
        if keys[i] < df < keys[i + 1]:
            lo, hi = keys[i], keys[i + 1]
            return T_TABLE[lo] + (df - lo) / (hi - lo) * (T_TABLE[hi] - T_TABLE[lo])
    return 1.96


def load(name):
    """Return dict col -> (mean, half-width) for one scenario CSV."""
    rows = list(csv.DictReader(open(DATA / f"FermaCore_{name}.csv")))
    out = {}
    for col in rows[0]:
        try:
            vals = np.array([float(r[col]) for r in rows])
        except ValueError:
            continue
        n = len(vals)
        mean = vals.mean()
        s = vals.std(ddof=1) if n > 1 else 0.0
        hw = t_crit(n - 1) * s / math.sqrt(n) if n > 1 else 0.0
        out[col] = (mean, hw)
    return out


# ---------- scenario set (ordered for narrative) ----------
SCENARIOS = [
    ("baseline",                              "Baseline"),
    ("dryer2",                                "+1 dryer"),
    ("cleanTeam2",                            "+1 clean team"),
    ("packLine4",                             "+1 pack line"),
    ("groupByProduct",                        "Resequence"),
    ("dryer2_cleanTeam2",                     "dryer2+clean2"),
    ("dryer2_cleanTeam2_packLine4",           "dryer2+clean2+pack4"),
    ("queue1",                                "EDD queue"),
    ("queue2",                                "SPT queue"),
    ("i40_scrap0p04",                         "I4.0 (scrap 4%)"),
]

DATAW = {key: load(key) for key, _ in SCENARIOS}
labels = [lab for _, lab in SCENARIOS]

plt.rcParams.update({"font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True})


# =====================================================================
# Figure 1 — Throughput per scenario with 95 % CI
# =====================================================================
def fig_throughput():
    means = np.array([DATAW[k]["bottlesShipped"][0] for k, _ in SCENARIOS])
    hws = np.array([DATAW[k]["bottlesShipped"][1] for k, _ in SCENARIOS])
    base = DATAW["baseline"]["bottlesShipped"][0]

    colors = []
    for k, _ in SCENARIOS:
        if k == "baseline":
            colors.append("#34495e")
        elif k == "i40_scrap0p04":
            colors.append("#27ae60")          # the winner
        else:
            colors.append("#5dade2")

    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(len(SCENARIOS))
    ax.bar(x, means, yerr=hws, capsize=3, color=colors,
           edgecolor="black", linewidth=0.4, error_kw=dict(lw=0.8))
    ax.axhline(base, color="#34495e", ls="--", lw=0.8, alpha=0.6,
               label=f"Baseline = {base:,.0f}")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Bottles shipped per run")
    ax.set_ylim(min(means) * 0.96, max(means) * 1.02)
    ax.set_title("Throughput by scenario (95 % CI)")
    ax.legend(loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(OUT / "fig_throughput.pdf")
    plt.close(fig)
    print("  wrote fig_throughput.pdf")


# =====================================================================
# Figure 2 — Utilisation per scenario (bottleneck shift)
# =====================================================================
def fig_utilisation():
    dryer = np.array([DATAW[k]["dryerUtil"][0] for k, _ in SCENARIOS]) * 100
    clean = np.array([DATAW[k]["cleaningTeamUtil"][0] for k, _ in SCENARIOS]) * 100
    pack = np.array([DATAW[k]["packagingUtil"][0] for k, _ in SCENARIOS]) * 100

    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(len(SCENARIOS))
    w = 0.27
    ax.bar(x - w, dryer, w, label="Dryer", color="#e67e22", edgecolor="black", lw=0.3)
    ax.bar(x, clean, w, label="Cleaning team", color="#3498db", edgecolor="black", lw=0.3)
    ax.bar(x + w, pack, w, label="Packaging", color="#9b59b6", edgecolor="black", lw=0.3)
    ax.axhline(90, color="red", ls=":", lw=0.8, alpha=0.7, label="90 % (bottleneck zone)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Mean utilisation (%)")
    ax.set_ylim(0, 105)
    ax.set_title("Resource utilisation by scenario — bottleneck shifts with capacity")
    ax.legend(loc="lower right", ncol=2, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(OUT / "fig_utilisation.pdf")
    plt.close(fig)
    print("  wrote fig_utilisation.pdf")


# =====================================================================
# Figure 3 — 2^3 DOE: Pareto of effects (dryer x cleaning team x packaging)
# =====================================================================
# corner -> (A, B, C, csv-stem)   coded -1/+1 (A=dryer, B=clean, C=pack)
DOE_CORNERS = {
    "(1)": (-1, -1, -1, "baseline"),
    "a":   (+1, -1, -1, "dryer2"),
    "b":   (-1, +1, -1, "cleanTeam2"),
    "ab":  (+1, +1, -1, "dryer2_cleanTeam2"),
    "c":   (-1, -1, +1, "packLine4"),
    "ac":  (+1, -1, +1, "dryer2_packLine4"),
    "bc":  (-1, +1, +1, "cleanTeam2_packLine4"),
    "abc": (+1, +1, +1, "dryer2_cleanTeam2_packLine4"),
}
DOE_EFFECTS = {
    "C (pack)":  lambda a, b, c: c,
    "B (clean)": lambda a, b, c: b,
    "A (dryer)": lambda a, b, c: a,
    "AB": lambda a, b, c: a * b,
    "AC": lambda a, b, c: a * c,
    "BC": lambda a, b, c: b * c,
    "ABC": lambda a, b, c: a * b * c,
}


def _doe_reps(stem):
    rows = list(csv.DictReader(open(DATA / f"FermaCore_{stem}.csv")))
    return np.array([float(r["bottlesShipped"]) for r in rows])


def fig_doe():
    reps = {c: _doe_reps(stem) for c, (a, b, cc, stem) in DOE_CORNERS.items()}
    ybar = {c: v.mean() for c, v in reps.items()}
    r = len(next(iter(reps.values())))
    ncorners = len(DOE_CORNERS)

    # pooled within-corner variance and common SE of an effect
    sp2 = np.mean([v.var(ddof=1) for v in reps.values()])
    n_half = (ncorners // 2) * r
    se_eff = math.sqrt(sp2 * (2.0 / n_half))
    t_crit = 1.99                                   # ~ t(152, 0.975)
    sig_thresh = t_crit * se_eff

    effects = {}
    for name, sign in DOE_EFFECTS.items():
        hi = [ybar[c] for c in DOE_CORNERS if sign(*DOE_CORNERS[c][:3]) > 0]
        lo = [ybar[c] for c in DOE_CORNERS if sign(*DOE_CORNERS[c][:3]) < 0]
        effects[name] = sum(hi) / len(hi) - sum(lo) / len(lo)

    order = sorted(effects, key=lambda k: abs(effects[k]))   # ascending for barh
    vals = [effects[k] for k in order]
    colors = ["#27ae60" if v > 0 else "#c0392b" for v in vals]

    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    y = np.arange(len(order))
    ax.barh(y, [abs(v) for v in vals], color=colors, edgecolor="black", lw=0.4)
    ax.axvline(sig_thresh, color="black", ls="--", lw=1.0,
               label=f"95 % significance = {sig_thresh:.0f}")
    for yi, v in zip(y, vals):
        ax.text(abs(v) + 12, yi, f"{v:+.0f}", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.set_xlabel("|Effect| on bottles shipped")
    ax.set_title(r"$2^3$ DOE Pareto of effects (dryer $\times$ clean $\times$ pack)")
    ax.legend(loc="lower right", framealpha=0.9)
    ax.margins(x=0.18)
    fig.tight_layout()
    fig.savefig(OUT / "fig_doe.pdf")
    plt.close(fig)
    print("  wrote fig_doe.pdf")
    sig = [k for k in order if abs(effects[k]) > sig_thresh]
    print(f"  2^3 effects (SE={se_eff:.0f}, sig>{sig_thresh:.0f}): "
          f"significant = {sig or 'none'}")


def fig_volume():
    """Mean flow time (bars) and on-time delivery (line) vs order-book size N."""
    vols = [("baseline", 50), ("batches75", 75), ("batches100", 100)]
    xs = [str(n) for _, n in vols]
    flow = [load(k)["meanFlowTime"][0] for k, _ in vols]
    flow_hw = [load(k)["meanFlowTime"][1] for k, _ in vols]
    otd = [load(k)["onTimePct"][0] for k, _ in vols]
    fig, ax1 = plt.subplots(figsize=(5.0, 3.2))
    ax1.bar(xs, flow, yerr=flow_hw, color="#9ecae1", edgecolor="white",
            capsize=4, label="Mean flow time")
    ax1.set_xlabel("Order book size (batches)")
    ax1.set_ylabel("Mean flow time [h]")
    ax2 = ax1.twinx()
    ax2.plot(xs, otd, "o-", color="#d62728", lw=2, label="On-time %")
    ax2.set_ylabel("On-time delivery [%]")
    ax2.set_ylim(0, 105)
    for x, y in zip(xs, otd):
        ax2.annotate(f"{y:.0f}%", (x, y), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=8, color="#d62728")
    ax1.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig_volume.pdf")
    plt.close(fig)
    print("  wrote fig_volume.pdf")


if __name__ == "__main__":
    print(f"Reading {len(SCENARIOS)} scenarios from {DATA}")
    fig_throughput()
    fig_utilisation()
    fig_doe()
    fig_volume()
    print(f"Done. Figures in {OUT}")
