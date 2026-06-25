"""
2^3 full factorial (DOE) analysis for FermaCore (testV2.0).

Factors:  A = number of dryers       (1 -> 2)
          B = cleaning-team size      (1 -> 2)
          C = number of packaging lines (3 -> 4)
Response: bottlesShipped  (r replications per corner)

All 8 corners are replicated, so the standard error of every effect is
estimated from pooled within-corner variance and each effect is tested
for significance (Montgomery, Design and Analysis of Experiments).

    python3 doe_analysis.py
"""

import csv
import math
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "test_data"
RESP = "bottlesShipped"

# corner -> (A, B, C, csv-stem)   coded: -1 = low, +1 = high
CORNERS = {
    "(1)": (-1, -1, -1, "baseline"),
    "a":   (+1, -1, -1, "dryer2"),
    "b":   (-1, +1, -1, "cleanTeam2"),
    "ab":  (+1, +1, -1, "dryer2_cleanTeam2"),
    "c":   (-1, -1, +1, "packLine4"),
    "ac":  (+1, -1, +1, "dryer2_packLine4"),
    "bc":  (-1, +1, +1, "cleanTeam2_packLine4"),
    "abc": (+1, +1, +1, "dryer2_cleanTeam2_packLine4"),
}

# effects to estimate -> function of the three coded levels giving its sign
EFFECTS = {
    "A  (dryer)":  lambda a, b, c: a,
    "B  (clean)":  lambda a, b, c: b,
    "C  (pack)":   lambda a, b, c: c,
    "AB":          lambda a, b, c: a * b,
    "AC":          lambda a, b, c: a * c,
    "BC":          lambda a, b, c: b * c,
    "ABC":         lambda a, b, c: a * b * c,
}


def reps(stem):
    rows = list(csv.DictReader(open(DATA / f"FermaCore_{stem}.csv")))
    return [float(r[RESP]) for r in rows]


def mean(v):
    return sum(v) / len(v)


def var(v):
    m = mean(v)
    return sum((x - m) ** 2 for x in v) / (len(v) - 1)


# ---------- load ----------
data = {c: reps(stem) for c, (a, b, cc, stem) in CORNERS.items()}
r = len(data["(1)"])
ybar = {c: mean(v) for c, v in data.items()}
k = 3
ncorners = 2 ** k

# ---------- pooled variance & SE of an effect ----------
sp2 = sum(var(v) for v in data.values()) / ncorners
df = ncorners * (r - 1)
sp = math.sqrt(sp2)
# effect = avg of (ncorners/2 * r) obs minus avg of (ncorners/2 * r) obs
n_half = (ncorners // 2) * r
se_eff = math.sqrt(sp2 * (1.0 / n_half + 1.0 / n_half))
t_crit_95 = 1.99 if df >= 60 else 2.00   # ~ t(152, 0.975)

grand = sum(ybar.values()) / ncorners

print("=" * 70)
print(f"  2^3 full factorial DOE  --  response: {RESP}")
print(f"  A=dryer  B=cleaning team  C=packaging line")
print(f"  r = {r} reps/corner   pooled df = {df}   pooled sd = {sp:.0f}")
print("=" * 70)

print("\n  Corner means (bottles shipped):")
print(f"  {'corner':<6}{'A':>3}{'B':>3}{'C':>3}{'  mean':>12}")
for c, (a, b, cc, _) in CORNERS.items():
    print(f"  {c:<6}{a:>+3}{b:>+3}{cc:>+3}{ybar[c]:>12.0f}")
print(f"\n  Grand mean = {grand:,.0f}")

print("\n  Effect estimates (bottles, low->high) with significance test:")
print(f"  {'effect':<12}{'estimate':>10}{'SE':>8}{'t':>8}{'  sig(95%)':>11}")
print("  " + "-" * 49)
results = {}
for name, sign in EFFECTS.items():
    contrast_hi = [ybar[c] for c in CORNERS if sign(*CORNERS[c][:3]) > 0]
    contrast_lo = [ybar[c] for c in CORNERS if sign(*CORNERS[c][:3]) < 0]
    eff = sum(contrast_hi) / len(contrast_hi) - sum(contrast_lo) / len(contrast_lo)
    t = eff / se_eff
    sig = "YES" if abs(t) > t_crit_95 else "no"
    results[name] = eff
    print(f"  {name:<12}{eff:>10.1f}{se_eff:>8.1f}{t:>8.2f}{sig:>11}")
print("  " + "-" * 49)
print(f"  |t| > {t_crit_95:.2f} = significant at 95%.  SE common to all "
      f"effects = {se_eff:.0f}")
print("=" * 70)
