# FermaCore — Gap-analyse
**Dato: 24. juni 2026 | Deadline: Fredag 26. juni 2026 kl. 18:00**

---

## MANDATORY REQUIREMENTS — status

| # | Krav (assignment s. 8) | Status |
|---|---|---|
| 1 | Problem formulation: KPIs + conceptual model | ✅ Done (sektioner 03, 04) |
| 2 | Simulation model building incl. V&V | ⚠️ Delvist — fejl + placeholders |
| 3 | Experimental design + final analysis | ⚠️ Delvist — mangler demand-sweep + I4.0 resultater |

### Specific Issues (mandatory, s. 8)

| # | Krav | Status |
|---|---|---|
| 1 | Bottleneck identification med KPIs | ✅ Done (dryer 94.6%) |
| 2 | Improvements der optimerer linjen | ✅ Done (OFAT + kombination) |
| 3 | 2030 demand: maks sustainable throughput + bedste kombination | ❌ MANGLER HELT — tabel er tom |

### Non-mandatory (s. 8)

| # | Krav | Status |
|---|---|---|
| 1 | Industry 4.0 — press scrap 10%→4% | ⚠️ Struktur der, men mangler simuleringsresultat |

---

## RAPPORT-STRUKTUR — sektion for sektion

| Sektion | Krav (s. 12) | Problem fundet |
|---|---|---|
| 00 Forside | Navne + studienumre + gruppenummer | Ikke tjekket — kontrollér manuelt |
| 01 Intro | Intro til case + studie-objektiv | ✅ OK — men lidt kort |
| 02 Collaboration | Samarbejde med andre grupper + arbejdsdeling | ❌ `[Author A]` og `[Author B]` er stadig placeholders! |
| 03 KPIs | Liste + argumentation for valg | ✅ OK |
| 04 Conceptual | Flowchart + activity diagram | ✅ OK |
| 05 Assumptions | Liste over modelantagelser | ⚠️ Antagelse 9: "press scrap 10%" — men `09ExperimentalStudy` siger "premix scrap ~6%" om I4.0 — inkonsistens på tværs af sektioner |
| 06 Input Modeling | Dokumentér input-modellering | ⚠️ Tekst OK, men histogram-figurer mangler (TODO-kommentar linje 32) |
| 07 V&V | Verify model, validate + calibrate | ❌ 3 problemer — se nedenfor |
| 08 Output Analysis | Replikationsantal + CI | ✅ OK |
| 09 Experimental | Scenario-design + resultater med figurer (s. 12b) | ⚠️ OFAT+kombination ✅, demand-tabel `[\,]` + I4.0 `[\,]` + throughput bar chart er placeholder |
| 10 Conclusions | Managerielle indsigter med konkrete tal | ❌ Fuld af placeholders: `[x]`, `[\,]`, `[N]`, `[M]` |

### Detaljer: 07 V&V — 3 fejl

1. **Validation-bullet** (linje 18–20) siger `"packaging is expected constraint"` — FORKERT. Drying er bottleneck. Kapacitetstabellen nedenfor i samme sektion viser rigtigt; bullet-teksten er ikke rettet.
2. **Little's Law** har `[ ]`-placeholders — tallene kendes allerede:
   - WIP = 19.85 batches
   - Throughput rate ≈ 0.102 batches/h
   - Mean flow time W = 200.9 h
   - rate × W = 0.102 × 200.9 = **20.5 ≈ 19.85** ✅
3. **Verification-tabel** (expected vs. simulated) mangler helt.

### Detaljer: 09 ExperimentalStudy — inkonsistens med assignment

Assignment (s. 8) siger I4.0 handler om **press scrap 10%→4%** via tryksensorer.
`09ExperimentalStudy` siger "premix scrap fra ~6% til 4%".
`10Conclusions` siger "press sensors (scrap 10%→4%)" — korrekt.
Ret `09ExperimentalStudy` til at matche assignment + `10Conclusions`.

---

## DELIVERABLES — hvad mangler

| Leverance | Status |
|---|---|
| Gruppe-rapport (PDF) | ⚠️ Næsten — 4 sektioner har holes |
| AnyLogic-model (zippet, ingen logs/binaries) | ✅ Model eksisterer |
| Video Jacob | ❌ Ikke lavet |
| Video makker | ❌ Ikke lavet |

---

## PRIORITERET TODO — næste 24 timer

### Blokkerende (kræver AnyLogic-kørsler)

| # | Kørsel | Parameter(e) | CSV |
|---|---|---|---|
| A | Baseline × 1.25 | `demandMultiplier = 1.25` | `FermaCore_demand1p25.csv` |
| B | Baseline × 1.5 | `demandMultiplier = 1.5` | `FermaCore_demand1p5.csv` |
| C | Baseline × 2.0 | `demandMultiplier = 2.0` | `FermaCore_demand2p0.csv` |
| D | I4.0 press scrap | `premixFailureProbability = 0.04` | `FermaCore_i40_scrap0p04.csv` |
| E | Best combo × 1.25 | `numDryers=2` + `cleaningTeamCapacity=2` + `demandMultiplier=1.25` | `FermaCore_dryer2_cleanTeam2_demand1p25.csv` |

Kørsel E er vigtigst — viser om bedste kombination holder mod 2030.

### Kan gøres nu (ingen simulation)

1. `02Collaboration.tex` — erstat `[Author A]` / `[Author B]` med rigtige navne
2. `07VerificationValidation.tex` linje 18–20 — ret "packaging is expected constraint" → drying
3. `07VerificationValidation.tex` — udfyld Little's Law med kendte tal
4. `09ExperimentalStudy.tex` — ret "premix scrap ~6%" → "press scrap 10%→4%" (konsistens med assignment)
5. Throughput bar chart (Python/matplotlib fra eksisterende CSV'er — kan laves nu)
6. Histogram-figurer til `06InputModeling` (fra distribution fitter output)

### Når simuleringerne er færdige

7. Udfyld `tab:demand` i `09ExperimentalStudy.tex`
8. Udfyld I4.0-resultat i `09ExperimentalStudy.tex`
9. Indsæt alle konkrete tal i `10Conclusions.tex`
10. Sidetal-tjek — **maks 15 sider inkl. forside og indholdsfortegnelse**

### Afsluttende (fredag morgen)

11. Video Jacob (maks 5 min, kamera til intro, egne slides)
12. Video makker (maks 5 min, kamera til intro, egne slides)
13. Zip-fil: `FermaCore_Replication_Harness_Brams.alp` + `FermaCore_input_data.xlsx` — ingen logs, ingen CSV-output
14. Upload til DTU Learn inden 18:00
