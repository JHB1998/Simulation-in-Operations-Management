# FermaCore — Plan og status
**Deadline: Fredag 26. juni 2026, kl. 18:00**

---

## Arbejdsregel

> **Tjek altid `Curriculum/42417_Case_descriptions_June26_160626.pdf` inden der anbefales næste skridt, skrives rapportindhold eller bygges nye scenarier.** Ingen hallucinering af krav der ikke står i opgaven. Hvis noget er i planen men ikke i casen, skal det flagges fremfor at implementeres blindt.

---

## Hvad der er gjort

### Simuleringsinfrastruktur
- `FermaCore_Replication_Harness_Brams.alp` konfigureret med auto-navngivning af CSV'er baseret på aktive parameterværdier (sammensætter filnavn fra alle ikke-default parametre adskilt af `_`)
- Absolut filsti sat til `/Users/jacobbrams/Simulation-in-Operations-Management/`
- `halfwidth_analysis.py` skrevet og testet — kør med `python3 halfwidth_analysis.py <filnavn.csv>`

### Simuleringsresultater — 7 CSV'er låst

| CSV-fil | Scenarie | Bottles mean | ±95% CI HW |
|---|---|---|---|
| `FermaCore_replications.csv` | Baseline (N=20) | 67.487 | ±1.275 |
| `FermaCore_dryer2.csv` | +1 dryer | 67.701 | ±1.074 |
| `FermaCore_cleanTeam2.csv` | +1 cleaning team | 67.894 | ±1.151 |
| `FermaCore_packLine4.csv` | +1 packaging line | 67.919 | ±1.395 |
| `FermaCore_groupByProduct.csv` | Resequence | 67.579 | ±1.387 |
| `FermaCore_dryer2_cleanTeam2.csv` | **Bedste kombination** | **68.794** | **±904** |
| `FermaCore_dryer2_cleanTeam2_packLine4.csv` | Triple (forværrer) | 67.633 | ±1.320 |

### Vigtigste fund fra output-analysen

- **Ingen enkelt OFAT-forbedring er statistisk signifikant** — alle CI'er overlapper med baseline
- **+1 dryer alene** skifter bottleneck fra dryer (94.6%) til cleaning team (95.2%) — afslører at de to er co-constraints
- **+1 dryer & +1 cleaning team** giver +1.307 flasker (+1.9%), marginal CI-overlap — bedste resultat
- **+4. packaging linje** oven på kombinationen forværrer resultatet — ekstra linje øger cleaning team-belastning (setup/changeover) og overvælder den allerede pressede cleaning team
- **Bottleneck-rækkefølge:** Dryer (94.6%) → Cleaning team (81.9%) → Packaging (54.5%)

### Bottleneck-skift på tværs af scenarier

| Scenarie | Dryer util | Clean team util | Packaging util | Bottleneck |
|---|---|---|---|---|
| Baseline | **94.6%** | 81.9% | 54.5% | Dryer |
| +1 dryer | 76.3% | **95.2%** | 74.0% | Cleaning team |
| +1 cleaning team | 90.7% | **91.2%** | 88.1% | Cleaning team |
| +1 packaging line | **94.8%** | 82.1% | 41.0% | Dryer |
| Resequence | **93.2%** | 86.5% | 54.9% | Dryer |
| dryer2 + cleanTeam2 | 58.3% | **94.2%** | 93.6% | Cleaning team |
| dryer2 + cleanTeam2 + packLine4 | 72.9% | **93.5%** | 77.9% | Cleaning team |

### Rapport — LaTeX-status

| Sektion | Fil | Status |
|---|---|---|
| 01 Intro | `01Intro.tex` | ⚠️ Kort — mangler 2–3 linjer |
| 02 Collaboration | `02Collaboration.tex` | ✅ Komplet |
| 03 Performance (KPIs) | `03Performance.tex` | ✅ Komplet med SMART-tabel |
| 04 Conceptual model | `04Conceptual.tex` | ✅ Skrevet (103 linjer) |
| 05 Assumptions | `05Assumptions.tex` | ⚠️ Komplet men én fejl: siger "press scrap 10%" — skal sige "premix scrap ~6% via MTBF-model" |
| 06 Input Modeling | `06InputModeling.tex` | ⚠️ Tekst skrevet — mangler histogram-figurer fra distribution fitter |
| 07 V&V | `07VerificationValidation.tex` | ⚠️ Struktur til stede — mangler: verification-tabel, Little's Law tal, én fejl: bullet siger "packaging er forventet bottleneck" men tabel og simulation siger drying |
| 08 Output Analysis | `08OutputAnalysis.tex` | ✅ Komplet med alle tal fra N=20 halvbredde-analyse |
| 09 Experimental Study | `09ExperimentalStudy.tex` | ✅ OFAT + kombination udfyldt — ⏳ demand-tabel og I4.0 mangler (venter på kørsler) |
| 10 Conclusions | `10Conclusions.tex` | ⚠️ Skelet til stede — mangler konkrete tal (venter på demand/I4.0) |

---

## Næste skridt — prioriteret rækkefølge

### 1. Kør de 5 resterende simuleringer (gør dette NU)

Åbn `FermaCore_Replication_Harness_Brams.alp` i AnyLogic. Kør `ReplicationsExp` for hvert scenarie. Husk at nulstille alle parametre til default mellem kørsler.

| # | Parameter(e) der ændres | Default bagefter | CSV der skabes |
|---|---|---|---|
| A | `demandMultiplier = 1.25` | → 1.0 | `FermaCore_demand1p25.csv` |
| B | `demandMultiplier = 1.5` | → 1.0 | `FermaCore_demand1p5.csv` |
| C | `demandMultiplier = 2.0` | → 1.0 | `FermaCore_demand2p0.csv` |
| D | `premixFailureProbability = 0.04` | → -1.0 | `FermaCore_i40_scrap0p04.csv` |
| E | `numDryers=2` + `cleaningTeamCapacity=2` + `demandMultiplier=1.25` | alle → default | `FermaCore_dryer2_cleanTeam2_demand1p25.csv` |

Kørsel E er den vigtigste — viser om bedste kombination holder under 2030-efterspørgsel.

Kør halvbredde-analyse på hver færdig CSV:
```
python3 halfwidth_analysis.py FermaCore_demand1p25.csv
```

### 2. Ret de to fejl i rapporten

**05Assumptions.tex, punkt 9:**
- Nu: `"press scrap 10\% (baseline)"`
- Skal være: `"premix scrap \approx 6\% (data-derived via MTBF model; see Sec.~\ref{sec:input})"`

**07VerificationValidation.tex, første bullet:**
- Nu: `"packaging load ≈ 167h/week ⟹ packaging is the expected constraint"`
- Skal være: `"drying + 2h clean ≈ 300 required unit-hours on 1 dryer ⟹ drying is the expected constraint"`

### 3. Udfyld resterende LaTeX efter simuleringsresultater

**09ExperimentalStudy.tex — demand-tabel:**
Erstat `[\,]` i `tab:demand` med tal fra kørsel A–E.

**09ExperimentalStudy.tex — Industry 4.0-afsnit:**
Erstat `[\,]` med resultat fra kørsel D.

**10Conclusions.tex:**
Indsæt konkrete tal:
- Max sustainable batches/week (fra demand-sweep)
- Bedste kombinations hold under 2030 (fra kørsel E)
- I4.0 effekt i ekstra flasker/uge (fra kørsel D)

**07VerificationValidation.tex — Little's Law:**
Baseline-tal er klar:
- WIP = 19.85 batches
- Throughput rate = 50 batches / ~490h ≈ 0.102 batches/h
- Mean flow time W = 200.9h
- rate × W = 0.102 × 200.9 = **20.5 ≈ WIP = 19.85** ✅

### 4. Figurer til rapporten

Tre figurer skal produceres:

| Figur | Kilde | Placering |
|---|---|---|
| Utilisation bar chart (alle scenarier) | `halfwidth_analysis.py` output / Python matplotlib | Sektion 09 |
| Throughput bar chart med 95% CI error bars | Alle CSV'er / Python matplotlib | Sektion 09 |
| WIP-over-time | Screenshot fra AnyLogic `chartWIP` under kørsel | Sektion 07 eller 09 |

Når alle CSV'er er klar, kan Python-kode til figurerne genereres automatisk.

### 5. Afsluttende polish (torsdag aften)

- [ ] Section 01 Intro: 2–3 linjer for at afslutte
- [ ] Section 10 Conclusions: konkrete tal ind
- [ ] Tjek sidetal — maks **15 sider inkl. forside og indholdsfortegnelse**
- [ ] Tjek at alle tal i rapporten matcher CSV-outputtet præcist
- [ ] Figurnavne og nummerering

### 6. Individuelle videoer (hver for sig)

- Maks **5 minutter** — brug ikke speed-up
- Kamera **skal være tændt** til introen
- Fælles AnyLogic-model og figurer må bruges, men **slides og præsentation skal være individuelle**
- Foreslået disposition:
  1. Introducer dig selv (navn + studienummer) med kamera
  2. Præsenter simuleringsformålet
  3. Vis modellen i AnyLogic (Main-canvas + flowchart)
  4. Demonstrer en kørsel (fx baseline eller dryer2-scenariet)
  5. Præsenter de vigtigste fund og konklusioner

### 7. Pakke og aflevere (fredag morgen — buffer til kl. 18:00)

**Zip-filen skal indeholde:**
- `FermaCore_Replication_Harness_Brams.alp`
- `FermaCore_input_data.xlsx`
- Ingen log-filer, ingen binaries, ingen CSV-output

**DTU Learn upload:**
- [ ] Gruppe-rapport (PDF)
- [ ] Zip-fil med model + input
- [ ] Video 1 (Jacob)
- [ ] Video 2 (makker)

---

## Kritisk sti

```
Nu            → Kørsel A–E (5 × ~2 min = ~10 min total)
               ↓
Nu/i aften    → Udfyld demand-tabel + I4.0 + Conclusions
               ↓
I aften       → Ret de 2 fejl + Little's Law + figurer
               ↓
Torsdag aften → Final polish, sidetal-tjek
               ↓
Fredag morgen → Videoer + pakke + upload
               ↓
Fredag 18:00  → DEADLINE
```

**Blokkerende:** Kørsel A–E er det eneste der blokerer konklusioner og demand-tabel. Alt andet kan skrives parallelt.
