# FermaCore — Plan og status
**Case: Manufacturing (FermaCore Labs). Deadline: Fredag 26. juni 2026, kl. 18:00**

> Sidst verificeret: 25. juni 2026. Alle tal nedenfor er trukket direkte fra
> `test_data/` via `halfwidth_analysis.py`. Den **kanoniske rapport** er Overleaf-
> repoet `Simulation-in-Operations-Management-wRepo--1/` (separat git, remote
> `Maglehoj/...-wRepo-`). Den indlejrede `Simulation_in_Operations_Management/`
> i hovedrepoet er **arkiveret** (`Arkiv/old_report/`) — rediger den ikke.

---

## Arbejdsregel
> **Tjek altid `Curriculum/42417_Case_descriptions_June26_160626.pdf` (Manufacturing, s. 6–9) inden der anbefales næste skridt eller skrives rapportindhold.** Det er Manufacturing-casen — IKKE Healthcare/apheresis. Hint som "multi-factorial test design" hører til Healthcare og må ikke bruges som begrundelse her.

---

## Overordnet status: rapporten er ~95% færdig

Den kanoniske rapport (`-wRepo--1`) har **ingen TODO/placeholder-huller tilbage** i
brødteksten, og dens tal er verificeret mod `test_data`. Resultater, DOE, 2030-demand
og I4.0 er skrevet og korrekte. Det der mangler er **afsluttende detaljer + leverancer**
(se "Hvad mangler" nederst).

---

## Modelfiler

| Fil | Status |
|---|---|
| `FermaCore_Replication_Harness_Brams_testV2.0.alp` | **Aktiv model** — alle kørsler herfra |
| Gamle `.alp` (BASE-linjen, original Replication_Harness, m.fl.) | Arkiveret i `Arkiv/old_models/` |

### testV2.0 — hvad modellen faktisk indeholder (verificeret i .alp)
- `pressScrapRate = 0.10` (baseline); I4.0-scenarie sænker til 0.04
- `queueStrategy`: 0=FIFO (baseline), 1=EDD, 2=SPT ved tørrer-kø
- **Drying** = `triangular(2.703493, 5.541093, 3.748756)` h (fittet fra DryingConditioning)
- **Premix/blender repair** = `lognormal(0.803, 2.086)` h (middel/std fra PremixBlending)
- **Packaging repair** = `lognormal(5.009, 7.671)` h (middel/std fra TabletLine)
- **Failure-interarrival**: blenderNew `exponential(168.0)` h, blenderOld `exponential(54.164718)` h, packaging `exponential(4.0)` h (Weibull-middelværdier implementeret som exponential)

---

## Simuleringsresultater — verificeret fra test_data/ (n=20 reps)

**Baseline: 60,972 bottles (±1,067).** Bottleneck = drying ~94.9%.

| Scenarie | Bottles | ±CI | Δ baseline |
|---|---|---|---|
| **baseline** | 60,972 | ±1,067 | — |
| dryer2 | 60,880 | ±734 | −91 |
| cleanTeam2 | 60,918 | ±1,419 | −54 |
| packLine4 | 61,759 | ±861 | +787 |
| groupByProduct | 60,619 | ±1,199 | −352 |
| dryer2_cleanTeam2 | 60,183 | ±887 | −789 |
| dryer2_packLine4 | 61,266 | ±955 | +294 |
| cleanTeam2_packLine4 | 61,018 | ±934 | +47 |
| dryer2_cleanTeam2_packLine4 | 61,776 | ±889 | +805 |
| demand1p25 | 60,435 | ±1,361 | −537 |
| demand1p5 | 61,058 | ±957 | +87 |
| demand2p0 | 60,890 | ±1,362 | −81 |
| dryer2_cleanTeam2_demand1p25 | 60,718 | ±1,197 | −254 |
| dryer2_cleanTeam2_packLine4_demand1p25 | 61,132 | ±978 | +160 |
| dryer2_demand1p25_queue1 | 60,874 | ±878 | −98 |
| queue1 (EDD) | 61,333 | ±1,245 | +362 |
| queue2 (SPT) | 61,444 | ±902 | +472 |
| **i40_scrap0p04** | **65,736** | ±797 | **+4,764 (+7.8%)** |

### Vigtigste fund (alle korrekte i rapporten)
- **I4.0 er den eneste reelle løftestang** — press scrap 10%→4% = **+4,764 bottles (+7.8%)**, 95% CI [3,479; 6,050], ingen CAPEX.
- **DOE (fuldt 2³, dryer×clean×pack)**: kun **packaging-linjen er signifikant** (+717 bottles, +1.2%); dryer, cleaning team og alle interaktioner er ikke til at skelne fra støj (pooled SE=334, ±664-grænse).
- **Supply-constrained**: throughput flad ~61k uanset demand ×1.25/1.5/2.0; volumen sat af 50-batch-planen + yield, ikke stationskapacitet.
- **Whack-a-Mole**: ekstra dryer flytter bottleneck til cleaning team (94.8%), dryer2+cleanTeam2 flytter til packaging — synligt i **utilisation**, ikke i throughput.
- **Kø-sekvensering virker ikke**: EDD/SPT ingen reel effekt; drying-tider for homogene (σ≈0.39 h).
- **OTD/tardiness ubrugelig**: releaseViolations=0 overalt (OTD=100%), maxReleaseDev konstant → udeladt (se NOTER).

---

## Rapport — sektionsstatus (kanonisk -wRepo--1)

| Sektion | Status | Note |
|---|---|---|
| Forside (`title.tex`) | ✅ | Jacob (s224927) / Gustav (s224917) / **Group 16** |
| 01 Intro | ✅ | — |
| 02 Collaboration | ✅ | Ingen andre grupper; Jacob = input/output/eksperimenter, Gustav = AnyLogic+V&V |
| 03 Performance (KPIs) | ✅ | — |
| 04 Conceptual | ✅ | Flowchart + activity diagram |
| 05 Assumptions | ✅ | Inkl. queueStrategy=0, yields, terminating-horisont |
| 06 Input Modeling | ✅ | Fit-tabel rettet til modellens kald + 3 fit-figurer indsat (afventer push) |
| 07 V&V | ⚠️ | Indhold OK (Little's Law udfyldt, verification-tabel, capacity-tabel). **Mangler WIP-figur** + småryd ("collect and compare") |
| 08 Output Analysis | ✅ | Replikationsantal + CI |
| 09 Experimental Study | ✅ | Scenario-tree, DOE+Pareto, throughput/util-figurer, 2030-demand, I4.0, value-tabel — alt korrekt |
| 10 Conclusions | ✅ | Konkrete tal, korrekt I4.0 +7.8% |

---

## HVAD MANGLER — prioriteret

### A. Rapport (kanonisk -wRepo--1)
1. ~~Forside: gruppenummer~~ → **færdig (Group 16)**.
2. ~~§02: navne + arbejdsdeling~~ → **færdig**.
3. **§07**: indsæt WIP-over-time-figuren (screenshot taget). Formulér som "transient build-up and drain (terminating, no steady state)" — IKKE "monotont stigende". Ryd "(collect and compare)" og template-agtig calibrate-sætning.
4. **§06**: afgør Weibull-vs-exponential-noten i "Given distributions" (failure-frekvens står som Weibull, men modellen kører exponential med Weibull-middel) — tilføj evt. én præciserende linje.
5. **Sidetjek ≤15 sider** (inkl. forside) — kompilér i Overleaf og trim ved overløb.

### B. Commits/push (gøres af jer)
6. **Hovedrepo**: Arkiv-oprydning + `figures/` + scripts + xlsx → `git add -A && commit && push`.
7. **-wRepo--1**: §06-ændring + 3 `fig_fit_*.pdf` → commit & push, så Overleaf henter dem.

### C. Leverancer (case-formalia, s. 11)
8. **2 individuelle videoer** (Jacob + Gustav) — egne slides, egen præsentation (kopiering = plagiat), MP4.
9. **Zip**: `FermaCore_Replication_Harness_Brams_testV2.0.alp` + `FermaCore_input_data.xlsx`. **Ingen** logs, binaries eller CSV-output.
10. **Upload til DTU Learn** inden fre 26/6 18:00: rapport-PDF + zip + 2 videoer.

---

## Kendte data-uoverensstemmelser (ryddet op)
- README/denne plans **gamle** tal (baseline 61,627, I4.0 +4,109/+6.7%) var **forkerte**. Korrekt: baseline 60,972, I4.0 +4,764/+7.8% (verificeret). Rapporten bruger de korrekte.
- `FermaCore_AnyLogic_Build_Guide.md` er forældet på ét punkt: den påstår modellen ikke har repair/downtime-fordelinger — det har testV2.0 (se modelafsnit ovenfor). Brug denne fil, ikke guiden, for failure/repair-fakta.

---

## Hjælpekommandoer
```bash
cd /Users/jacobbrams/Simulation-in-Operations-Management
# Ét scenarie
./venv/bin/python halfwidth_analysis.py test_data/FermaCore_baseline.csv
# Alle scenarier
for f in test_data/FermaCore_*.csv; do ./venv/bin/python halfwidth_analysis.py "$f"; done
# Regenerér rapport-figurer (→ figures/)
./venv/bin/python make_figures.py        # throughput / utilisation / DOE (fra test_data)
./venv/bin/python make_fit_figures.py     # 3 input-fit-figurer (fra FermaCore_input_data.xlsx)
```
