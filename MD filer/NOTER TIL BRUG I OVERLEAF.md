# NOTER TIL BRUG I OVERLEAF
**Faktatjekkede analysevinkler — verificeret mod `test_data/` (testV2.0-modellen)**
**Dato: 24. juni 2026**

> Alle tal nedenfor er trukket direkte fra CSV'erne i `test_data/`. Brug dem som de står — de tre "topniveau-vinkler" er fakta-tjekket, og to af dem skulle reframes fordi den oprindelige formulering ikke holdt mod data. Læs advarslerne før noget skrives i rapporten.

---

## 1. Design of Experiments (DOE) — BRUG, men korrekt framet

DOE > OFAT er pensum-guld (Law & Kelton, Banks et al.) fordi det fanger interaktionseffekter. Lav et fuldt $2^2$ faktorielt design på **dryer × cleaningTeam** og inkludér **Main Effects Plot** + **Interaction Plot**.

### Faktiske effekter (på `bottlesShipped`, fra test_data/)

| Cellet design | Bottles |
|---|---|
| dryer=1, clean=1 (baseline) | 60.972 |
| dryer=2, clean=1 | 60.880 |
| dryer=1, clean=2 | 60.918 |
| dryer=2, clean=2 | 60.183 |

| Effekt | Værdi |
|---|---|
| Main effect dryer | **−413 flasker** |
| Main effect clean team | **−376 flasker** |
| Interaktionseffekt | **−322 flasker** |

### ⚠️ FRAMING — kritisk

Skriv **IKKE** "en ekstra tørrer virker kun hvis man også har et ekstra cleaning team" eller "massiv positiv interaktion". Dataene viser det **modsatte**:
- Begge faktorer **sænker** throughput hver for sig.
- Interaktionen er **negativ** (−322), ikke positiv synergi.

### Korrekt narrativ
> Kapacitetsinvestering **flytter flaskehalsen** (dryer → cleaning team → packaging) frem for at hæve output. Den negative interaktion og de negative main effects beviser matematisk, at blind investering i én eller flere maskiner er værdiløs i throughput. Interaktionen er synlig i **utilisation/bottleneck-skift**, ikke i throughput — derfor skal Main Effects + Interaction Plot læses sammen med utilisationstallene.

---

## 2. On-Time Delivery (OTD) / Tardiness — DROP (død med nuværende data)

### Faktiske tal (fra test_data/)

| Scenarie | releaseViolations | OTD% | maxReleaseDev |
|---|---|---|---|
| baseline | 0,00 | 100,0 | 18,50 |
| groupByProduct | 0,00 | 100,0 | 18,50 |
| i40_scrap0p04 | 0,00 | 100,0 | 18,50 |
| dryer2+clean2+pack4 | 0,00 | 100,0 | 18,50 |

### ⚠️ Hvorfor den ikke kan bruges
- `releaseViolations` = **0 i alle scenarier** → OTD er allerede **100%** i baseline. Man kan ikke "forbedre" 100%.
- `maxReleaseDev` er en **konstant 18,50** overalt → opfører sig som en fast parameter, ikke en målt per-batch-forsinkelse. KPI'en er sandsynligvis ikke koblet til en reel due-date-mekanik i modellen.
- Påstanden "groupByProduct forbedrer markant leveringssikkerheden" er derfor **ikke understøttet** — den ville præsentere en flad 100%-søjle og hævde en gevinst der ikke findes.

### Hvis service-level alligevel ønskes
Kræver en **model-ændring + ny kørsel**: indfør reelle leveringsdeadlines pr. batch og mål faktisk tardiness. Ikke realistisk så tæt på deadline — anbefaling: **udelad OTD-vinklen**.

---

## 3. Økonomisk dimension (OPEX / WIP holding cost) — BRUG kun den ene halvdel

### 3a. CAPEX-paradokset ✅ HOLDER — brug det

Managementsprog = penge. Lav en simpel, **eksplicit illustrativ** cost-funktion:
- WIP holding cost: antag €500/batch/dag (bundet kapital)
- Extra dryer OPEX: antag €800/dag
- Extra cleaning team member: antag €300/dag
- Extra packaging line: antag €1.200/dag

For `dryer2_cleanTeam2_packLine4`:
- Extra OPEX = (800+300+1.200) = **€2.300/dag = €16.100/uge**
- Throughput-gevinst ≈ flad (~61k, inden for CI af baseline)
- **Konklusion: massiv OPEX-stigning for nul reel gevinst.**

Sammenlign med I4.0 (press-scrap 10%→4%): **engangs** sensorinvestering, +4.109 flasker/uge (+6,7%) — klart bedst pr. investeret krone, ingen løbende OPEX.

### 3b. WIP-besparelse ❌ DROP

| Scenarie | avgWIP |
|---|---|
| baseline | 19,53 |
| groupByProduct | 19,43 |

Forskel = 0,1 batch (0,5%) → i praksis **identisk**. Skriv **IKKE** at groupByProduct reducerer WIP/kapitalbinding markant — tallet bærer det ikke.

---

## Samlet anbefaling til rapporten

| Vinkel | Verdikt | Handling i Overleaf |
|---|---|---|
| DOE (dryer × clean) | ✅ Brug | Main Effects + Interaction Plot; framing = bottleneck-shift / negativ interaktion, INGEN "synergi" |
| OTD / Tardiness | ❌ Drop | Udelad — OTD=100% overalt, ingen variation |
| Økonomi: CAPEX-paradoks | ✅ Brug | Cost-funktion (illustrativ), €16.100/uge for ~0 gevinst vs. I4.0 |
| Økonomi: WIP-besparelse | ❌ Drop | WIP uændret (19,53 vs. 19,43) |

**Den røde tråd der binder det hele:** Kapacitetsinvestering flytter flaskehalsen og koster penge uden at hæve output. Den eneste reelle gevinst kommer fra **I4.0 (press-scrap 10%→4%, +6,7%) uden CAPEX.**
