# Analyst Report

Generated: 2026-06-10T06:38:15.509265
Models: .ipynb_checkpoints, deepseek-v3, gpt-5.4-mini, gpt-5.4-nano
Troll mode: progressive, 0, 2, 4

## Data Availability

  .ipynb_checkpoints @ 0 trolls: B (1/9 conditions)
  deepseek-v3 @ progressive (0→4→8→16 trolls): B, GR, C, M, G, NR, S, J, E (9/9 conditions)
  deepseek-v3 @ 0 trolls: B (1/9 conditions)
  deepseek-v3 @ 2 trolls: B, NR (2/9 conditions)
  deepseek-v3 @ 4 trolls: B, GR, C, M, G, NR, S (7/9 conditions)
  gpt-5.4-mini @ 2 trolls: NR (1/9 conditions)
  gpt-5.4-mini @ 4 trolls: B, GR, C, M, G, NR, S (7/9 conditions)
  gpt-5.4-nano @ 2 trolls: B, GR, C, M, G, NR, S (7/9 conditions)
  gpt-5.4-nano @ 4 trolls: B, GR, C, M, G, NR, S (7/9 conditions)

---

# Institutional Mechanisms for Sustaining Cooperation Under Progressive Adversarial Stress
## A Research Analysis Report

---

## 1. EXECUTIVE SUMMARY

The single most important finding is that **structural cooperation support (mediation, escrow) and information-based defenses (network rewiring) sustained the highest non-troll welfare under escalating troll pressure in the deepseek-v3 progressive runs, while punitive peer-enforcement mechanisms (costly sanctions, judicial complaints) actively destroyed welfare**. In the progressive condition, mediation (M) achieved the highest overall mean utility (7.78) and *increased* utility across phases (7.17 → 8.15), whereas costly sanctions (S) collapsed to the bottom (overall 3.42, declining 3.77 → 3.21). Critically, **mechanism robustness was not primarily about suppressing troll damage — it was about not damaging cooperative agents in the process**: governance (G) and escrow (E) suppressed damaging troll trades most effectively (G fell to just 17 damaging trades at 16 trolls vs. baseline's 395), yet S and J permitted heavy losses *and* imposed self-inflicted costs. **A central caveat dominates this entire report: every progressive result rests on a single run per condition for one model (deepseek-v3), with no replication, no confidence intervals, and severe data gaps for the GPT models.** The cross-model fixed-troll snapshots reveal that mechanism rankings do **not** transfer across models — gpt-5.4-mini and gpt-5.4-nano operated at drastically lower absolute utility (often near zero or negative), suggesting findings are highly model-dependent and should not be generalized.

---

## 2. DATA COVERAGE

### What exists
| Model | Trolls | Conditions | Replication |
|---|---|---|---|
| deepseek-v3 | progressive (0→4→8→16) | All 9 (B, GR, C, M, G, NR, S, J, E) | **1 run each** |
| deepseek-v3 | 0 (fixed) | B only | 1 run |
| deepseek-v3 | 2 (fixed) | B, NR | 1 run each |
| deepseek-v3 | 4 (fixed) | B, GR, C, M, G, NR, S (7/9) | 1 run each |
| gpt-5.4-mini | 2 (fixed) | NR only | 1 run |
| gpt-5.4-mini | 4 (fixed) | B, GR, C, M, G, NR, S (7/9) | 1 run each |
| gpt-5.4-nano | 2 (fixed) | B, GR, C, M, G, NR, S (7/9) | 1 run each |
| gpt-5.4-nano | 4 (fixed) | B, GR, C, M, G, NR, S (7/9) | 1 run each |
| .ipynb_checkpoints | 0 | B only (artifact directory) | 1 run |

### What is missing (critical gaps)
- **No replication anywhere.** Every single cell is n=1. No mechanism claim can be stated with statistical confidence.
- **The progressive design exists ONLY for deepseek-v3.** All cross-phase degradation analysis (Sections 3, 4, 5) is single-model, single-run.
- **J (judicial) and E (escrow) have NO fixed-troll data and NO GPT data.** They exist only in the deepseek-v3 progressive run.
- **GPT models never ran progressive, J, or E**, and gpt-5.4-mini lacks fixed-troll B at 2 trolls (only NR).
- **Per-round tables for fixed-troll runs cover only 30 rounds**; progressive tables cover all 200.
- `.ipynb_checkpoints` is a checkpoint artifact, not a distinct model — disregard.
- Several `gini.mean` fields are `null` (e.g., deepseek progressive overall, NR at 2 trolls), and `mean_utility.mean` is `null` throughout the progressive phases — we rely on `non_troll_mean_utility` per phase.

**Every numeric conclusion below is flagged as single-run.** Treat all rankings as hypotheses, not established results.

---

## 3. MECHANISM RANKING (deepseek-v3 progressive, single run)

Ranked by overall non-troll mean utility, with per-phase non-troll utility and mean Gini. **All values single-run.**

| Rank | Cond | Overall Util | Util 0T | Util 4T | Util 8T | Util 16T | Gini 0T | Gini 4T | Gini 8T | Gini 16T | Damaging trades (0/4/8/16T) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **M** (mediation) | 7.78 | 7.17 | 7.76 | 8.05 | 8.15 | 0.271 | 0.300 | 0.329 | 0.333 | 0 / 71 / 105 / 110 |
| 2 | **E** (escrow) | 6.91 | 7.29 | 6.84 | 6.88 | 6.64 | 0.285 | 0.312 | 0.348 | 0.369 | 0 / 22 / 16 / 30 |
| 3 | **NR** (network rewiring) | 6.76 | 6.78 | 6.83 | 6.71 | 6.72 | 0.317 | 0.313 | 0.316 | 0.298 | 0 / 32 / 38 / 60 |
| 4 | **G** (governance) | 6.44 | 6.36 | 6.32 | 6.71 | 6.37 | 0.284 | 0.284 | 0.273 | 0.286 | 0 / 34 / 28 / 17 |
| 5 | **B** (baseline) | 6.05 | 6.37 | 6.20 | 5.97 | 5.65 | 0.358 | 0.357 | 0.385 | 0.380 | 0 / 136 / 284 / 395 |
| 6 | **C** (contracting) | 5.65 | 5.43 | 5.74 | 5.71 | 5.73 | 0.252 | 0.283 | 0.258 | 0.259 | 0 / 60 / 51 / 94 |
| 7 | **GR** (global reputation) | 5.52 | 5.67 | 6.12 | 5.17 | 5.13 | 0.387 | 0.373 | 0.402 | 0.408 | 0 / 38 / 70 / 202 |
| 8 | **J** (judicial) | 4.26 | 4.12 | 4.84 | 4.29 | 3.78 | 0.287 | 0.307 | 0.306 | 0.302 | 0 / 84 / 130 / 193 |
| 9 | **S** (costly sanctions) | 3.42 | 3.77 | 3.51 | 3.21 | 3.21 | 0.281 | 0.293 | 0.271 | 0.274 | 0 / 29 / 51 / 82 |

**Key observations from the table:**
- **M is the only mechanism whose utility rose monotonically** under escalating trolls (7.17 → 8.15). This is striking and warrants replication scrutiny — it may be an artifact.
- **C achieves the lowest inequality** (Gini ≈ 0.25–0.28 throughout) but at a mediocre utility level (~5.65).
- **G is the best at suppressing troll damage** — damaging trades *fell* as trolls rose (34 → 28 → 17), the only mechanism showing this counterintuitive pattern, consistent with its escalating-suspension design.
- **GR is the worst information mechanism** — damaging trades exploded 38 → 202 and utility fell 6.12 → 5.13. System-computed scores appear to have provided little protection against silently-injected trolls.
- **B (baseline) suffered the most raw troll damage** (395 damaging trades at 16T) but still outperformed S, J, GR, and C on utility — punitive mechanisms underperformed *doing nothing*.

---

## 4. PROGRESSIVE STRESS ANALYSIS

(All deepseek-v3, single run. Phases: 0T = rounds 1–50, 4T = 51–100, 8T = 101–150, 16T = 151–200.)

### Mechanisms that MAINTAINED utility
- **M (mediation):** 7.17 → 7.76 → 8.05 → 8.15. No degradation; utility *increased*. Gini drifted up modestly (0.271 → 0.333). **No breakdown point observed.** This is the standout — but the single-run, single-model caveat is acute, especially given M's catastrophic failure in fixed-troll runs (see below).
- **E (escrow):** 7.29 → 6.84 → 6.88 → 6.64. Mild monotonic decline (~9% total), but Gini rose notably (0.285 → 0.369), indicating welfare was maintained on average but distributed less equally as the pool absorbed shocks. **No catastrophic collapse — the pool never reset to 0 in this run** (utility never floored at 0 across the table). Robust but fragile-by-design.
- **NR (network rewiring):** 6.78 → 6.83 → 6.71 → 6.72. Remarkably *flat* — essentially no degradation across all four phases, and Gini even improved at 16T (0.298). Damaging trades grew only modestly (32 → 60). **Best stability-to-simplicity ratio.**
- **G (governance):** 6.36 → 6.32 → 6.71 → 6.37. Flat with a mid-game bump; damaging trades *declined* to 17. **No breakdown.**

### Mechanisms that DEGRADED
- **B (baseline):** 6.37 → 6.20 → 5.97 → 5.65. Steady ~11% erosion, with damaging trades scaling almost linearly with troll count (136 → 284 → 395). Degradation begins immediately at phase 2 (4 trolls).
- **GR (global reputation):** 6.12 → 5.17 → 5.13. **Breakdown at phase 3 (8 trolls)** — utility dropped sharply between 4T and 8T (6.12 → 5.17), and damaging trades surged 70 → 202 by 16T. Inequality is the worst of any mechanism (Gini 0.408 at 16T). The per-round table shows extreme volatility late (e.g., round 181 AvgUtil 0.00, Gini 0.685).
- **J (judicial):** 4.84 → 4.29 → 3.78. **Breakdown after phase 2.** Complaint-driven enforcement failed to scale: damaging trades climbed 84 → 130 → 193, and the filing costs/penalties appear to have suppressed welfare without deterring trolls.
- **S (costly sanctions):** 3.77 → 3.51 → 3.21 → 3.21. **Began degraded from phase 1** (lowest 0T utility of any mechanism at 3.77) — the mechanism itself depressed welfare even with zero trolls, because the spend-1-to-cost-3 punishment is net-negative for the system. Per-round AvgUtil frequently went negative (round 30: −1.17; round 61: −1.11; round 146: −0.44).

### Summary of breakdown points
| Mechanism | Degrades at | Failure character |
|---|---|---|
| M | never (this run) | none observed |
| NR | never (essentially flat) | none observed |
| G | never | none observed |
| E | gradual from 4T | rising inequality |
| B | 4T onward | linear troll damage |
| C | stable but low | self-suppressed volume |
| GR | **8T (sharp)** | reputation gaming/inequality |
| J | 4T onward | enforcement doesn't scale |
| S | **from 0T** | self-inflicted welfare loss |

---

## 5. MECHANISM-SPECIFIC FINDINGS

### B — Baseline (no mechanisms)
- **Worked:** Surprisingly resilient on utility (overall 6.05), outperforming four enforcement/reputation mechanisms. Pure repeated-interaction trust held up moderately.
- **Failed:** Absorbed by far the most troll damage (395 damaging trades at 16T). High inequality (Gini ~0.36–0.38).
- **Degradation:** Immediate at 4T; steady to 16T.
- **Failure mode:** No defense — trolls simply harvest cooperative agents who keep proposing trades. Damaging trades scale ~linearly with troll count.

### GR — Global Reputation
- **Worked:** Brief benefit at 4 trolls (utility 6.12, the only phase it beat baseline).
- **Failed:** Collapsed at 8T+. Worst inequality of all conditions (Gini 0.408 at 16T). Damaging trades surged to 202.
- **Degradation:** Sharp at phase 3 (8 trolls).
- **Failure mode:** System-computed scores didn't capture silently-injected trolls fast enough, and the public scores appear to have enabled a winner-take-all dynamic (high Gini, volatile per-round utility crashing to 0.00 at round 181). **Single-run — the late-game volatility could be one bad trajectory.**

### C — Contracting (6-utility breach penalty)
- **Worked:** Lowest, most stable inequality (Gini ~0.25–0.28 throughout). Effectively deterred breach — defection counts and trade *volume* both stayed very low (many rounds <10 trades).
- **Failed:** Suppressed trade volume so much that aggregate welfare stayed mediocre (5.65). The deterrent worked by making agents trade less, not more safely.
- **Degradation:** No collapse, but no growth either — flat at a low level.
- **Failure mode:** Over-deterrence / chilling effect on trade volume.

### M — Mediation (agent-designed mediator, free delegation)
- **Worked (progressive):** Best overall (7.78), monotonically increasing, supporting the highest trade volumes (40–60/round). The free mediator appears to have brokered safe high-volume exchange.
- **Failed (FIXED 4-troll, deepseek):** **Catastrophic — mean utility −1.22, Gini 0.626.** The per-round table shows utility at −5.00 (round 1) climbing slowly out of a deep hole, with Gini up to 0.944 (round 2).
- **Degradation:** In progressive: none. In fixed-4T: total collapse from round 1.
- **Failure mode:** **This is the report's most important contradiction.** M was the *best* in progressive and the *worst* in fixed-4-troll. The likely explanation: in progressive, agents built mediation habits during the 50-round troll-free phase before trolls arrived; in fixed runs, trolls were present from round 1 and poisoned the mediator/delegation channel immediately. **This is a single-run-per-condition result and must be replicated — but if real, it implies mediation's robustness depends entirely on a cooperation-establishment grace period.**

### G — Governance (oracle, defection >40% & predatory-targeting detection)
- **Worked:** Best troll suppression (damaging trades fell 34 → 28 → 17 as trolls rose). Flat utility (~6.4), low Gini (~0.28). The escalating fine/suspension regime visibly deterred — CoT traces show agents tracking "UNDER REVIEW" status.
- **Failed:** Generated nonsensical accusation behavior in fixed runs (false_accusation_rate = 1.0 in fixed-4T deepseek), suggesting the oracle interface confused agents.
- **Degradation:** None observed in progressive.
- **Failure mode:** Oracle dependence — requires a trustworthy central detector, which is itself a strong assumption.

### NR — Network Rewiring + Local Reputation
- **Worked:** Flattest utility curve of any mechanism (6.78 → 6.72), *improving* Gini at max pressure (0.298 at 16T), low damaging trades. In fixed-4T deepseek it had the **lowest avg_damaging_last_half (0.13)** of all mechanisms — agents successfully severed links to trolls. High whistleblowing (0.456 mean in fixed-4T).
- **Failed:** Did not transfer to GPT models — gpt-5.4-mini NR at 2 trolls scored just 1.47 mean utility.
- **Degradation:** None in deepseek progressive.
- **Failure mode:** Model-dependent; relies on agents actually using sever/gossip capabilities (which gpt-mini did poorly).

### S — Costly Sanctions
- **Worked:** Kept Gini moderate (~0.27–0.29).
- **Failed:** **Worst utility overall (3.42), degraded from phase 1.** The spend-1→target-loses-3 mechanism is net-destructive; agents burned utility on (often misdirected) punishment. Frequent negative per-round AvgUtil.
- **Degradation:** From the very start (0T utility 3.77, already lowest).
- **Failure mode:** Self-inflicted welfare destruction; anonymous sanctions invited misuse and retaliation spirals.

### J — Judicial (complaint-driven, fine 5 / comp 3 / filing fee 1 / false-complaint fine 2)
- **Worked:** Modest benefit at 4T (4.84, its peak).
- **Failed:** Second-worst overall (4.26), degrading after phase 2 with damaging trades climbing to 193.
- **Degradation:** Phase 3 onward.
- **Failure mode:** Complaint enforcement didn't scale — filing friction (fee + false-complaint risk) deterred legitimate complaints faster than it deterred trolls. **Only one run; no fixed-troll or GPT comparison exists for J.**

### E — Escrow (pool=100, pays 4/victim, collapse→reset all to 0)
- **Worked:** Second-best overall (6.91); the insurance pool successfully compensated victims and the catastrophic reset **never triggered** in this run (utility never floored).
- **Failed:** Rising inequality (Gini 0.285 → 0.369) as the pool absorbed asymmetric shocks.
- **Degradation:** Gradual from 4T.
- **Failure mode:** Tail risk — the design contains a system-wide reset that did not fire here but represents a latent catastrophic failure mode. **One run cannot characterize the probability of pool collapse — this is the single most under-tested risk in the study.**

---

## 6. BEHAVIORAL INSIGHTS (from CoT traces)

### (a) How agents react when trolls first appear (phase 2 transition, ~round 51)
The traces provided are mostly Rounds 1–2, so direct phase-2-transition reasoning is limited, but the **discovery-through-experience** dynamic is visible. In deepseek-v3 / B (2 trolls), Round 2, Agent 0 already adapts to a fresh defection:
> *"Agent 19 defected on me: they offered 2B for 2A, I accepted, they took my 2A and gave nothing. So I lost 2A to defection... Agent 19 [is untrustworthy]."* — deepseek-v3 / B (2 trolls), Round 2, Agent 0.

This shows the intended mechanism: trolls are not announced, so agents build local blacklists from experience. In deepseek-v3 / NR (2 trolls), Round 2, Agent 2 demonstrates the rewiring response forming:
> *"Agent 6 defected twice... Agent 7 defected once... So Agents 6 and 7 are defectors against me."* — deepseek-v3 / NR (2 trolls), Round 2, Agent 2.

This local-reputation accumulation is exactly the behavior that produced NR's low damaging-trade counts.

### (b) Whether agents use mechanisms strategically to counter trolls
**Governance (G):** Agents explicitly reason about regulator status and adjust:
> *"I am UNDER REVIEW by the regulator due to a high defection rate (D1 signal). I need 2 consecutive clean rounds (zero defections) to clear the warning. If I defect again, I'll face fines."* — deepseek-v3 / G (progressive), Round 2, Agent 0.

This is genuine strategic use of the mechanism — the deterrent is internalized, consistent with G's declining damaging-trade counts.

**Escrow (E):** Agents reason about systemic pool risk — and some exploit it:
> *"I defected on multiple trades in Round 1 (against Agents 9, 10, 11, 12, 15)... This gave me a high utility gain (13) but drained the insurance pool significantly. The pool is now at 56/100, and I contributed 5 of the 11 defections."* — deepseek-v3 / E (progressive), Round 2, Agent 1.

This is alarming: a non-troll agent recognizes it can free-ride on the insurance pool, accelerating it toward the catastrophic reset. The mechanism's collective-punishment design creates a tragedy-of-the-commons incentive **even among cooperative agents** — a latent failure mode not captured by the single run's average utility.

**Contracting (C):** Agents weigh the breach penalty explicitly:
> *"The contract proposed by Agent 11: I deliver 1 A, they deliver 1 B, breach penalty..."* — deepseek-v3 / C (4 trolls), Round 2, Agent 1.

The penalty is salient in reasoning, explaining C's low breach/defection and low volume.

### (c) Behavior under maximum pressure — and the M contradiction
The most revealing trace is the **fixed-4-troll mediation collapse**, which explains M's −1.22 utility:
> *"Last round utility was −5 (likely from producing 5 units of Good A at cost of 1 each, totaling −5, with no consumption gains)... I rejected all trade offers last round (from Agents 9, 10, 15, 16)."* — deepseek-v3 / M (4 trolls), Round 2, Agent 0.

Here, with trolls present from round 1, agents produced but **refused to trade** through a poisoned mediation channel, generating only production costs and no consumption gains — the −5.00 per-round floor visible in the table. Contrast with progressive M, where the 50-round troll-free runway let cooperative mediation habits stabilize before trolls arrived. **This single comparison (n=1 each) is the strongest behavioral evidence that grace periods matter — and the strongest reason to demand replication.**

Under sanctions (S), even cooperative agents disclose opportunistic defection under pressure:
> *"I defected on Agent 15 and Agent 16 when they offered A for C (I took their C without giving A). Agent 10 defected on me when I offered A for B."* — deepseek-v3 / S (progressive), Round 2, Agent 1.

The mutual defection + costly retaliation dynamic explains S's persistent negative per-round utility.

---

## 7. IMPLICATIONS & NEXT STEPS

### What the data suggests (all hypotheses, given n=1)
1. **Punishment ≠ protection.** S and J — the two purest peer-punishment mechanisms — were the *worst* performers, both worse than doing nothing (B). Net-negative sanction technology and complaint friction destroyed welfare without scaling deterrence. **Real-world systems should not assume that adding punishment improves cooperation.**
2. **Damage suppression and welfare are different objectives.** G suppressed troll damage best (17 trades at 16T) but only matched baseline on welfare; M permitted moderate troll damage (110) but delivered the highest welfare. Designers must specify which they optimize.
3. **Lightweight, decentralized defenses (NR) were the most robust per unit of complexity** — flat utility, improving equality, no oracle required. This is the most promising candidate for real multi-agent deployment.
4. **Grace periods may be decisive.** The M progressive-v