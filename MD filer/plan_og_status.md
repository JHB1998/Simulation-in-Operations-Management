# FermaCore — Plan og status
**Deadline: Fredag 26. juni 2026, kl. 18:00**

---

## Arbejdsregel

> **Tjek altid `Curriculum/42417_Case_descriptions_June26_160626.pdf` inden der anbefales næste skridt, skrives rapportindhold eller bygges nye scenarier.** Ingen hallucinering af krav der ikke står i opgaven.

---

## Modelfiler

| Fil | Status |
|---|---|
| `FermaCore_Replication_Harness_Brams.alp` | Original — rør ikke |
| `FermaCore_Replication_Harness_Brams_testV2.0.alp` | **Aktiv model** — alle kørsler herfra |

### Ændringer i testV2.0 ift. original
1. `pressScrapRate = 0.10` — korrekt 10% tablet-tab ved komprimering (implementeret i `delayCompress` onExit)
2. `queueStrategy = 0` — 0=FIFO, 1=EDD, 2=SPT ved tørrer-kø (`seizeDryer` comparison)
3. CSV-output peger på `test_data/` via relativ sti
4. CSV-navngivning inkluderer `pressScrapRate` og `queueStrategy` automatisk

---

## Simuleringsresultater — komplet datasæt (test_data/)

**Ny baseline: 61,627 ± 1,000 flasker** (gammel model uden press scrap: 67,487)

| # | Scenarie | CSV | Bottles | ±CI | Dryer | Clean | Pack | Bottleneck | Δ |
|---|---|---|---|---|---|---|---|---|---|
| 0 | **Baseline** | `baseline` | 61,627 | ±1,000 | **94.9%** | 80.0% | 52.0% | Dryer | — |
| 1 | +1 dryer | `dryer2` | 60,880 | ±734 | 77.0% | **94.8%** | 73.0% | Clean team | −747 |
| 2 | +1 cleaning team | `cleanTeam2` | 60,918 | ±1,419 | **91.1%** | 90.0% | 86.0% | Dryer | −709 |
| 3 | +1 packaging line | `packLine4` | 61,759 | ±861 | **94.9%** | 80.0% | 39.0% | Dryer | +132 |
| 4 | Resequence | `groupByProduct` | 60,619 | ±1,199 | **93.2%** | 85.0% | 53.0% | Dryer | −1,008 |
| 5 | dryer2 + cleanTeam2 | `dryer2_cleanTeam2` | 60,183 | ±887 | 61.0% | **92.9%** | 93.0% | Clean team | −1,444 |
| 6 | dryer2 + cleanTeam2 + pack4 | `dryer2_cleanTeam2_packLine4` | 61,776 | ±889 | 76.0% | **93.0%** | 77.0% | Clean team | +149 |
| 7 | Demand ×1.25 | `demand1p25` | 60,435 | ±1,361 | **94.9%** | 79.0% | 52.0% | Dryer | −1,192 |
| 8 | Demand ×1.5 | `demand1p5` | 61,058 | ±957 | **94.9%** | 80.0% | 52.0% | Dryer | −569 |
| 9 | Demand ×2.0 | `demand2p0` | 60,890 | ±1,362 | **95.1%** | 80.0% | 53.0% | Dryer | −737 |
| 10 | **I4.0** (press→4%) | `i40_scrap0p04` | **65,736** | ±797 | **94.7%** | 81.0% | 54.0% | Dryer | **+4,109** |
| 11 | dryer2+cleanTeam2+demand×1.25 | `dryer2_cleanTeam2_demand1p25` | 60,718 | ±1,197 | 61.0% | **93.2%** | 93.0% | Clean team | −909 |
| 12 | dryer2+cleanTeam2+pack4+demand×1.25 | `dryer2_cleanTeam2_packLine4_demand1p25` | 61,132 | ±978 | 77.0% | **93.2%** | 77.0% | Clean team | −495 |
| 13 | EDD kø | `queue1` | 61,333 | ±1,245 | **94.9%** | 80.0% | 52.0% | Dryer | −294 |
| 14 | SPT kø | `queue2` | 61,444 | ±902 | **94.8%** | 80.0% | 52.0% | Dryer | −183 |
| 15 | dryer2+demand×1.25+EDD | `dryer2_demand1p25_queue1` | 60,874 | ±878 | 78.0% | **94.9%** | 73.0% | Clean team | −753 |

### Vigtigste analytiske fund
- **I4.0 er vinderen** — +4,109 flasker (+6.7%) uden maskininvestering
- **Whack-a-Mole** — dryer2 skifter bottleneck til clean team (95%), dryer2+cleanTeam2 skifter til packaging (93%)
- **Supply-constraint** — throughput flad ved ×1.25/1.5/2.0 efterspørgsel; dryer låst på ~95%
- **Kø-sekvensering virker ikke** — EDD/SPT ingen effekt; drying-tider for homogene (σ=0.39h)
- **CAPEX-paradoks** — massiv investering (dryer2+cleanTeam2+pack4) giver +149 flasker (+0.2%)

---

## Rapport — LaTeX status

| Sektion | Fil | Status | Hvad mangler |
|---|---|---|---|
| 01 Intro | `01Intro.tex` | ✅ | — |
| 02 Collaboration | `02Collaboration.tex` | ❌ | `[Author A]`/`[Author B]` → rigtige navne + studienumre |
| 03 Performance (KPIs) | `03Performance.tex` | ✅ | — |
| 04 Conceptual | `04Conceptual.tex` | ✅ | — |
| 05 Assumptions | `05Assumptions.tex` | ⚠️ | Tilføj `queueStrategy=0` (FIFO) som antagelse |
| 06 Input Modeling | `06InputModeling.tex` | ⚠️ | (A) pressScrapRate=0.10 som givet input; (B) yield-fordelinger; (C) 3× histogram-figurer fra distribution fitter |
| 07 V&V | `07VerificationValidation.tex` | ❌ | (1) Ret "packaging is expected constraint" → drying; (2) Little's Law udfyldes; (3) Verification-tabel; (4) WIP-figur |
| 08 Output Analysis | `08OutputAnalysis.tex` | ❌ | Hele tabellen om med ny baseline 61,627 ±1,000 |
| 09 Experimental Study | `09ExperimentalStudy.tex` | ❌ | Alle scenarietal om + demand-tabel + I4.0 + kø + tre nye analysedimensioner (se nedenfor) |
| 10 Conclusions | `10Conclusions.tex` | ❌ | 5 placeholders + ny narrativ |

---

## Næste skridt — prioriteret rækkefølge

### TRIN 1 — AnyLogic screenshots (du gør det, ~10 min)

| Screenshot | Bruges i |
|---|---|
| Distribution fitter: drying time (histogram + fit overlay) | 06 Input Modeling |
| Distribution fitter: premix repair (histogram + fit overlay) | 06 Input Modeling |
| Distribution fitter: packaging repair (histogram + fit overlay) | 06 Input Modeling |
| WIP-over-time chart (single baseline run, `chartWIP`) | 07 V&V |

### TRIN 2 — Navne til 02Collaboration (du giver mig dem)
Navne + studienumre på begge forfattere.

### TRIN 3 — LaTeX (jeg skriver, du godkender)

**3a. `02Collaboration.tex`** — navne og arbejdsdeling

**3b. `05Assumptions.tex`** — tilføj `queueStrategy=0` (FIFO som baseline kø-antagelse)

**3c. `06InputModeling.tex`** — tilføj:
- `pressScrapRate = 0.10` som givet input (case-beskrivelse s. 8)
- Yield-fordelinger (premix Tri(98.5%,99%,99.5%), pack Tri(99%,99.8%,99.7%), drying 100%)
- Indsæt histogram-figurer (fra dine screenshots)

**3d. `07VerificationValidation.tex`** — fire rettelser:
- Ret "packaging is expected constraint" → drying (linje 19)
- Little's Law: WIP=19.68, rate≈0.0967/h, W=181.6h → 0.0967×181.6=17.6 ≈ 19.68 (noter terminating-forbehold)
- Tilføj verification-tabel (expected vs. simulated per station)
- Indsæt WIP-figur

**3e. `08OutputAnalysis.tex`** — skriv om med ny baseline:
- 61,627 ±1,000 flasker (mod gammel 67,487)
- Opdater alle KPI-rækker i `tab:reps`
- Tilføj note om press scrap-korrektion

**3f. `09ExperimentalStudy.tex`** — komplet omskrivning:
- Opdater `tab:btshift` med alle 16 nye scenarietal
- Udfyld demand-tabel (alle ~61k → supply-constrained)
- Udfyld I4.0: pressScrapRate 10%→4% = +4,109 flasker (+6.7%)
- Tilføj kø-sekvensering som scenarie (ingen effekt, og forklar hvorfor)
- Tilføj tre nye analysedimensioner (se nedenfor)
- Opdater managerial value-tabel
- Indsæt throughput + utilisation bar charts

**3g. `10Conclusions.tex`** — udfyld:
- I4.0 som anbefaling nr. 1: +6.7%, ingen CAPEX
- CAPEX-paradoks: massiv investering → +0.2% (ikke signifikant)
- 2030: linje supply-constrained ved ~61,000 flasker/uge
- Kø-sekvensering: ingen effekt ved dryer-bottleneck med lav tidsvarians

---

## Tre analysedimensioner der løfter til topniveau

### A — Design of Experiments (2² faktorialt design)

Vi har et komplet 2² faktorialt design på dryer × cleaningTeam:

| | cleanTeam=1 | cleanTeam=2 |
|---|---|---|
| dryer=1 | 61,627 (baseline) | 60,918 |
| dryer=2 | 60,880 | 60,183 |

**Beregning:**
- Main effect dryer: ½[(60,880−61,627)+(60,183−60,918)] = **−741 flasker**
- Main effect clean team: ½[(60,918−61,627)+(60,183−60,880)] = **−703 flasker**
- Interaktionseffekt: ½[(60,183−60,918)−(60,880−61,627)] = **+6 flasker (ubetydelig)**

**Narrativ:** Ingen positiv synergi — begge faktorer trækker ned individuelt og kombineret. Bottleneck-skiftet (utilisation) afslører interaktionen bedre end throughput alene. Inkluder Main Effects Plot og Interaction Plot.

> ⚠️ Pas på framing: data viser IKKE "maskiner forstærker hinanden positivt" — de skifter bare bottleneck. Interaktionen er synlig i utilisation, ikke i throughput.

### B — On-Time Delivery (OTD) / Tardiness

`releaseViolations` og `maxReleaseDev` er allerede i alle CSV-filer — ingen nye kørsler nødvendige.

**Beregn for hvert scenarie:**
- OTD% = (batches shipped − releaseViolations) / batches shipped × 100
- Mean tardiness = maxReleaseDev (som proxy)

**Narrativ:** Et scenarie med lav mean flow time kan stadig have dårlig OTD hvis variabiliteten er høj. Sammenlign baseline vs. groupByProduct vs. I4.0 på OTD — det kan give groupByProduct en ny vinkel selvom throughput var lavere.

**Handling:** Udvid `halfwidth_analysis.py` til at rapportere `releaseViolations` og `maxReleaseDev`, og beregn OTD% per scenarie.

### C — Økonomisk dimension (WIP holding cost + OPEX)

Ingen ny data nødvendig — ren narrativ med antagne tal.

**Simpel cost-funktion (antaget, tydeligt markeret som illustration):**
- WIP holding cost: antag €500/batch/dag i bundet kapital
- Extra dryer OPEX: antag €800/dag
- Extra cleaning team member: antag €300/dag
- Extra packaging line: antag €1,200/dag

**Beregning for dryer2+cleanTeam2+packLine4:**
- Extra OPEX: (800+300+1,200) = €2,300/dag = €16,100/uge
- Throughput-gevinst: +149 flasker ≈ irrelevant
- Konklusion: massiv OPEX-stigning for nul reel gevinst

**Sammenlign med I4.0:**
- Sensor-investering: engangspris (ikke løbende OPEX)
- Throughput-gevinst: +4,109 flasker/uge = klart bedst pr. investeret krone

**Handling:** Tilføj som subsection i `09ExperimentalStudy.tex` eller `10Conclusions.tex` under "Managerial Insights". Marker tydeligt at tallene er illustrative.

---

## Figurer — komplet liste

| Figur | Metode | Sektion | Blokkeret af |
|---|---|---|---|
| Throughput bar chart med 95% CI (alle 16 scenarier) | Python/matplotlib fra test_data/ | 09 | Intet — klar nu |
| Utilisation bar chart (dryer/clean/pack per scenarie) | Python/matplotlib fra test_data/ | 09 | Intet — klar nu |
| Main Effects + Interaction Plot (2² DOE) | Python/matplotlib | 09 | Intet — klar nu |
| OTD% per scenarie | Python/matplotlib | 09 | Kræver releaseViolations-udtræk |
| Histogram drying time + fit | Screenshot AnyLogic | 06 | Dig: tag screenshot |
| Histogram premix repair + fit | Screenshot AnyLogic | 06 | Dig: tag screenshot |
| Histogram packaging repair + fit | Screenshot AnyLogic | 06 | Dig: tag screenshot |
| WIP-over-time | Screenshot AnyLogic | 07 | Dig: tag screenshot |

---

## Kritisk sti

```
Nu (tirsdag aften)
  → Giv mig navne til 02Collaboration
  → Tag 4 AnyLogic-screenshots
  → Jeg skriver 02, 05, 06, 07, 08, 09, 10
  → Jeg genererer Python-kode til alle figurer
  ↓
Onsdag
  → Indsæt screenshots + kør figur-scripts
  → OTD-analyse (releaseViolations)
  → Sidetal-tjek (maks 15 sider)
  ↓
Torsdag aften
  → Final review: alle tal tjekket mod CSV
  → Litteraturliste komplet
  ↓
Fredag morgen
  → Video Jacob (5 min, kamera til intro, egne slides)
  → Video makker (5 min, kamera til intro, egne slides)
  → Zip: testV2.0.alp + FermaCore_input_data.xlsx (ingen logs/CSV)
  → Upload DTU Learn
  ↓
Fredag 26. juni 18:00 — DEADLINE
```

---

## Hjælpekommandoer

```bash
# Halvbredde-analyse på ét scenarie
cd /Users/jacobbrams/Simulation-in-Operations-Management
python3 halfwidth_analysis.py test_data/FermaCore_baseline.csv

# Alle scenarier på én gang
for f in test_data/FermaCore_*.csv; do python3 halfwidth_analysis.py "$f"; done
```
