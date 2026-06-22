# Building the FermaCore Model in AnyLogic — A Complete, Beginner-Friendly Guide (42417)

This guide assumes **zero** AnyLogic experience. Every term is explained the first time it appears, and every instruction is a literal click-by-click step. Work through it top to bottom; do not skip ahead, because each part depends on the one before it. It uses the exact blocks and function names from your course notes (Chapter 2 "Process Model Library", Chapter 3 "Input Modeling", Chapters 4–5 "Output Analysis"), so everything matches what the examiners taught.

> **This guide documents the model that actually exists in `FermaCore_BASE.alp`** — the block names, conditions, distributions, parameters and helper functions below are the ones in the file, not a generic plan. Where the build uses a particular pattern (Seize/Delay/Release rather than a single Service, a scrap branch rather than a Downtime element) the reason is given.

> **The golden rule:** build the **baseline** model first, get it running and verified, and only *then* add the parameters that let you run the experiments. Resist the urge to model everything at once.

---

## Part 0 — How AnyLogic is laid out (read this once)

When you open AnyLogic 8 you see four areas:

1. **Projects** panel (top-left): a tree of everything in your model — `Main`, your agent types, and your experiments. Think of it as the file explorer for your model.
2. **Palette** panel (bottom-left): the toolbox. The section you need is **Process Modeling Library**. You build the model by *dragging* items ("blocks") from here onto the canvas.
3. **Graphical editor / canvas** (centre): the big white area where you drop blocks and connect them. The main canvas is called **`Main`**.
4. **Properties** panel (right or bottom): when you click any block, its settings appear here. This is where you type capacities, delay times, conditions, etc.

A few vocabulary words you'll see constantly:

- **Agent** = one moving "thing" in the model. For us, **one agent = one process-batch**. The plan gives each batch as **150 kg of active-ingredient powder blend**; **75 kg of excipients is added in premix**, giving a **225 kg** batch that yields **300,000 tablets** (each tablet = 500 mg active + 250 mg excipient = 750 mg).
- **Block** = one operation or rule (e.g. a machine, a queue, a router). You connect blocks with lines so agents flow Source → … → Sink.
- **Resource** = something an agent needs to *use* to be processed (a machine, the cleaning team). Resources live in a **Resource Pool**.
- **Port** = the little dot on the edge of a block where connection lines attach (`in` on the left, `out` on the right).

To **run** the model: click the green ▶ play button in the toolbar. To **stop**: the red ■ button. While running you can hover over a block to see live counts (how many agents passed through, how many are inside).

---

## Part 1 — Create the project and set time correctly

### 1.1 New model
1. **File → New → Model**.
2. Name it `FermaCore`. Click **Finish**. You now have an empty `Main`.

### 1.2 Set the model time unit to **hours**
All our processing times are in hours, so we make the model "tick" in hours.
1. In **Projects**, click **Simulation: Main** (this is the default experiment).
2. In **Properties**, find the **Model time** section.
3. Set **Model time units = hours**.

> Why it matters: if the model unit is seconds but you type a delay of "2" meaning 2 hours, every machine will be 3,600× too fast. Keep everything in hours; where a value is naturally in minutes or days, use that field's own unit dropdown.

### 1.3 Set the stop condition
This baseline drives arrivals from the plan with a **limited number of arrivals** (50 batches — see Part 3), so the run ends naturally once the last batch ships. Set **Stop = Never** and stop manually, or **Stop at specified time** safely after the last batch clears packaging. Because arrivals are interarrival-driven (not calendar dates), you do **not** need to pin a real start date for the baseline to line up.

---

## Part 2 — Tell AnyLogic what a "batch" is (the agent type)

Before agents can flow, we define what one agent looks like. In this model the product is stored as a **String** (`"CoreTab"`, `"PlusTab"`, `"MaxTab"`), not an enumeration — the helper functions compare it with `product.equals("CoreTab")` etc., so keep the spelling exact.

### 2.1 Create the Batch agent type
1. In the **Palette → Process Modeling Library**, find **Agent Type** at the top. Drag it onto `Main`.
2. The **New agent** wizard opens:
   - Choose **I want to create a new agent type**. Click **Next**.
   - **Agent type name:** `Batch`. Click **Next**.
   - For animation choose **None**. Click **Next**, then **Finish**.
3. In **Projects**, double-click **Batch** to open its own diagram.

### 2.2 Add the batch's fields (parameters & variables)
On the **Batch** diagram, drag these from the **Agent** palette. These are the exact fields the model reads and writes:

| Field | Type | Initial | Purpose |
|---|---|---|---|
| `product` | String | `""` | `"CoreTab"`, `"PlusTab"` or `"MaxTab"` — set at the Source from the plan |
| `batchKg` | double | `150` | active-ingredient blend weight |
| `tablets` | double | `300000` | good tablets remaining in the batch (reduced by yields) |
| `arrivalTime` | double | `0` | model time the batch entered the line (for flow time) |
| `premixUnit` | String | `""` | `"New"` or `"Old"` — which blender served it |
| `premixProcessTime` | double | `0` | the batch's sampled premix duration (used by the failure model) |
| `premixYield` | double | `0` | sampled premix yield factor |
| `packYield` | double | `0` | sampled packaging yield factor |
| `scrapped` | boolean | `false` | set true if the batch is scrapped at premix |
| `productChanged` | boolean | `false` | true if this batch caused a packaging changeover |
| `packLineIndex` | int | `-1` | which packaging line it used (changeover logic) |
| `bottlesShipped` | int | `0` | bottles produced from this batch |

> **Mass cross-check (from the TA hint).** The plan's kg is the *active-ingredient powder blend only*. Excipients (75 kg per 150 kg active) are added in premix, so the batch is 225 kg from premix onward — exactly the "one batch of 225 kg" the case quotes for the 2 h compression step. Tablet count is fixed by the active mass: **2,000 tablets per kg active**, i.e. `150 × 2000 = 300,000`. Reading 150 kg as the *whole* batch would give 200,000 tablets — a 33% undercount that would corrupt packaging time and throughput.

### 2.3 Helper functions on `Main` (not on the Batch)
These live on `Main` and take the batch (or its product string) as an argument. Create them in Part 4.9; they are listed here so the names are familiar:

- `bottleSize(String product)` → `int`: `return product.equals("MaxTab") ? 300 : 180;` (CoreTab and PlusTab both 180.)
- `needsCoating(String product)` → `boolean`: `return !product.equals("CoreTab");`

Go back to `Main` (double-click **Main** in Projects).

---

## Part 3 — The production plan (arrays on `Main`, interarrival arrivals)

This model does **not** use AnyLogic's Database arrival table. Instead the 50-batch plan lives in two arrays on `Main`, and the Source uses **interarrival times**:

- `arrivalTimes` — array of the planned arrival instants (hours).
- `productPlan` — array of the product strings, one per batch, in plan order.
- `sourceIndex` — int counter, incremented as each batch is created.

The Source asks a function for the gap to the next batch:

```java
// arrivalDelay() on Main — converts the absolute plan to interarrival gaps,
// scaled by demandMultiplier (the 2030 lever).
int i = Math.max(0, sourceIndex - 1);
if (i < arrivalTimes.length - 1) {
    return Math.max(0.0, (arrivalTimes[i + 1] - arrivalTimes[i]) / demandMultiplier);
}
return 1.0e9; // no more arrivals after the plan is exhausted
```

Populate `arrivalTimes` and `productPlan` from your `FermaCore_input_data.xlsx` plan however you prefer (read the sheet on **Agent → On startup**, or paste the values). The only requirements are that both arrays hold the 50 plan rows in order and that the Source is limited to 50 arrivals (Part 4.1).

---

## Part 4 — Build the baseline flowchart (block by block)

You'll drag blocks onto `Main` left-to-right and connect each block's `out` port to the next block's `in` port. The exact chain in the file is:

```
src → selectPremix → (seizeNew→delayPremixNew→releaseNew | seizeOld→delayPremixOld→releaseOld)
    → premixFailureCheck → [sinkScrapped]
    → seizeGran→delayGran→releaseGran
    → seizeDryer→delayDrying→seizeCleanTeam_Dry→delayDryingClean→releaseCleanTeam_Dry→releaseDryer
    → seizePress→delayCompress→releasePress
    → coreTabCheck → (seizeCoater→delayCoating→seizeCleanTeam_Coat→delayCoatClean→releaseCleanTeam_Coat→releaseCoater | bypass)
    → seizePackLine→seizeCleanTeam_Pkg→delayPkgSetup→releaseCleanTeam_Pkg→delayPackaging→releasePackLine
    → sinkShipped
```

### 4.0 Create the Resource Pools first
A **Resource Pool** is a set of identical units an agent must *seize* to be processed. Drag **Resource Pool** once per row below; set **Capacity** in Properties (capacity defined directly, or by a parameter — see Part 5). Leave **Resource type = Static**.

| Resource Pool name | Capacity | Represents |
|---|---|---|
| `blenderNew` | `numBlenders_New` (1) | new (fast) blender |
| `blenderOld` | `numBlenders_Old` (1) | old (slow) blender |
| `granulator` | 1 | granulation unit |
| `dryer` | `numDryers` (1) | drying unit |
| `press` | `numPresses` (3) | tablet presses |
| `coater` | 1 | coating unit |
| `packagingLine` | `numPackagingLines` (3) | packaging lines |
| `cleaningTeam` | `cleaningTeamCapacity` (1) | the **single shared** cleaning team |

> **Naming matters.** Whatever you name a Resource Pool is exactly how you refer to it in Java later (e.g. `cleaningTeam.utilization()`, `blenderNew.idle()`). A typo here = silent failure later.

### 4.1 Source — `src`
1. Drag **Source**, name it `src`.
2. **Properties:**
   - **Arrivals defined by:** **Interarrival time**.
   - **Interarrival time:** `arrivalDelay()`.
   - **Limited number of arrivals:** ticked, **Maximum arrivals:** `50` (the plan size).
   - **New agent:** `Batch`.
3. **Actions → On exit:**
```java
int i = Math.min(sourceIndex, productPlan.length - 1);
agent.product   = productPlan[i];
agent.batchKg   = 150;
agent.tablets   = 300000;
agent.arrivalTime = time();
sourceIndex++;
```

### 4.2 Premix — routed parallel units, built as Seize/Delay/Release
The old and new blenders run **in parallel** at **different** speeds. We route each batch to the new unit if it's free, and build each branch as explicit **Seize → Delay → Release** (not a single Service) so the resource accounting is unambiguous.

**Router — `selectPremix` (SelectOutput).** **Select True output → Condition:**
```java
blenderNew.idle() > 0
```
`outT` → new branch (fast). `outF` → old branch (slow).

**New branch:**
- **Seize** `seizeNew` → `blenderNew`.
- **Delay** `delayPremixNew` → delay time `premixDurationNew(agent)`; **On enter:** `agent.premixUnit = "New";` **On exit:** `agent.premixYield = triangular(0.985, 0.990, 0.995); agent.tablets = 300000 * agent.premixYield;`
- **Release** `releaseNew` → `blenderNew`.
- Connect `selectPremix.outT → seizeNew → delayPremixNew → releaseNew`.

**Old branch:**
- **Seize** `seizeOld` → `blenderOld`.
- **Delay** `delayPremixOld` → delay time `premixDurationOld(agent)`; **On enter:** `agent.premixUnit = "Old";` **On exit:** same yield line as above.
- **Release** `releaseOld` → `blenderOld`.
- Connect `selectPremix.outF → seizeOld → delayPremixOld → releaseOld`.

The two duration functions (Part 4.9) return:
```java
// premixDurationNew:  double d = triangular(3.5, 4.5, 4.0); a.premixUnit="New"; a.premixProcessTime=d; return d;
// premixDurationOld:  double d = triangular(4.5, 6.5, 5.5); a.premixUnit="Old"; a.premixProcessTime=d; return d;
```
(AnyLogic `triangular(min, max, mode)`.)

### 4.3 Premix failure — a probabilistic batch-scrap branch
A premix failure during processing destroys the whole batch. This is modelled **not** with a Downtime element but with a **SelectOutput** that scraps the batch probabilistically, where the probability comes from the workbook failure frequencies.

1. Drag **SelectOutput**, name `premixFailureCheck`. Connect both `releaseNew.out` and `releaseOld.out` into its `in`.
2. **Select True output → Condition:**
```java
uniform(0, 1) < premixFailureRate(agent)
```
3. `outT` → **Sink** `sinkScrapped`. On `sinkScrapped` **On enter:** `agent.scrapped = true; batchesScrapped++;`
4. `outF` → continue to granulation.

The failure-rate function (Part 4.9) turns each blender's mean-time-between-failures into a per-batch scrap probability over the batch's sampled premix duration:
```java
// premixFailureRate(Batch a):
if (premixFailureProbability >= 0) {                 // manual override knob
    return Math.max(0.0, Math.min(1.0, premixFailureProbability));
}
double duration = a.premixProcessTime > 0 ? a.premixProcessTime
                  : (a.premixUnit.equals("Old") ? 5.5 : 4.0);
double mtbfHours = a.premixUnit.equals("Old") ? 54.164718 : 168.0;  // from weibull(1.5,2.5)/weibull(0.5,3.5) days
mtbfHours *= mtbfMultiplier;                          // Industry 4.0 / predictive-maintenance lever
double p = 1.0 - Math.exp(-duration / mtbfHours);     // exponential hazard over the batch's premix time
return Math.max(0.0, Math.min(0.95, p));
```

> The Weibull failure frequencies from the workbook are used to derive the **mean** MTBF per unit; the per-batch scrap chance is then an exponential-hazard approximation over the batch's own premix duration. `mtbfMultiplier` (default 1.0) is the lever that *extends* MTBF — that is the Industry 4.0 / predictive-maintenance scenario. `premixFailureProbability` (default −1.0) forces a fixed probability when ≥ 0, otherwise the MTBF model is used.

### 4.4 Granulation
- **Seize** `seizeGran` → `granulator`; **Delay** `delayGran` → `normal(1.0, 0.1)` hours (AnyLogic `normal(mean, sd)`); **Release** `releaseGran` → `granulator`.
- Connect `premixFailureCheck.outF → seizeGran → delayGran → releaseGran`.

### 4.5 Drying + its 2-hour clean (shared cleaning team)
Drying holds the dryer for the drying time **and** through a 2 h clean, during which the cleaning team is also seized. Build it as:
- **Seize** `seizeDryer` → `dryer`.
- **Delay** `delayDrying` → `dryingTime()` (returns `triangular(2.703493, 5.541093, 3.748756)` — the fitted drying time).
- **Seize** `seizeCleanTeam_Dry` → `cleaningTeam`.
- **Delay** `delayDryingClean` → `2.0` hours.
- **Release** `releaseCleanTeam_Dry` → `cleaningTeam`.
- **Release** `releaseDryer` → `dryer`.
- Connect in that order. Because the dryer is released only *after* the clean, it can't take the next batch until cleaning is done.

### 4.6 Compression
- **Seize** `seizePress` → `press`; **Delay** `delayCompress` → `2.0` hours; **Release** `releasePress` → `press`.
- **No scrap is applied here** — compression is a flat 2 h step on 3 presses.

### 4.7 Coating — CoreTab bypasses, others coated + 1-hour clean
1. **SelectOutput** `coreTabCheck`. **Condition:**
```java
!needsCoating(agent.product)   // true for CoreTab → bypass
```
   - `outT` (CoreTab) → straight to `seizePackLine` (bypass).
   - `outF` (PlusTab/MaxTab) → coating chain.
2. Coating chain (same pattern as drying):
   - **Seize** `seizeCoater` → `coater`.
   - **Delay** `delayCoating` → `triangular(1.5, 2.0, 2.5)` hours.
   - **Seize** `seizeCleanTeam_Coat` → `cleaningTeam`.
   - **Delay** `delayCoatClean` → `1.0` hour.
   - **Release** `releaseCleanTeam_Coat` → `cleaningTeam`.
   - **Release** `releaseCoater` → `coater`.
3. Connect both `releaseCoater.out` and `coreTabCheck.outT` into `seizePackLine.in`.

### 4.8 Packaging — line, setup/changeover (cleaning team), pack, yield, bottling
1. **Seize** `seizePackLine` → `packagingLine`. **On exit:** `assignPackagingLine(agent);` (chooses a line, sets `packLineIndex`, flags `productChanged`, marks the line busy).
2. **Seize** `seizeCleanTeam_Pkg` → `cleaningTeam` (the team does the setup/changeover).
3. **Delay** `delayPkgSetup` → `packagingSetupTime(agent)`; **On enter:** `agent.productChanged = isPackagingChangeover(agent);`
   where `packagingSetupTime` returns `0.5 + (isPackagingChangeover(a) ? 0.5 : 0.0)`.
4. **Release** `releaseCleanTeam_Pkg` → `cleaningTeam` (free the team for the long packing delay).
5. **Delay** `delayPackaging` → `agent.tablets / 30000.0` hours (30,000 tablets/hour per line); **On enter:** `agent.packYield = triangular(0.990, 0.995, 0.998); agent.tablets = agent.tablets * agent.packYield;`
6. **Release** `releasePackLine` → `packagingLine`. **On exit:** `releasePackagingLine(agent);` (records last product on the line, frees it).

### 4.9 Sink — `sinkShipped`
Connect `releasePackLine.out → sinkShipped.in`. **On enter:**
```java
int bs = bottleSize(agent.product);
agent.bottlesShipped = (int) Math.floor(agent.tablets / bs);
agent.tablets = agent.bottlesShipped * bs;       // leftover tablets are not bottled
totalBottlesShipped += agent.bottlesShipped;
totalTabletsShipped += agent.tablets;
totalFlowTime += time() - agent.arrivalTime;
maxFlowTime = Math.max(maxFlowTime, time() - agent.arrivalTime);
batchesShipped++;
```

### 4.10 The line-assignment helpers (on `Main`)
These implement "prefer an idle line that already ran this product, else any idle line, to avoid changeovers":
- `choosePackagingLine(String product)` → `int`
- `assignPackagingLine(Batch a)` — sets `a.packLineIndex`, `a.productChanged`, `packLineBusy[i]=true`
- `isPackagingChangeover(Batch a)` → `boolean` (compares `a.product` with `lastProductOnPackLine[i]`)
- `releasePackagingLine(Batch a)` — writes `lastProductOnPackLine[i]=a.product`, frees the line
The arrays `lastProductOnPackLine[]`, `packLineBusy[]` and the fallback `lastProductOnLine` live on `Main`. The boolean `groupByProduct` (default off) is the sequencing lever.

You now have a complete baseline flowchart. **Do not add experiments yet** — first make it run (Part 8).

---

## Part 5 — The model's knobs (parameters on `Main`)

To run every scenario from one file, the things you change are **parameters** on `Main`. These are the parameters/levers in the file:

| Parameter | Type | Default | Used for |
|---|---|---|---|
| `numBlenders_New` | int | 1 | `blenderNew` capacity |
| `numBlenders_Old` | int | 1 | `blenderOld` capacity |
| `numDryers` | int | 1 | `dryer` capacity |
| `numPresses` | int | 3 | `press` capacity |
| `numPackagingLines` | int | 3 | `packagingLine` capacity |
| `cleaningTeamCapacity` | int | 1 | `cleaningTeam` capacity |
| `demandMultiplier` | double | 1.0 | 2030 demand sweep (scales arrivals via `arrivalDelay()`) |
| `mtbfMultiplier` | double | 1.0 | **Industry 4.0** — extends premix MTBF, lowers scrap |
| `groupByProduct` | boolean | false | sequencing lever (group batches by product to cut changeovers) |
| `premixFailureProbability` | double | −1.0 | manual override of the per-batch scrap probability (−1 = use MTBF model) |

Set each Resource Pool's **Capacity** to its matching parameter (e.g. `packagingLine` capacity = `numPackagingLines`). After this, changing one parameter reconfigures the whole model.

---

## Part 6 — Collect the KPIs

The four headline KPIs are throughput, utilisation per station, flow time, and WIP/queue, plus scrap/yield. The model already keeps the counters below on `Main`.

### 6.1 Throughput
`totalBottlesShipped` and `batchesShipped` (incremented at `sinkShipped`). `totalTabletsShipped` tracks bottled tablets. For per-product throughput, branch on `agent.product`.

### 6.2 Utilisation per station
Each pool reports its own utilisation:
```java
dryer.utilization()        // 0..1; expected highest (the bottleneck)
cleaningTeam.utilization()
packagingLine.utilization()
press.utilization()
```
The station nearest 1.0 is the constraint. Make sure **statistics collection** is enabled on each pool.

### 6.3 Flow time
The model accumulates flow time directly at the sink via `agent.arrivalTime`:
```java
// meanFlowTime() on Main:
return batchesShipped > 0 ? totalFlowTime / batchesShipped : 0;
```
`maxFlowTime` holds the worst case. (No TimeMeasure blocks are used — flow time is `time() - agent.arrivalTime` summed at `sinkShipped`.)

### 6.4 WIP / queue per station
Each Seize block keeps its own internal queue; enable statistics and read its queue size, or place a **Queue** block before a Seize and read `queueName.size()`.

### 6.5 Scrap / yield
```java
// scrapRate() on Main:
int total = batchesShipped + batchesScrapped;
return total > 0 ? ((double) batchesScrapped) / total : 0;
```
Overall tablet yield = `totalTabletsShipped` divided by tablets started (`batchesShipped + batchesScrapped` batches × 300,000), capturing premix yield, packaging yield, bottle remainders and scrapped batches.

---

## Part 7 — Input modelling: what was fitted vs. given

Only **one** processing distribution was fitted from data; the rest are given in the plan/case, and the failure frequencies feed the MTBF model rather than a Downtime element.

| Quantity | Source | Distribution in the model |
|---|---|---|
| **Drying time** (h) | **Fitted** from 300 `DryingConditioning` observations (min 2.7035, max 5.5411, mean 3.9978) | `triangular(2.703493, 5.541093, 3.748756)` — mode inferred as `3·mean − min − max = 3.748756` |
| Premix new / old (h) | Given | `triangular(3.5,4.5,4.0)` / `triangular(4.5,6.5,5.5)` |
| Granulation (h) | Given | `normal(1.0, 0.1)` |
| Coating (h) | Given | `triangular(1.5, 2.0, 2.5)` |
| Premix yield | Given | `triangular(0.985, 0.990, 0.995)` |
| Packaging yield | Given | `triangular(0.990, 0.995, 0.998)` |
| Premix failure frequency | Workbook | Weibull `weibull(1.5,2.5)` days (old) / `weibull(0.5,3.5)` days (new) → mean MTBF 54.16 h / 168.0 h, used in `premixFailureRate` |

> Document in the report that **drying** was the fitted quantity (use the course Python/Jupyter distribution fitter on the `DryingConditioning` column and screenshot the histogram-with-overlay), and that the Weibull failure frequencies were converted into a per-batch scrap probability rather than a machine-downtime process. There are no lognormal repair distributions in the baseline because there is no Downtime element.

---

## Part 8 — Verify the model (make it run, then make it right)

1. Click ▶. If a red error appears, read the bottom **Console** — it names the block and the problem (Part 11).
2. **Single-batch trace:** hover over each block while running; confirm counts add up (50 in at `src`, `batchesShipped + batchesScrapped ≈ 50` at the end).
3. **Routing check:** confirm CoreTab batches skip coating (compare `coreTabCheck` outT vs outF counts).
4. **Conservation check:** bottled tablets + scrapped + bottle remainders ≈ batches × 300,000 after the two yields.
5. **Degenerate tests:**
   - Set `premixFailureProbability = 0` → `batchesScrapped` should stay 0.
   - Raise `mtbfMultiplier` a lot → scrap should fall toward 0 (sanity-checks the Industry 4.0 lever).
   - Set `groupByProduct = true` on a mixed plan → changeover count (and cleaning-team load) should drop.

When the numbers behave, the model is **verified**. Then **validate**: confirm the simulated bottleneck is **drying** (`dryer.utilization()` highest, cleaning team a close second), matching your hand calculation of required unit-hours.

---

## Part 9 — Output analysis: how many replications?

The model is random, so one run isn't enough. Run many replications and average; use **Rossetti's half-width method** to decide how many.

### 9.1 Build the experiment
1. **Projects** → right-click the model → **New → Experiment** → **Parameter Variation**. Name it `ReplicationsExp`, top agent `Main`.
2. **Properties:**
   - **Parameters: Type = Fixed value** (replicate the baseline; don't vary anything yet).
   - **Replications: Varying number of replications** — set a minimum (e.g. 5), a maximum (e.g. 200) and a confidence/precision target.
   - Tick **Allow parallel evaluation**.
3. In **After simulation run**, append the headline KPI (`root.totalBottlesShipped`) to a dataset.

### 9.2 Size N with the half-width formula
Run ~10 pilot replications, read mean `x̄` and sd `s` of throughput, then `n ≥ ( t(n0−1,1−α/2)·s/ε )²` with α = 0.05 and ε your acceptable half-width (5–10% of the mean). Report mean, s, half-width and CI bounds for each KPI; size on throughput and report CIs for the rest.

---

## Part 10 — Run the experiments (all from one model)

Reuse the same `.alp`; only change parameters in Parameter Variation experiments.

1. **Baseline:** the replication run above → confirm the bottleneck via `utilization()`.
2. **OFAT screening** (one lever at a time):
   - `numPackagingLines` 3 → 4
   - `numDryers` 1 → 2
   - `cleaningTeamCapacity` 1 → 2
   - `groupByProduct` false → true
   Rank the levers by throughput gain.
3. **2^k factorial:** take the top ~3 levers, two values each; every combination is one run — reveals interactions and the best combination.
4. **2030 demand sweep:** vary `demandMultiplier` (1.0 → 1.25 → 1.5 → 2.0) on baseline and best config; find the largest demand the line still clears.
5. **Industry 4.0 (predictive maintenance):** raise `mtbfMultiplier` (e.g. ×2, ×3) so premix MTBF extends and the per-batch scrap probability falls; report the gain in good bottles/week, ideally combined with the best config.

For each, export KPI means + CIs and make bar charts with error bars for the report (§9).

---

## Part 11 — Common errors and how to fix them

- **"Cannot find symbol `cleaningTeam`/`blenderNew`"** → a name typo, or you renamed a Resource Pool. Java names must match block names exactly.
- **Utilisation / queue stats empty or 0** → statistics not enabled on that pool. Enable and re-run.
- **No flow-time value** → flow time is accumulated at `sinkShipped` from `agent.arrivalTime`; check that `arrivalTime` is set at `src` (On exit) and that the sink's On-enter block runs.
- **All batches arrive at time 0 / none arrive** → the Source isn't in **Interarrival time** mode, `arrivalDelay()` isn't wired, or `arrivalTimes`/`productPlan` weren't populated.
- **Machines finish instantly or take forever** → model time unit isn't hours, or a Delay's unit dropdown is wrong.
- **Premix routing sends everything to one unit** → `selectPremix` condition is backwards; `outT` is true. `blenderNew.idle() > 0` sends to the new unit on true.
- **Nothing is ever scrapped** → `premixFailureProbability` is ≥ 0 and pinned to 0, or `mtbfMultiplier` is huge. Set `premixFailureProbability = -1.0` to use the MTBF model.
- **Tablets don't conserve** → a yield line uses `=` instead of `*` correctly, or a yield is applied twice. Premix yield is applied once at `delayPremixNew/Old` On exit; packaging yield once at `delayPackaging` On enter.

---

## Part 12 — Optional: a 3D animation of the line (for your video)

A 3D view is **not required**, but it makes a strong individual video. Build it **only after the model runs and is verified**.

### 12.1 Lay out the line as a network (Space Markup)
Drag one **Point Node** per station and name them to match your blocks: `nSrc`, `nPremixNew`, `nPremixOld`, `nGran`, `nDryer`, `nPress`, `nCoat`, `nPack`, `nSink`. Connect them in flow order with **Path** elements (endpoints light cyan when snapped). Add short paths in front of the busy stations (drying, packaging) as visible queue lines.

### 12.2 Tell each block where to animate
- **Source `src`** → **Location of arrival** = `nSrc`.
- Each **Seize/Delay** → **Agent location** = its matching node (e.g. `delayCompress` → `nPress`, `delayDrying` → `nDryer`).
- **Sink `sinkShipped`** needs nothing.
Run in 2D: default shapes should hop node to node.

### 12.3 Give the batch a 3D shape
Open the **Batch** agent type, drag a 3D **Box** or **Cylinder** onto the origin, size ~0.8 m, and colour by product:
```java
product.equals("CoreTab") ? gray :
product.equals("PlusTab") ? dodgerBlue : orange
```

### 12.4–12.7 Machines, 3D window, polish, pitfalls
Place simple **Geometric** boxes/cylinders (or imported `.obj/.dae`) on each node as machine stand-ins; label them with **Text** shapes. Drag a **3D Window** onto an empty area of `Main` (not over the 2D layout), optionally aim a **Camera**, and run. Common pitfalls: batches invisible → no 3D shape on the Batch; agents don't move → an **Agent location** unset or a Path unsnapped; everything tiny/huge → the 3D-object scale prompt; blank 3D window → it overlaps the 2D shapes.

> Keep the 3D effort proportionate: it earns presentation marks, not analysis marks.

## What "done" looks like

A single `.alp` that: drives 50 batches from the plan arrays via interarrival times; flows each batch through premix (routed parallel Seize/Delay/Release, with a **probabilistic batch-scrap** at `premixFailureCheck`), granulation, drying (+2 h clean), compression (flat 2 h, no scrap), coating (CoreTab bypass, +1 h clean), and packaging (line assignment, setup/changeover by the cleaning team, pack, yield, bottling); reports throughput, per-station utilisation, mean/max flow time, WIP and scrap/yield; runs as a Parameter Variation with enough replications for 95% confidence; and re-runs every scenario by changing parameters (`numDryers`, `numPackagingLines`, `cleaningTeamCapacity`, `groupByProduct`, `demandMultiplier`, `mtbfMultiplier`). Build it in that order, verify after Part 4, and you'll never be more than one block away from a working model.
