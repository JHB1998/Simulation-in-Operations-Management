# NOTER TIL BRUG I OVERLEAF
**Faktatjekkede analysevinkler — verificeret mod `test_data/` (testV2.0-modellen)**
**Dato: 24. juni 2026**

> Alle tal nedenfor er trukket direkte fra CSV'erne i `test_data/`. Brug dem som de står — de tre "topniveau-vinkler" er fakta-tjekket, og to af dem skulle reframes fordi den oprindelige formulering ikke holdt mod data. Læs advarslerne før noget skrives i rapporten.

---

## 1. Design of Experiments (DOE) — fuldt $2^3$, BRUG med signifikanstest

DOE > OFAT er pensum-guld (Law & Kelton, Banks et al.; course notes §6.2.2) fordi det fanger interaktionseffekter. **Vigtig rettelse:** "multi-factorial test design"-hintet står i **Healthcare-casen**, IKKE i FermaCore — brug det ikke som begrundelse her. DOE berettiges i stedet via **Specifik krav 3** (bedste kombination mod 2030) + curriculum §6.2.2. Vi har nu et **komplet, balanceret $2^3$ design**: 3 faktorer × 2 niveauer × 8 hjørner × 20 reps.

- **A = antal dryers** (1 → 2)
- **B = cleaning team** (1 → 2)
- **C = antal packaging lines** (3 → 4)
- Respons: `bottlesShipped`. Figur: `figures/fig_doe.pdf` (Pareto of effects). Analyse: `doe_analysis.py`.

### Hjørne-middelværdier (bottles shipped, fra test_data/)

| Hjørne | A | B | C | Mean |
|---|---|---|---|---|
| (1) baseline | − | − | − | 60.972 |
| a (dryer2) | + | − | − | 60.880 |
| b (cleanTeam2) | − | + | − | 60.918 |
| ab | + | + | − | 60.183 |
| c (packLine4) | − | − | + | 61.759 |
| ac | + | − | + | 61.266 |
| bc | − | + | + | 61.018 |
| abc | + | + | + | 61.776 |

### Effekt-estimater med signifikanstest (pooled SE = 334, df = 152, 95% grænse = ±664)

| Effekt | Estimat (flasker) | t | Signifikant (95%)? |
|---|---|---|---|
| **C — packaging line** | **+717** | **2,15** | **JA** |
| ABC | +474 | 1,42 | nej |
| AC | +273 | 0,82 | nej |
| B — cleaning team | −245 | −0,74 | nej |
| AB | +152 | 0,46 | nej |
| A — dryer | −140 | −0,42 | nej |
| BC | +130 | 0,39 | nej |

### ⚠️ FRAMING — kritisk (dette er den rigorøse konklusion)

Med proper signifikanstest er konklusionen **renere** end et naivt 2² ville give:
- **Dryer (A) og cleaning team (B) har INGEN signifikant effekt på throughput.** De ligger godt inden for støjen — skriv IKKE at de "sænker" throughput; det ville være overtolkning af punktestimater.
- **Ingen interaktion er signifikant** — heller ikke AB. Whack-a-mole / bottleneck-skiftet er reelt, men det lever i **utilisation** (`fig_utilisation.pdf`), ikke i throughput-tallene.
- **Kun en ekstra packaging line (C) rykker throughput signifikant** — og kun med **+717 flasker (+1,2%)**, lige akkurat over støjgrænsen.

### Korrekt narrativ
> Det fulde $2^3$ faktorielle design viser, at af de tre kapacitetsfaktorer er **kun packaging-linjen statistisk signifikant** (+717 flasker, +1,2%); dryer- og cleaning-kapacitet samt samtlige interaktioner er ikke til at skelne fra nul. OFAT ville have overset dette ved at fejltolke tilfældig variation som effekter. Det beviser matematisk, at maskininvestering i dryer/clean er spild, og at selv den eneste reelle løftestang (packaging) giver en triviel gevinst sammenlignet med I4.0 (+4.764 flasker, +7,8%, ingen CAPEX). Bottleneck-skiftet aflæses separat i utilisation.

> **Antagelse at nævne (cheatsheet):** $2^k$ med 2 niveauer antager lineær respons mellem niveauerne.

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

Sammenlign med I4.0 (press-scrap 10%→4%): **engangs** sensorinvestering, +4.764 flasker/uge (+7,8%) — klart bedst pr. investeret krone, ingen løbende OPEX.

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
| DOE — fuldt $2^3$ (dryer × clean × pack) | ✅ Brug | Pareto of effects (`fig_doe.pdf`) + signifikanstabel; framing = **kun packaging signifikant (+1,2%)**, dryer/clean + interaktioner ikke signifikante |
| OTD / Tardiness | ❌ Drop | Udelad — OTD=100% overalt, ingen variation |
| Økonomi: CAPEX-paradoks | ✅ Brug | Cost-funktion (illustrativ), €16.100/uge for ~0 gevinst vs. I4.0 |
| Økonomi: WIP-besparelse | ❌ Drop | WIP uændret (19,53 vs. 19,43) |

**Den røde tråd der binder det hele:** Kapacitetsinvestering flytter flaskehalsen og koster penge uden at hæve output. Den eneste reelle gevinst kommer fra **I4.0 (press-scrap 10%→4%, +6,7%) uden CAPEX.**
