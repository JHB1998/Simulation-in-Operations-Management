# FermaCore — Simulation in Operations Management
**42417 DTU · Case: Manufacturing · Deadline: fredag 26. juni 2026 kl. 18:00**

Discrete-event simulation af FermaCore Labs' tablet-/flaskelinje (AnyLogic) + skriftlig rapport.

> **Detaljeret status og "hvad mangler" står i [`MD filer/plan_og_status.md`](MD%20filer/plan_og_status.md)** — det er kilden til projektets tilstand. Denne README er kun et hurtigt overblik.

---

## Repo-struktur

| Sti | Indhold |
|---|---|
| `FermaCore_Replication_Harness_Brams_testV2.0.alp` | **Aktiv AnyLogic-model** |
| `FermaCore_input_data.xlsx` | Input-data (skal med i afleverings-zip) |
| `test_data/` | CSV-output, ét pr. scenarie (20 reps) |
| `figures/` | Genererede figurer til rapporten (PDF) |
| `halfwidth_analysis.py` | Per-KPI middel, CI-halvbredde, N-krav, bottleneck |
| `make_figures.py` | throughput / utilisation / DOE-figurer (fra `test_data/`) |
| `make_fit_figures.py` | 3 input-fit-figurer (fra `.xlsx`) |
| `doe_analysis.py`, `scenario_comparison.py` | 2³-DOE og scenarie-sammenligning |
| `Curriculum/` | Case-beskrivelse + kursusmateriale |
| `MD filer/` | `plan_og_status.md` (status) + `NOTER TIL BRUG I OVERLEAF.md` (analysevinkler) |
| `Arkiv/` | Gamle modeller, CSV'er, MD-filer og den forældede indlejrede rapport-kopi |

**Den kanoniske rapport** ligger i et separat Overleaf-repo (`...-wRepo--1/`), ikke her.

---

## Nøgleresultater (verificeret mod `test_data/`)

- **Baseline: 60,972 bottles** (±1,067). Bottleneck = drying ~94.9%.
- **Industry 4.0 (press scrap 10%→4%): +4,764 bottles (+7.8%)** — eneste reelle løftestang, ingen CAPEX.
- **DOE (2³)**: kun en ekstra packaging-linje er signifikant (+717, +1.2%); dryer/clean + interaktioner ikke signifikante.
- **Supply-constrained**: throughput flad ~61k uanset demand ×1.25/1.5/2.0.

---

## Hurtige kommandoer

```bash
cd /Users/jacobbrams/Simulation-in-Operations-Management
for f in test_data/FermaCore_*.csv; do ./venv/bin/python halfwidth_analysis.py "$f"; done
./venv/bin/python make_figures.py
./venv/bin/python make_fit_figures.py
```
