"""
Generate the input-modelling fit figures for FermaCore (testV2.0) from the raw
observation columns in FermaCore_input_data.xlsx.

Outputs (vector PDF, for Overleaf) to figures/ (copy into the report repo's figures/):
    fig_fit_drying.pdf      - drying time, Normal fit (solid) + implemented triangular (dashed)
    fig_fit_premix.pdf      - premix/blending repair time, lognormal fit
    fig_fit_packaging.pdf   - packaging-line repair time, lognormal fit

The three fitted quantities match the AnyLogic model exactly:
    drying    = triangular(2.703493, 5.541093, 3.748756) h
    premix    = lognormal(mean 0.803 h, std 2.086 h)        [PremixBlending column]
    packaging = lognormal(mean 5.009 h, std 7.671 h)        [TabletLine column]

Reads the .xlsx via the standard-library zip/XML reader (no openpyxl needed).
Needs matplotlib + numpy + scipy. Run from repo root:
    venv/bin/python make_fit_figures.py
"""

import math
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).parent
XLSX = ROOT / "FermaCore_input_data.xlsx"
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def column(zf, sheet_xml):
    """Return the numeric values of the (single-column) sheet, skipping the header."""
    root = ET.fromstring(zf.read(sheet_xml))
    out = []
    for row in root.findall(f".//{NS}row")[1:]:
        c = row.find(f"{NS}c")
        if c is None:
            continue
        v = c.find(f"{NS}v")
        if v is not None and v.text:
            try:
                out.append(float(v.text))
            except ValueError:
                pass
    return np.array(out)


def ks_p(x, frozen):
    return stats.kstest(x, frozen.cdf).pvalue


def lognormal_fig(x_hours, fname, xlabel, call):
    """Histogram (clipped at the 99th pct for readability) + lognormal MLE overlay."""
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    hi = np.percentile(x_hours, 99)
    ax.hist(x_hours[x_hours <= hi], bins=40, density=True,
            color="#a1d99b", edgecolor="white", label=f"Data (n={len(x_hours)})")
    lx = np.log(x_hours)
    mu_log, sd_log = lx.mean(), lx.std(ddof=1)
    frozen = stats.lognorm(sd_log, 0, math.exp(mu_log))
    xs = np.linspace(x_hours.min(), hi, 400)
    p = ks_p(x_hours, frozen)
    ax.plot(xs, frozen.pdf(xs), "r-", lw=2,
            label=f"Lognormal\n{call}\nKS p={p:.2f}")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Density")
    ax.set_title(f"mean={x_hours.mean():.2f} h, std={x_hours.std(ddof=1):.2f} h", fontsize=8)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / fname)
    plt.close(fig)
    return p


def main():
    if not XLSX.exists():
        raise SystemExit(f"Missing {XLSX} - place FermaCore_input_data.xlsx in the repo root.")
    plt.rcParams.update({"font.size": 9})

    with zipfile.ZipFile(XLSX) as zf:
        dry = column(zf, "xl/worksheets/sheet3.xml")        # DryingConditioning [h]
        premix = column(zf, "xl/worksheets/sheet4.xml") / 60.0   # PremixBlending [min] -> h
        pack = column(zf, "xl/worksheets/sheet5.xml") / 60.0     # TabletLine [min] -> h

    # --- Drying: histogram + Normal fit (solid) + implemented triangular (dashed) ---
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    ax.hist(dry, bins=20, density=True, color="#9ecae1", edgecolor="white",
            label=f"Data (n={len(dry)})")
    xs = np.linspace(dry.min(), dry.max(), 300)
    mu, sd = dry.mean(), dry.std(ddof=1)
    p_norm = ks_p(dry, stats.norm(mu, sd))
    ax.plot(xs, stats.norm(mu, sd).pdf(xs), "r-", lw=2,
            label=f"Normal({mu:.2f}, {sd:.2f})\nKS p={p_norm:.2f}")
    a, b, mode = 2.703493, 5.541093, 3.748756
    c = (mode - a) / (b - a)
    ax.plot(xs, stats.triang(c, loc=a, scale=b - a).pdf(xs), "k--", lw=1.5,
            label="Triangular (AnyLogic)")
    ax.set_xlabel("Drying time [h/batch]")
    ax.set_ylabel("Density")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "fig_fit_drying.pdf")
    plt.close(fig)
    print(f"  wrote fig_fit_drying.pdf (Normal KS p={p_norm:.2f})")

    p_pre = lognormal_fig(premix, "fig_fit_premix.pdf",
                          "Premix repair time [h]", "lognormal(0.803, 2.086)")
    print(f"  wrote fig_fit_premix.pdf (KS p={p_pre:.2f})")
    p_pack = lognormal_fig(pack, "fig_fit_packaging.pdf",
                           "Packaging repair time [h]", "lognormal(5.009, 7.671)")
    print(f"  wrote fig_fit_packaging.pdf (KS p={p_pack:.2f})")

    print(f"Done. Fit figures in {OUT}")


if __name__ == "__main__":
    main()
