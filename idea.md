# Idea Dump

> These are exploratory ideas and notes — not committed to implementation.
> Last updated: 2026-05-28

---

## Current Setup Summary

- **18 LLM agents**, 6 per good (A, B, C), all CoT reasoning
- **Models**: GPT-5.4-mini (Azure, default) and DeepSeek-V3.2 (Azure) — `--model` flag switches between them. Each model logs to its own folder (`data/runs/gpt-5.4-mini/`, `data/runs/deepseek-v3/`). Cross-model comparison plot implemented.
- **Barter economy**: no tokens, goods-for-goods trade, cost 1 utility to produce, 3 utility per consumed unit, 20% spoilage
- **Phase 1**: 30 rounds, 3 runs per condition. **Phase 2**: 100 rounds, 1 run, with `--trolls N` and `--rounds N` CLI flags
- **Two-tier trade history**: lifetime partner summary (all rounds, never forgotten) + recent detail window (last 5 rounds). Agents see "Agent 5: 12 trades, 12/12 defections by them (100%)" — prevents trolls being "forgiven" when evidence scrolls out of the detail window.
- **Self-interest framing**: explicit prompt language ("Your only goal is to maximise your own total utility") counteracting RLHF cooperative prior
- **5 core metrics** — see "Metrics Provenance" and "Gini Coefficient" sections below:
  - Production Stability (our construct), Cooperation Rate (our construct), Gini coefficient (citeable), Per-round mean utility, Rawlsian min utility
- **Cooperation threshold**: both Production Stability and Cooperation Rate > 0.5

### Implemented Mechanisms (8 conditions)

| Code | Mechanism | Type | Status | Description |
|------|-----------|------|--------|-------------|
| B | Baseline | — | Implemented | No mechanism. Pure self-interest dynamics |
| R | Reputation | Agent-participatory | Implemented | System-tracked reputation (exponential decay: 0.9 * old + 0.1 * observation), visible to agents, initial = 1.0 |
| C | Contracting | Agent-participatory | Implemented | Formal binding contracts: propose → sign/reject → enforce. Breach penalty = 6 utility |
| M | Mediation | Agent-participatory | Implemented | Democratic: agents propose mediator rules, vote, then delegate trades. Fee = 1 utility |
| G | Governance | External-deterministic | Implemented | Oracle detects defection patterns (4 signals, 5-round window) → escalates: Active → Warning → Fined → Suspended. See "Governance Signal Validity" section for D2/D3 concerns |
| NR | Network Rewiring + Reputation | Agent-participatory | Implemented | Agents sever/request links + system reputation score. Adapted from RepuNet (arXiv:2505.05029). Full isolation allowed |
| S | Sanctions | Agent-participatory | Implemented | Costly punishment: spend 1 utility → target loses 3. Anonymous, public announcement. Based on Piedrahita et al. 2025 |

Full factorial combinations (RC, RM, etc.) disabled until initial results reviewed.

### Troll Agents (Phase 2) — IMPLEMENTED

- **Deterministic**: no LLM calls, zero cost per round
- **Does NOT produce**: 0 production every round (pure parasite)
- **Defects on ALL incoming trades**: takes proposer's goods, delivers nothing
- **Lies in messages**: sends public messages claiming fair cooperation ("I'm committed to fair trading!"). Tests whether agents learn to weigh actions over words
- **Passive**: does NOT propose trades — can only defect on offers sent TO them. If no agents propose trades to a troll, the troll's defection count drops to zero
- **Fully connected**: trolls are connected to ALL other agents in the network (maximally exposed — every non-troll can encounter them)
- **Round-robin distribution**: 2 trolls = agents 0 (Good A) + 6 (Good B); 4 = 0, 6, 12, 1; 6 = 0, 6, 12, 1, 7, 13
- **Excluded from metrics**: trolls are excluded from sustainability (production), peace (trade defection rate), utility averages, and distribution plots. Only non-troll-to-non-troll trades count. This prevents troll behavior from skewing aggregate metrics — we measure how well the remaining agents cooperate despite the trolls, not the trolls' own performance.
- **CLI**: `--trolls N` flag, `--rounds N` for longer games
- **File naming**: `{condition}_t{n_trolls}_run_{idx:02d}.json`

---

## Governance Signal Validity — D2 and D3 (OPEN QUESTION)

**Issue**: D1 and D4 are clearly defection-based signals grounded in the governance literature. D2 (production withdrawal) and D3 (trade volume collapse) were added without a specific paper citation. They may penalise agents unfairly.

**D3 specific problem**: An agent can trigger D3 (fewer than 2 completed trades in 5 rounds) even if it's not their fault — e.g. their neighbors are refusing to trade with them. The oracle punishes the victim, not the defector.

**Options to consider:**

| Option | What changes | Risk |
|---|---|---|
| Remove D2 and D3 entirely | Only keep D1 (defection rate) and D4 (predatory targeting) | G becomes purely defection-reactive; production/participation collapse goes undetected |
| Keep D2, remove D3 | Production withdrawal is a plausible signal; trade volume is too noisy | Partial fix |
| Fix D3 to be proposer-side only | Only count trades *proposed by the agent* that collapsed | More defensible but harder to implement |
| Cite a paper for D2/D3 | Find a governance/market regulation framework that justifies monitoring production and trade volume | Preferred if a citation exists |

**Decision needed**: Keep, fix, or remove D2/D3?

---

## Network Rewiring + Reputation (NR) — Design Notes

**Based on**: RepuNet (arXiv:2505.05029, May 2025, AAMAS 2026) — Siyue Ren et al.

RepuNet uses network rewiring **with** reputation — the paper's mechanism is inherently a combined approach. We implement this as condition NR (not N alone), matching the literature.

**RepuNet key results** (for reference):
- Public goods game: cooperation 0.19 → 0.85 (4.5x improvement)
- Trust game: cooperation 0.17 → 0.98 (5.8x improvement)
- Ablation: removing gossip barely hurts (0.85→0.81); removing reputation collapses everything (0.85→0.29)

**Our NR implementation** (simplified from RepuNet):
- Sparse starting graph (4-6 neighbors per agent, cross-good guarantees)
- Each round: agents can **sever** links (max 1/round) and **request** new links (max 2/round, auto-accepted if target has capacity)
- Full isolation allowed (no minimum neighbor floor)
- System reputation score visible to all agents (same as R mechanism)
- Network evolves over rounds — defectors lose partners, cooperators gain them

**What NR tests vs R alone**: R gives agents information (public reputation score) but no structural power (fixed network). NR gives agents BOTH — the public score AND the ability to act on it by severing/requesting links. Does adding structural power to information improve outcomes?

---

## Candidate Mechanisms NOT Implemented

### Taxation / Redistribution (T)
- **Paper**: Zheng et al. 2022, "The AI Economist" (Science Advances); "LLM Economist" (arXiv:2507.15815, 2025)
- **Idea**: Tax a percentage of each agent's round utility, redistribute equally or to lowest-utility agents
- **Open question**: What tax rate? Does redistribution remove incentive to trade well?

### Escrow / Performance Bonds (E)
- **Paper**: "Quantifying Trust: Financial Risk for AI Agents" (ARS, arXiv:2604.03976); Blockchain+MARL (Nature Sci Reports 2025)
- **Idea**: Both parties stake collateral before a trade. If one defects, collateral goes to the victim
- **Difference from C**: Contracting is post-hoc (penalty after breach). Escrow is pre-committed

### Metanorm Enforcement
- **Paper**: "Evolution of Social Norms in LLM Agents using Natural Language" (arXiv:2409.00993, Sep 2024)
- **Idea**: Second-order punishment — punish agents who FAIL to punish defectors
- **Open question**: Very complex — may be too much cognitive load for the LLM

### Insurance / Risk Pooling (I)
- **No LLM-specific paper** — classical basis: Arrow 1963, Townsend 1994
- **Idea**: Agents pool into an insurance fund; defection victims get compensated
- **Open question**: Novel contribution opportunity but complex to implement

---

## Experimental Design: Two-Phase Resilience Study

### Research Question

Which institutional mechanisms allow a marketplace of self-interested LLM agents to sustain cooperation — and how resilient are those mechanisms to adversarial actors that cannot be incentivized?

### Key Framing

All agents are **self-interested**, not good-faith cooperators. Mechanisms work by making cooperation the **rational choice**. A "troll" is a hardcoded defector — a self-interested agent that **cannot be incentivized** to cooperate regardless of mechanism. The question is: can the mechanism sustain cooperation among the remaining rational agents even when some participants are immune to incentives?

### Phase 1: Mechanism Comparison

**Goal**: Which mechanisms make cooperation the rational choice for self-interested agents?

- All 7 conditions: B, R, C, M, G, NR, S
- 0 trolls — pure self-interest dynamics
- **3 runs** per condition, **30 rounds** each
- **Metrics**: Production Stability, Cooperation Rate, Gini, per-round mean utility, Rawlsian min utility
- **Advancement criterion**: mechanisms that keep mean utility positive AND cooperation rate > 0.5 advance to Phase 2
- **Output**: Ranked list of mechanism conditions by cooperation outcomes

### Phase 2: Adversarial Resilience

**Goal**: Take the top 3-4 mechanisms from Phase 1 and stress-test with escalating trolls.

**Why funnel, not full factorial**: If a mechanism can't even get self-interested agents to cooperate in Phase 1, there's no point testing it against trolls — it already fails. But run the top 3-4 (not just the single winner) in case rankings shift under adversarial pressure.

- **1 run** per condition, **100 rounds** each
- **Trolls**: 2, 4, 6 (out of 18 agents) — find each mechanism's **breaking point**
- **CLI**: `python -m simulation.main --condition B --trolls 2 --rounds 100 --runs 1`

**Troll design** — see "Troll Agents" section above. Key: trolls **lie in public messages** claiming cooperation while defecting on all trades. This tests whether agents learn to weigh actions over words. Trolls are passive parasites — they can only defect on offers sent TO them. If all agents stop proposing trades to a troll, its defection count drops to zero.

**Collapse definition** (decided): per-round mean utility < 0 sustained for **3+ consecutive rounds**.

**Key metric**: Per-round societal utility (NOT cumulative). Cumulative utility always increases as long as any agent cooperates — it never "dips." Per-round utility is what drops when trolls enter.

**Target result table:**

| Condition | Phase 1 Coop Rate | Phase 1 Prod Stability | Trolls to collapse |
|---|---|---|---|
| Top mechanism 1 | ? | ? | ? |
| Top mechanism 2 | ? | ? | ? |
| Top mechanism 3 | ? | ? | ? |
| Top mechanism 4 | ? | ? | ? |

**Target graph** (the paper figure):
```
plot_troll_sweep():
  X-axis: Number of trolls (0, 2, 4, 6)
  Y-axis: Final-round mean utility (averaged across runs)
  Lines:  One per condition (B, R, C, M, G, NR, S)
  Horizontal line at y=0 (collapse threshold)
  Shows: which mechanisms hold positive utility longest as trolls increase
```

**How each mechanism handles trolls (predicted):**

| Mechanism | Troll defense | Strategy type | Predicted resilience |
|---|---|---|---|
| B (baseline) | None — troll defects, victims retaliate, cascade collapse | — | Very low |
| R | Troll's reputation drops, agents see they're bad — but can't avoid them (fixed network) | Information without action | Low |
| C | Troll breaches contracts, pays utility penalties — but trust damage done | Penalty | Medium |
| M | If troll delegates to mediator, mediator forces fair execution | **Neutralization** | High |
| G | Oracle detects 100% defection rate, escalates to fines/suspension | **Ejection** | High |
| NR | Agents sever links to troll + reputation drops — coordinated isolation | **Hard isolation + information** | High |
| S | Agents spend utility to punish troll; troll loses 3× per sanction | **Costly punishment** | Medium-High |
| B/R/C/S (all fixed-network) | Agents stop *proposing* trades to known defectors | **Soft boycott** | Varies |

**Key insight**: Troll isolation happens in ALL mechanisms, not just N. The difference is the mechanism:
- **Soft boycott** (B, R, C, S): agents learn from lifetime partner summary and stop proposing trades. Slower, depends on agents processing history correctly
- **Hard isolation** (NR): agents sever network links. Structural, permanent, visible to all
- **Neutralization** (M): mediator overrides defection on delegated trades
- **Ejection** (G): oracle detects and suspends troll from market

M, NR, and G are predicted most resilient, but for fundamentally different reasons. This is a publishable finding if confirmed.

**B vs R — does public reputation add anything?** The lifetime partner summary (available in ALL conditions including B) gives agents **private first-hand knowledge**: you see defection stats only for partners you've personally traded with. R adds a **public aggregate signal**: a system-computed reputation score derived from ALL of an agent's trades across all partners. An agent who has never traded with a troll can still see its low reputation in R, but would have a blank slate in B. However, with small networks (4-6 neighbors), most agents gain direct experience with a troll within a few rounds — so R's advantage may only be a few rounds of faster detection. If experiments show B and R converge quickly, that's itself a finding: public reputation adds little when agents have long memory and small networks. It would matter more with larger networks or shorter memory windows.

**Differentiating mechanisms that all isolate trolls** — if every mechanism eventually contains trolls, the question shifts from *whether* to *how well*:

1. **Speed of detection**: how many rounds before trades proposed to trolls drop to near-zero? Faster = better. Measured as the first round where troll trade volume stays at 0 for 3+ consecutive rounds.
2. **Collateral damage**: how much utility do non-troll agents lose during the containment period? Measured as `Σ(baseline_utility_t − troll_utility_t)` summed over all rounds — the area between the 0-troll curve and the troll curve. Lower = better.

These two metrics together rank mechanisms even when all of them eventually succeed. A mechanism that isolates trolls by round 5 with minimal utility loss is strictly better than one that takes 20 rounds and tanks the economy in the process.

### Substantiating Claims (Post-Experiment Analysis)

Three levels of evidence, from weakest to strongest:

**1. Statistical significance (p-values)**
With 3 runs per condition, use Mann-Whitney U test (non-parametric, no normality assumption) to compare each mechanism vs baseline B:
```python
from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(mechanism_utilities, baseline_utilities, alternative="greater")
```
Report as a table: condition | mean final utility | p-value vs B. p < 0.05 = significant.
Note: 3 runs gives limited statistical power — sufficient for directional evidence, not for fine-grained pairwise rankings.

**2. Causal pathway evidence (mechanism of action)**
Show the mechanism worked THROUGH its intended channel:
- **R**: agents with low reputation received fewer trade proposals (information → avoidance)
- **G**: warned/fined agents reduced defection rate in subsequent rounds (deterrence → behavior change)
- **NR**: defectors' neighbor count dropped over time, cooperators' held stable (structural → isolation)
- **C**: agents with active contracts defected less than in uncontracted trades (commitment → compliance)
- **M**: mediated trades had lower defection than unmediated trades (enforcement → fair execution)
- **S**: sanctioned agents reduced defection in subsequent rounds (punishment → behavior change)
All derivable from existing logged data — no new simulation runs needed, just post-hoc analysis.

**3. Controlled adversarial test (troll sweep)**
Inject hardcoded defectors (0, 2, 4, 6 trolls) and show which mechanisms maintain positive utility. Strongest evidence: the troll is a known ground-truth defector — if G suspends it, if N isolates it, that's proof the mechanism detected and contained a real adversary.

### Open Design Questions

- **Timing**: trolls from round 1 (decided) or injected mid-game? Round-1 injection is simpler and tests steady-state resilience
- **Troll placement**: round-robin across goods (decided). Targeted placement (hub agent) could be a future extension
- **Troll awareness**: agents do NOT know trolls exist — they discover it through experience and lifetime partner summary
- **Mixed trolls**: all 100% defection rate (decided). Variable defection rates (50%, 75%) could be a future extension
- **Cross-model comparison**: run same conditions on GPT-5.4-mini and DeepSeek-V3.2. If both agree, mechanisms are robust to model choice. If they diverge, high baseline cooperation may be model-specific RLHF bias

---

## Metrics Provenance — "Sustainability" and "Peace" Are Our Own Constructs

**Issue**: The codebase currently uses metrics named "sustainability" and "peace." These names overlap with established definitions in the literature, but our formulas do not match. We cannot cite those papers for our metrics.

### What the literature defines

**Perolat et al. 2017** (used by Gallego 2026, arXiv:2603.19453 — "Cooperation and Exploitation in LLM Policy Synthesis for Sequential Social Dilemmas") defines four standard metrics for sequential social dilemmas:

| Metric | Perolat Definition | Our Definition | Compatible? |
|---|---|---|---|
| **Sustainability** | Mean timestep at which agents earn positive reward (temporal — did resources last through the episode?) | `production_t / production_round1` (ratio — are agents still producing at round-1 levels?) | **No** — theirs is temporal distribution, ours is a production ratio |
| **Peace** | Avg number of agents active per step, not tagged out by combat (gridworld-specific) | `1 - defections/trades` (fraction of trades without defection) | **No** — theirs counts agent-steps lost to combat beams, ours counts trade-level defection |
| **Equality** | `1 − Gini` over total agent rewards | Not yet implemented | — |
| **Efficiency** | Total reward per timestep | `mean_utility` per round | Closest match |

**GovSim** (Piatti et al., NeurIPS 2024, arXiv:2404.16698) defines sustainability as **survival rate** — the proportion of runs where the shared resource pool stays above a collapse threshold. This is resource-stock survival in a common-pool resource game, not a production ratio. GovSim does not define "peace" at all. GovSim does use `1 − Gini` as an equality metric.

### Decision: rename, don't force-fit

Perolat's formulas are designed for gridworld environments (Melting Pot / Gathering / Cleanup) with tagging beams, apple spawning, and continuous timesteps. They don't translate meaningfully to a barter economy with discrete rounds and trade-level defection.

**Action**:
- Rename "sustainability" → **"production stability"** in the paper (and optionally in code)
- Rename "peace" → **"cooperation rate"** in the paper (and optionally in code)
- Define both clearly as our own constructs — no citation needed, just a clear formula in the methodology section
- Add **Gini coefficient** (citeable — used by both GovSim and Gallego/Perolat) as a third core metric
- Add **per-round mean utility** as a fourth core metric (standard welfare measure)

This avoids confusion with established definitions while keeping metrics that make sense for our barter economy.

### Proposed core metric set

| Metric | Formula | Citeable? | What it captures |
|---|---|---|---|
| Production Stability | `avg_production_t / avg_production_round1` | Our own construct | Are agents still producing? (market health) |
| Cooperation Rate | `1 - total_defections / total_trades` | Our own construct | Are agents honoring trades? (trust) |
| Gini Coefficient | `Σ|uᵢ−uⱼ| / (2n²·mean(u))` | GovSim; Gallego 2026; Shi et al. 2025 | Is utility distributed fairly? (inequality) |
| Per-Round Mean Utility | `mean(uᵢ)` per round | Standard welfare measure | Is the society producing value? (welfare) |
| Rawlsian Min Utility | `min(uᵢ)` per round | arXiv:2412.15163 | Is anyone being exploited? (worst-off agent) |

---

## Gini Coefficient as an Inequality Metric

**Problem**: Mean utility can be misleading. If one agent extracts most of the utility (e.g., consistently defects and takes goods without delivering), the group mean looks healthy while 17/18 agents are suffering. Mean utility is a **utilitarian** metric — it maximises the aggregate and ignores distribution.

**Proposed metric**: Gini coefficient per round, computed from per-agent utilities.

**Formula**:
```
G = Σᵢ Σⱼ |uᵢ − uⱼ| / (2n² · mean(u))
```
- G = 0: perfect equality (all agents earn the same utility)
- G = 1: maximum inequality (one agent gets everything)

**Negative utility caveat**: Standard Gini requires all values ≥ 0. Since our utilities can be negative (production costs, penalties, sanctions), shift all values by `|min(u)|` before computing. Alternatively, use the absolute-mean Gini variant.

**Key paper**: Shi et al. 2025, *"Social Welfare Function Leaderboard: When LLM Agents Allocate Social Welfare"* (arXiv:2510.01164)
- Setup: one LLM allocator distributes tasks to 12 recipient agents of varying capability; 20 LLMs tested (GPT-5, Claude Opus 4, Gemini 2.5 Pro, DeepSeek-V3)
- Uses `SWF Score = (1 − Gini) × ROI` as a composite metric combining fairness and efficiency
- Finding: most LLMs are strongly **utilitarian** by default — they maximise aggregate efficiency at the expense of severe inequality. 14/20 LLMs were less fair than a simple "assign to whoever has fewest tasks" heuristic
- GPT-5-High ranked #2 on Arena but dead last (#20) on SWF; DeepSeek-V3 went from Arena rank 25 to SWF rank 1
- No LLM beat the fairness-oriented heuristic baseline

**Relevance to our work**: Their paper measures inequality of task allocation from a central allocator. Our setup is stronger — 18 autonomous LLM agents making their own decisions, so inequality arises emergently rather than by central allocation. If GPT-5.4-mini has the same utilitarian bias, we should see some agents consistently exploiting others, and Gini would capture this where mean utility would not.

**Companion metrics to consider alongside Gini**:
- **Rawlsian min utility** (`min(uᵢ)` per round): no shifting needed, directly measures worst-off agent
- **Geometric mean** (`(∏ uᵢ)^(1/n)` after shifting): Nash Social Welfare proxy — collapses toward zero if any single agent has near-zero utility (ILLC/AAMAS 2008/2010)
- **Jain's Fairness Index** (`(Σu)² / (n·Σu²)`): bounded [1/n, 1], simpler than Gini but less sensitive to distributional shape

**Implementation**: All computable post-hoc from existing per-agent `utilities` dict logged every round. No simulation re-run needed. Add to `stats.py` and `plots.py`.

**Files to change**:
- `simulation/analysis/stats.py` — add `gini`, `min_utility`, `geo_mean_utility` to METRICS
- `simulation/analysis/plots.py` — add `plot_inequality_trajectories()` (2×4 grid, Gini + Rawlsian min over rounds per condition)

---

## Key Behavioral Findings from Literature

These findings should inform which mechanisms we prioritize:

1. **Cooperation collapse is the default** — GovSim: 43/45 scenarios collapsed (NeurIPS 2024)
2. **One defection triggers permanent retaliation** — LLMs are extremely unforgiving (Nature Human Behaviour 2025). Mechanisms need forgiveness/restoration paths, not just punishment
3. **Reasoning models free-ride more** — o1-style CoT models exploit sanctioning systems (Piedrahita 2025). Since we use all-CoT agents, this is directly relevant
4. **Communication is critical** — GovSim found it essential for cooperation. Our agents already communicate via public/private messages
5. **LLMs collude autonomously** — In Cournot settings, they divide markets without instruction (Lin et al. 2024). Our multi-good setup may see similar emergent collusion
6. **Anchoring effects are strong** — Initial offers predict outcomes in LLM bargaining (arXiv:2512.09254). Contract terms or mediator prices may anchor all subsequent trades

---

## Research Paper References

- GovSim — Piatti et al., NeurIPS 2024 (arXiv:2404.16698)
- RepuNet — arXiv:2505.05029 (May 2025)
- Playing Repeated Games with LLMs — Nature Human Behaviour 2025
- Institutional AI: Governance Graphs — arXiv:2601.11369 (Jan 2025)
- Corrupted by Reasoning — arXiv:2506.23276 (2025)
- Evolution of Social Norms in LLM Agents — arXiv:2409.00993 (Sep 2024)
- Strategic Collusion of LLM Agents — Lin et al., NeurIPS LangGame 2024
- The AI Economist — Zheng et al., Science Advances 2022
- LLM Economist — arXiv:2507.15815 (2025)
- Quantifying Trust (ARS) — arXiv:2604.03976
- Blockchain+MARL — Nature Scientific Reports 2025
- Democracy-in-Silico — arXiv:2508.19562 (2025)
- GLEE Benchmark — arXiv:2410.05254 (Oct 2024)
- ALYMPICS — COLING 2025 (arXiv:2311.03220)
- Interpretable Automated Mechanism Design — arXiv:2502.12203 (Feb 2025)
- Structuring Collective Action with LLM-Guided Evolution — arXiv:2509.20412 (Dec 2025)
- Communication Enables Cooperation — arXiv:2510.05748
