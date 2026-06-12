# Analyst Report

Generated: 2026-06-10T06:56:46.910067
Models: deepseek-v3
Troll mode: progressive

## Data Availability

  deepseek-v3 @ progressive (0→4→8→16 trolls): B, GR, C, M, G, NR, S, J, E (9/9 conditions)

---

# Sustaining Cooperation Among Self-Interested LLM Agents Under Progressive Adversarial Stress
## A Comparative Analysis of 9 Institutional Mechanisms (DeepSeek-V3, Progressive Troll Injection)

---

## 1. EXECUTIVE SUMMARY

The single most important takeaway is that **mechanism design, not information transparency, drives robustness — and the relationship between a mechanism and welfare is non-monotonic in a way that defies intuition.** The best performer, **mediation (M, overall non-troll utility 7.78)**, actually *increased* welfare as trolls escalated (6.37 at 0 trolls → 8.15 at 16 trolls), while two punitive enforcement mechanisms designed specifically to deter defection — **costly sanctions (S, 3.42)** and **judicial complaint courts (J, 4.26)** — produced the *worst* welfare outcomes, below the no-mechanism baseline (B, 6.05). Critically, the second-best performer, **escrow (E, 6.91)**, carries a catastrophic tail risk: its design includes a pool-collapse clause that resets all agents to zero utility, and the data shows utility cratering to near-zero in late rounds for the structurally analogous GR condition. The mechanisms that best resisted *inequality* growth under stress were **contracting (C, Gini ~0.25–0.28 stable)** and **governance (G, ~0.28 stable)**, both of which suppressed trade volume to do so. The headline lesson: **the most "intuitive" deterrence mechanisms (peer punishment, courts) backfire by imposing costs on the cooperative majority, while structural facilitation (mediation, escrow) sustains and even grows cooperation under adversarial load** — but **all conclusions rest on single runs per cell and must be treated as hypotheses, not established effects.**

---

## 2. DATA COVERAGE

**Available:** All 9 conditions (B, GR, C, M, G, NR, S, J, E) for deepseek-v3 under the progressive schedule (0→4→8→16 trolls), with full 200-round per-round tables and 4-phase summary statistics.

**Missing / Limitations:**
- **`mean_utility.mean` is `null` in every phase summary** for every condition. Only `non_troll_mean_utility` (a single scalar per phase) and per-round `AvgUtil` are available. Phase-level dispersion (std, CI) is unavailable.
- **Single run per condition.** There is no replication. Every numeric comparison below is **n=1**. Differences smaller than the visible round-to-round noise (which is large — e.g., B's per-round AvgUtil swings from 2.50 to 11.00) cannot be treated as significant.
- **No total-rounds or market-health signal given to agents** (by design), so agents cannot anticipate phase transitions.
- **Only one model** (DeepSeek-V3). No cross-model generalization possible.
- **The escrow pool-collapse event is never explicitly logged** as triggered in the data provided; I infer near-collapse risk from low late-round AvgUtil values but cannot confirm a reset occurred. **Flagged as inference.**

**Every quantitative claim in this report is single-run evidence and should be replicated before any design decision.**

---

## 3. MECHANISM RANKING

Ranked by overall non-troll mean utility (primary robustness proxy), with inequality as secondary criterion. **All values single-run.**

| Rank | Cond | Mechanism | Util 0T | Util 4T | Util 8T | Util 16T | Overall Util | Gini 0T | Gini 4T | Gini 8T | Gini 16T |
|------|------|-----------|---------|---------|---------|----------|--------------|---------|---------|---------|----------|
| 1 | **M** | Mediation | 7.17 | 7.76 | 8.05 | 8.15 | **7.78** | 0.271 | 0.300 | 0.329 | 0.333 |
| 2 | **E** | Escrow | 7.29 | 6.84 | 6.88 | 6.64 | **6.91** | 0.285 | 0.312 | 0.348 | 0.369 |
| 3 | **NR** | Network rewiring + local rep | 6.78 | 6.83 | 6.71 | 6.72 | **6.76** | 0.317 | 0.313 | 0.316 | 0.298 |
| 4 | **G** | Governance (oracle) | 6.36 | 6.32 | 6.71 | 6.37 | **6.44** | 0.284 | 0.284 | 0.273 | 0.286 |
| 5 | **B** | Baseline | 6.37 | 6.20 | 5.97 | 5.65 | **6.05** | 0.358 | 0.357 | 0.385 | 0.380 |
| 6 | **C** | Contracting | 5.43 | 5.74 | 5.71 | 5.73 | **5.65** | 0.252 | 0.283 | 0.258 | 0.259 |
| 7 | **GR** | Global reputation | 5.67 | 6.12 | 5.17 | 5.13 | **5.52** | 0.387 | 0.373 | 0.402 | 0.408 |
| 8 | **J** | Judicial | 4.12 | 4.84 | 4.29 | 3.78 | **4.26** | 0.287 | 0.307 | 0.306 | 0.302 |
| 9 | **S** | Costly sanctions | 3.77 | 3.51 | 3.21 | 3.21 | **3.42** | 0.281 | 0.293 | 0.271 | 0.274 |

**Damaging troll trades by phase** (lower = better troll-resistance; phase 1 always 0):

| Cond | 4T | 8T | 16T |
|------|-----|-----|-----|
| G | 34 | 28 | **17** |
| E | 22 | **16** | 30 |
| NR | 32 | 38 | 60 |
| S | 29 | 51 | 82 |
| C | 60 | 51 | 94 |
| M | 71 | 105 | 110 |
| GR | 38 | 70 | 202 |
| J | 84 | 130 | 193 |
| B | 136 | 284 | 395 |

**Key tension:** Low damaging-troll-trades does *not* predict high welfare. G has the best troll-resistance but mid-tier utility; M has high troll losses (110 at 16T) yet the highest welfare — because M generates so much total trade volume (~45–55 trades/round) that troll losses are absorbed.

---

## 4. PROGRESSIVE STRESS ANALYSIS

**Mechanisms that maintain or improve utility as trolls escalate:**

- **M (Mediation): IMPROVES.** Utility rises monotonically 7.17 → 7.76 → 8.05 → 8.15. The only mechanism that gets *better* under stress. Gini rises modestly (0.271 → 0.333). No breakdown observed at any troll count.
- **NR (Network rewiring): FLAT.** 6.78 → 6.83 → 6.71 → 6.72. Remarkably stable; Gini actually *falls* at 16T (0.317 → 0.298), suggesting link-severing successfully isolates trolls. **No breakdown through 16 trolls.**
- **G (Governance): FLAT, with best troll-suppression.** Utility 6.36 → 6.32 → 6.71 → 6.37; damaging troll trades *decline* with more trolls (34→28→17), indicating the oracle progressively detects and suspends predators. No breakdown.
- **C (Contracting): FLAT but suppressed.** Utility ~5.4–5.7 throughout, lowest-and-most-stable Gini (~0.25–0.28). Achieves stability by collapsing trade volume — C's trade counts are often single digits (e.g., round 39: 1 trade), so it sidesteps trolls by barely trading.

**Mechanisms that degrade:**

- **B (Baseline): SLOW DECAY.** 6.37 → 6.20 → 5.97 → 5.65. Degrades steadily; damaging troll trades explode (136→284→395) because agents have no tool to avoid trolls. Breaks down gradually, not catastrophically.
- **GR (Global reputation): DEGRADES at 8T.** 5.67 → 6.12 → 5.17 → 5.13. Holds at 4 trolls but breaks at 8; damaging trades jump 70→202 at 16T. Per-round data shows **catastrophic individual rounds** (round 181 AvgUtil 0.00, round 144 Gini 0.628, round 175 AvgUtil 0.33) — GR concentrates wealth and produces collapse-like rounds. **Breakdown point: 8 trolls.**

**Mechanisms that are structurally weak from the start:**

- **J (Judicial): WEAK THROUGHOUT, worst at 16T.** 4.12 → 4.84 → 4.29 → 3.78. Complaint-driven enforcement imposes filing costs and never deters fast-cycling trolls; damaging trades rise 84→130→193. **Already broken at baseline; deteriorates further.**
- **S (Costly sanctions): WORST OVERALL.** 3.77 → 3.51 → 3.21 → 3.21. Costly peer punishment drains the cooperative majority's utility. Per-round AvgUtil frequently goes **negative** (round 30: −1.17, round 61: −1.11, round 146: −0.44). **Broken from phase 1** — trolls aren't deterred and honest agents impoverish themselves sanctioning.

**Summary breakdown thresholds:** M/NR/G/C never break through 16T; B and GR degrade (GR sharply at 8T); J and S are dysfunctional from 0 trolls.

---

## 5. MECHANISM-SPECIFIC FINDINGS

**B — Baseline (no mechanisms)** | Overall 6.05
- *Worked:* Surprisingly resilient — beats GR, C, J, S. With only private experience, agents avoid known defectors via last-5-rounds memory.
- *Failed:* No tool to avoid *new* trolls; damaging troll trades highest of all conditions (395 at 16T). Highest Gini among enforcement-free conditions (~0.36–0.38).
- *Degradation onset:* Gradual from phase 2; never catastrophic. *Failure mode:* slow welfare bleed via repeated troll victimization.

**GR — Global Reputation** | Overall 5.52
- *Worked:* Helped at 4 trolls (utility rose to 6.12).
- *Failed:* Underperformed even baseline overall. *Degradation onset: 8 trolls* (5.17). Produces extreme inequality (Gini 0.408 at 16T) and collapse rounds (AvgUtil 0.00 at round 181).
- *Failure mode:* System scores let agents pile onto a few high-reputation partners, concentrating wealth and creating fragility; trolls game the scoring before detection propagates.

**C — Contracting** | Overall 5.65
- *Worked:* Best inequality control (Gini ~0.25), fully stable across phases (5.43→5.74→5.71→5.73). Breach penalty (6) deters defection effectively — defection counts stay low.
- *Failed:* Suppressed trade volume kills welfare upside; round 1 AvgUtil 0.39 from over-cautious contracting.
- *Failure mode:* Not a failure under trolls but an *opportunity cost* — safety at the price of throughput.

**M — Mediation** | Overall 7.78 (BEST)
- *Worked:* Everything. Utility *increased* with troll pressure; sustained high trade volume (~45–55/round). Free delegation to an agent-designed mediator absorbs troll losses.
- *Failed:* Damaging troll trades are high in absolute terms (110 at 16T) but immaterial relative to volume. Gini drifts up (0.333) but stays moderate.
- *Failure mode:* None observed; the mechanism's reliance on a trusted mediator is an untested single point of failure.

**G — Governance (oracle)** | Overall 6.44
- *Worked:* Best troll-*suppression* (damaging trades fall 34→17 as trolls increase). Stable utility and low Gini.
- *Failed:* Some harsh low-utility rounds at transition (round 51 AvgUtil 2.00 as oracle escalates).
- *Failure mode:* None major; oracle detection (>40% defection / predatory targeting) is an idealized assumption.

**NR — Network Rewiring + Local Reputation** | Overall 6.76
- *Worked:* Flat utility, *declining* Gini under stress (0.298 at 16T). Link-severing structurally quarantines trolls without system-wide scores.
- *Failed:* Transition spikes (round 51 defections jump to 52, round 151 to 85) before rewiring stabilizes.
- *Failure mode:* Brief vulnerability window at each new troll injection before gossip/severing catches up.

**S — Costly Sanctions** | Overall 3.42 (WORST)
- *Worked:* Low Gini (~0.27–0.28) — punishment is egalitarian, but egalitarian *poverty*.
- *Failed:* Catastrophically. Honest agents spend utility to punish; net welfare collapses, going negative in many rounds.
- *Failure mode:* The 1-for-3 cost ratio still drains the cooperative majority faster than it deters trolls (who don't value utility the way honest agents model).

**J — Judicial (complaint court)** | Overall 4.26
- *Worked:* Modest Gini control (~0.30).
- *Failed:* Second-worst utility. Filing fees + slow complaint cycle never keep pace with troll defection rate (damaging trades 193 at 16T). Negative AvgUtil rounds (round 128: −0.56, round 193: −0.67).
- *Failure mode:* Reactive, victim-initiated enforcement is too slow and too costly against high-frequency adversaries.

**E — Escrow** | Overall 6.91 (2nd)
- *Worked:* High welfare, high trade volume (~30–45/round), compensation buffers victims (4/defection).
- *Failed:* Gini rises steadily (0.285→0.369) — the worst inequality trend among top performers. **Tail risk:** pool-collapse clause (→0 reset for ALL agents) is a systemic landmine; low late-round AvgUtil (round 169: 1.50) suggests near-depletion stress. **(Inference — collapse not confirmed in data.)**
- *Failure mode:* Latent catastrophic — a single pool exhaustion wipes everyone, untriggered (apparently) in this run but structurally present.

---

## 6. BEHAVIORAL INSIGHTS (from CoT traces)

**(a) Reaction when trolls first appear — Phase 2 transition.**
The provided traces are sampled from rounds 1–2 (pre-troll), so direct phase-2-transition reasoning is not in the sample. However, the *per-round data* documents the behavioral signature: in **B at round 51** (first troll injection), defections spike from ~17 (round 50) to **33**, and trades jump to 50 — agents had not yet learned to avoid the silently-injected trolls and propose into them. In **NR at round 51**, defections jump to **52** then collapse back to 24 by round 52 — consistent with rapid link-severing once trolls are experienced. In **G at round 51**, AvgUtil drops to **2.00** as the oracle escalates fines, a visible enforcement cost at onset.

**(b) Strategic use of mechanisms to counter adversaries.**
Agents demonstrably reason about mechanisms even pre-troll. In **G, Round 2, Agent 0**: *"I'm currently UNDER REVIEW by the regulator due to high defection rate (D1 signal). I need 2 consecutive clean rounds (zero defections) to clear the warning. If I defect again, I'll face fines."* — the oracle threat directly shapes cooperative intent. In **E, Round 1, Agent 1**: *"the insurance pool exists, defecting carries a systemic risk: each defection drains the pool by 4 utility, and if [it collapses]..."* — the agent internalizes the systemic externality. In **GR, Round 1, Agent 0**: *"Since reputation system is active, defec[ting]"* is reasoned against early — transparency creates anticipatory deterrence.

**(c) Behavior under maximum pressure (16 trolls) — and opportunism.**
The most revealing traces show agents *defecting strategically* when the mechanism permits. In **E, Round 2, Agent 1**: *"In Round 1, I defected on multiple trades (against Agents 9, 10, 11, 12, 15) — I took their goods without delivering my A. This gave me a high utility gain (13) but drained the insurance pool significantly. The pool is now at 56/100, and I contributed 5 of the 11 defections so far."* — a non-troll agent free-riding on the escrow buffer, illustrating exactly the inequality-growth (Gini 0.285→0.369) and pool-collapse risk identified in §5. Similarly in **S, Round 2, Agent 1**: *"I defected on multiple trades in Round 1... I gained goods for free but likely damaged my reputation with those specific partners."* — under costly sanctions, honest agents still defect opportunistically, then both parties bleed utility, explaining S's negative AvgUtil rounds.

**(Caveat: all traces are single-run, rounds 1–2 dominant in the sample; phase-4 reasoning is inferred from per-round metrics, not directly quoted.)**

---

## 7. IMPLICATIONS & NEXT STEPS

**Promising for real-world multi-agent design:**
1. **Mediation (M)** — the standout. Structural facilitation that *grows* welfare under adversarial load. Worth prioritizing, but its single-point-of-failure (the mediator) must be stress-tested (corrupt/compromised mediator, mediator overload).
2. **Network rewiring + local reputation (NR)** — decentralized, no oracle, declining inequality under stress. Most realistic for systems where no trusted central authority exists.
3. **Governance (G)** — best troll-suppression *if* a reliable oracle is achievable; in practice the >40%-detection assumption is the weak link.

**Cautionary findings:**
- **Avoid costly peer sanctions (S) and complaint-driven courts (J)** as primary mechanisms — both underperform doing nothing. The cost of enforcement falls on cooperators.
- **Escrow (E) is high-reward but carries catastrophic tail risk** — the all-agent-reset clause should be redesigned (graduated penalties, ring-fenced contributions) before deployment.
- **Global reputation (GR) is fragile** — it concentrates wealth and produces collapse rounds at ≥8 trolls. Transparency ≠ robustness.

**Next steps (in priority order):**
1. **Replicate every cell (≥5–10 seeds).** All findings here are n=1; the round-to-round variance is large enough that mid-table rankings (B/C/GR, even NR/G) could reorder. This is the single most important next step.
2. **Recover the `mean_utility` distribution** (currently null) to compute confidence intervals and test whether M's monotonic rise survives noise.
3. **Push troll fraction beyond 16/18 and test absolute breaking points** for M, NR, and G (none broke at 16).
4. **Deliberately trigger escrow pool collapse** to quantify the tail risk that the current run apparently avoided.
5. **Cross-model replication** — DeepSeek-V3's specific reasoning style (e.g., heavy explicit cost-benefit on pool drainage) may not transfer; test on other models.
6. **Test mechanism combinations** (e.g., M + NR, or G + E) — the best structural facilitator plus the best decentralized quarantine may be complementary.
7. **Adversarial mechanism-gaming:** trolls here are simple (defect-always). Test trolls that strategically exploit each mechanism (reputation-farming, mediator-capture, complaint-flooding) to probe true robustness.

**Bottom line for designers:** Favor mechanisms that *facilitate and absorb* (mediation, rewiring) over mechanisms that *punish* (sanctions, courts), and treat any mechanism with a systemic-reset failure mode (escrow) as a latent hazard — but validate all of this with replication before acting on it.