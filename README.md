# FermaCore — Simulation in Operations Management
**42417 DTU | Deadline: Fredag 26. juni 2026 kl. 18:00**

---

## Modelfiler

| Fil | Status |
|---|---|
| `FermaCore_Replication_Harness_Brams.alp` | Original — rør ikke |
| `FermaCore_Replication_Harness_Brams_testV2.0.alp` | **Aktiv model** — alle kørsler herfra |

### Ændringer i testV2.0 ift. original
1. `pressScrapRate = 0.10` — korrekt 10% tablet-tab ved komprimering (`delayCompress` onExit)
2. `queueStrategy = 0` — 0=FIFO, 1=EDD, 2=SPT ved tørrer-kø (`seizeDryer` comparison)
3. CSV-output peger på `test_data/` via relativ sti
4. CSV-navngivning inkluderer `pressScrapRate` og `queueStrategy` automatisk

---

## Simuleringsresultater — test_data/

**Ny baseline: 61,627 ± 1,000 flasker** (gammel model uden press scrap: 67,487)

| # | Scenarie | CSV | Bottles | ±CI | Bottleneck | Δ baseline |
|---|---|---|---|---|---|---|
| 0 | **Baseline** | `baseline` | 61,627 | ±1,000 | Dryer 94.9% | — |
| 1 | +1 dryer | `dryer2` | 60,880 | ±734 | Clean team 94.8% | −747 |
| 2 | +1 cleaning team | `cleanTeam2` | 60,918 | ±1,419 | Dryer 91.1% | −709 |
| 3 | +1 packaging line | `packLine4` | 61,759 | ±861 | Dryer 94.9% | +132 |
| 4 | Resequence | `groupByProduct` | 60,619 | ±1,199 | Dryer 93.2% | −1,008 |
| 5 | dryer2 + cleanTeam2 | `dryer2_cleanTeam2` | 60,183 | ±887 | Clean team 92.9% | −1,444 |
| 6 | dryer2 + cleanTeam2 + pack4 | `dryer2_cleanTeam2_packLine4` | 61,776 | ±889 | Clean team 93.0% | +149 |
| 7 | Demand ×1.25 | `demand1p25` | 60,435 | ±1,361 | Dryer 94.9% | −1,192 |
| 8 | Demand ×1.5 | `demand1p5` | 61,058 | ±957 | Dryer 94.9% | −569 |
| 9 | Demand ×2.0 | `demand2p0` | 60,890 | ±1,362 | Dryer 95.1% | −737 |
| 10 | **I4.0** (press 10%→4%) | `i40_scrap0p04` | **65,736** | ±797 | Dryer 94.7% | **+4,109 (+6.7%)** |
| 11 | dryer2+cleanTeam2+demand×1.25 | `dryer2_cleanTeam2_demand1p25` | 60,718 | ±1,197 | Clean team 93.2% | −909 |
| 12 | dryer2+cleanTeam2+pack4+demand×1.25 | `dryer2_cleanTeam2_packLine4_demand1p25` | 61,132 | ±978 | Clean team 93.2% | −495 |
| 13 | EDD kø | `queue1` | 61,333 | ±1,245 | Dryer 94.9% | −294 |
| 14 | SPT kø | `queue2` | 61,444 | ±902 | Dryer 94.8% | −183 |
| 15 | dryer2+demand×1.25+EDD | `dryer2_demand1p25_queue1` | 60,874 | ±878 | Clean team 94.9% | −753 |

### Vigtigste fund
- **I4.0 er den klare vinder** — +4,109 flasker (+6.7%), ingen maskininvestering
- **Whack-a-Mole** — dryer2 skifter bottleneck til clean team (95%), dryer2+cleanTeam2 skifter til packaging (93%)
- **CAPEX-paradoks** — dryer2+cleanTeam2+pack4 giver kun +149 flasker (+0.2%) trods massiv investering
- **Supply-constraint** — throughput flad ved ×1.25/1.5/2.0; dryer låst på ~95% uanset efterspørgsel
- **Kø-sekvensering virker ikke** — EDD/SPT ingen effekt; drying-tider for homogene (σ=0.39h)

---

## Rapport — LaTeX status

| Sektion | Fil | Status | Hvad mangler |
|---|---|---|---|
| 01 Intro | `01Intro.tex` | ✅ | — |
| 02 Collaboration | `02Collaboration.tex` | ❌ | Navne + studienumre ind |
| 03 Performance | `03Performance.tex` | ✅ | — |
| 04 Conceptual | `04Conceptual.tex` | ✅ | — |
| 05 Assumptions | `05Assumptions.tex` | ⚠️ | Tilføj `queueStrategy=0` som antagelse |
| 06 Input Modeling | `06InputModeling.tex` | ⚠️ | pressScrapRate + yields dokumenteret; 3× histogram-figurer mangler |
| 07 V&V | `07VerificationValidation.tex` | ❌ | Ret bottleneck-fejl; Little's Law; verification-tabel; WIP-figur |
| 08 Output Analysis | `08OutputAnalysis.tex` | ❌ | Skriv om med ny baseline 61,627 ±1,000 |
| 09 Experimental Study | `09ExperimentalStudy.tex` | ❌ | Alle 16 scenarietal + demand-tabel + I4.0 + kø + tre nye analysedimensioner |
| 10 Conclusions | `10Conclusions.tex` | ❌ | Udfyld med konkrete tal og ny narrativ |

---

## Tre analysedimensioner der løfter til topniveau

### A — Design of Experiments (2² faktorialt design)
Vi har et komplet 2² design på dryer × cleaningTeam — data klar, ingen nye kørsler nødvendige.

| | cleanTeam=1 | cleanTeam=2 |
|---|---|---|
| dryer=1 | 61,627 | 60,918 |
| dryer=2 | 60,880 | 60,183 |

- Main effect dryer: **−741 flasker**
- Main effect clean team: **−703 flasker**
- Interaktionseffekt: **+6 flasker (ubetydelig i throughput)**

Narrativ: ingen positiv synergi i throughput — interaktionen er synlig i bottleneck-skiftet (utilisation). Inkluder Main Effects Plot og Interaction Plot. ⚠️ Vær præcis: data viser IKKE "maskiner forstærker hinanden positivt".

### B — On-Time Delivery (OTD%)
`releaseViolations` og `maxReleaseDev` er allerede i alle CSV-filer — ingen nye kørsler.
- OTD% = (batches shipped − releaseViolations) / batches shipped × 100
- Sammenlign baseline vs. groupByProduct vs. I4.0 på leveringssikkerhed
- Kan give groupByProduct en ny vinkel selvom throughput var lavere

### C — Økonomisk dimension (WIP holding cost + OPEX)
Ren skriveopgave med antagne, illustrative tal — ingen ny data.
- WIP holding cost: antag €500/batch/dag
- dryer2+cleanTeam2+packLine4: €2,300/dag ekstra OPEX → +149 flasker → ikke rentabelt
- I4.0: engangsinvestering i sensorer → +4,109 flasker/uge → klart bedst pr. krone

---

## Figurer — komplet liste

| Figur | Metode | Sektion | Klar? |
|---|---|---|---|
| Throughput bar chart med 95% CI (16 scenarier) | Python/matplotlib | 09 | ✅ Data klar |
| Utilisation bar chart (dryer/clean/pack) | Python/matplotlib | 09 | ✅ Data klar |
| Main Effects + Interaction Plot (DOE 2²) | Python/matplotlib | 09 | ✅ Data klar |
| OTD% per scenarie | Python/matplotlib | 09 | ⚠️ Kræver releaseViolations-udtræk |
| Histogram drying time + fit overlay | Screenshot AnyLogic | 06 | ❌ Tag screenshot |
| Histogram premix repair + fit overlay | Screenshot AnyLogic | 06 | ❌ Tag screenshot |
| Histogram packaging repair + fit overlay | Screenshot AnyLogic | 06 | ❌ Tag screenshot |
| WIP-over-time chart | Screenshot AnyLogic | 07 | ❌ Tag screenshot |

---

## Næste skridt — prioriteret

```
1. Du: giv navne til 02Collaboration
2. Du: tag 4 AnyLogic-screenshots (distribution fitter ×3 + WIP chart)
3. Jeg: skriver 02, 05, 06, 07, 08, 09, 10 i LaTeX
4. Jeg: genererer Python-kode til alle figurer inkl. DOE og OTD
5. Du: indsætter screenshots + kører figur-scripts
6. Sidetal-tjek (maks 15 sider inkl. forside)
7. Fredag morgen: videoer + zip + upload DTU Learn inden 18:00
```

### Zip-fil skal indeholde
- `FermaCore_Replication_Harness_Brams_testV2.0.alp`
- `FermaCore_input_data.xlsx`
- **Ikke:** logs, binaries, CSV-output

### DTU Learn upload
- [ ] Gruppe-rapport (PDF)
- [ ] Zip-fil med model + input
- [ ] Video Jacob (maks 5 min, kamera til intro, egne slides)
- [ ] Video makker (maks 5 min, kamera til intro, egne slides)

---

## Hjælpekommandoer

```bash
# Halvbredde-analyse
cd /Users/jacobbrams/Simulation-in-Operations-Management
python3 halfwidth_analysis.py test_data/FermaCore_baseline.csv

# Alle scenarier
for f in test_data/FermaCore_*.csv; do python3 halfwidth_analysis.py "$f"; done
```
