# Idea Dump

> These are exploratory ideas and notes — not committed to implementation.
> Last updated: 2026-05-29

---

## Current Setup Summary

- **18 LLM agents**, 6 per good (A, B, C), all CoT reasoning (5-step: situation, self-reflection, gossip evaluation, assessment, strategy)
- **Models**: GPT-5.4-mini (Azure, default) and DeepSeek-V3.2 (Azure) — `--model` flag switches between them. Each model logs to its own folder (`data/runs/gpt-5.4-mini/`, `data/runs/deepseek-v3/`). Cross-model comparison plot implemented.
- **Barter economy**: no tokens, goods-for-goods trade, cost 1 utility to produce, 3 utility per consumed unit, 20% spoilage
- **Phase 1**: 30 rounds, 3 runs per condition. **Phase 2**: 100 rounds, 1 run, with `--trolls N` and `--rounds N` CLI flags
- **Two-tier trade history**: lifetime partner summary (all rounds, never forgotten) + recent detail window (last 5 rounds). Agents see "Agent 5: 12 trades, 12/12 defections by them (100%)" — prevents trolls being "forgiven" when evidence scrolls out of the detail window.
- **Self-interest framing**: explicit prompt language ("Your only goal is to maximise your own total utility") counteracting RLHF cooperative prior
- **No end-game information**: agents see only "Round N" — no total rounds, no rounds remaining. Prevents backward induction and end-game defection collapse.
- **No market health metrics in prompt**: agents do NOT see peace/sustainability scores. They must assess market state through their own experience and gossip.
- **5 core metrics** — see "Metrics Provenance" and "Gini Coefficient" sections below:
  - Production Stability (our construct), Cooperation Rate (our construct), Gini coefficient (citeable), Per-round mean utility, Rawlsian min utility
- **Cooperation threshold**: both Production Stability and Cooperation Rate > 0.5

### Implemented Mechanisms (7 conditions)

| Code | Mechanism | Type | Description |
|------|-----------|------|-------------|
| B | Baseline | — | No mechanism. Pure self-interest dynamics. Fixed network. |
| GR | Global Reputation | Agent-participatory | System-tracked reputation (exponential decay: 0.9 * old + 0.1 * observation), visible to agents, initial = 1.0. Fixed network. Upper-bound test — unrealistically powerful (trolls isolated in ~2 rounds). |
| C | Contracting | Agent-participatory | Formal binding contracts: propose → sign/reject → enforce. Breach penalty = 6 utility. Fixed network. |
| M | Mediation | Agent-participatory | Democratic: agents propose mediator rules, vote, then delegate trades. Fee = 1 utility. Fixed network. |
| G | Governance | External-deterministic | Oracle detects defection patterns (4 signals, 5-round window) → escalates: Active → Warning → Fined → Suspended. Fixed network. |
| NR | Network Rewiring + Local Reputation | Agent-participatory | Agents sever/request links + 10-round rolling gossip history. No system scores — agents form own trust assessments from direct experience and unverified public messages. Inspired by RepuNet (arXiv:2505.05029). |
| S | Sanctions | Agent-participatory | Costly punishment: spend 1 utility → target loses 3. Anonymous, public announcement. Fixed network. Based on Piedrahita et al. 2025. |

Full factorial combinations (RC, RM, etc.) disabled until initial results reviewed.

### Information Gradient: B → NR → GR

| | B | NR | GR |
|---|---|---|---|
| Private experience | Lifetime summary + last 5 rounds | Same | Same |
| Current round public messages | Yes | Yes | Yes |
| Historical gossip (last 10 rounds) | No | **Yes** | No |
| Network reshaping | No | **Yes (sever/request)** | No |
| System reputation scores | No | No | **Yes** |
| End-game info | No | No | No |
| Market health metrics | No | No | No |

B agents can only warn others in the moment — those warnings vanish next round. NR agents accumulate gossip over 10 rounds, so a warning about a troll in round 5 is still visible in round 14. Combined with the ability to sever links, NR agents can both *remember* and *act on* collective intelligence. GR gives agents a global, system-computed signal — unrealistically powerful but useful as an upper bound.

### Troll Agents (Phase 2)

- **Deterministic**: no LLM calls, zero cost per round
- **Does NOT produce**: 0 production every round (pure parasite)
- **Actively proposes trades**: trolls propose trades to ALL neighbors every round (offering 2 units of their specialty for 2 units of a needed good)
- **Defects on ALL trades**: whether they proposed or the other agent proposed, trolls take goods and deliver nothing
- **Lies in messages**: sends public messages claiming fair cooperation ("I'm committed to fair trading!"). Tests whether agents learn to weigh actions over words
- **Fully connected**: trolls are connected to ALL other agents in the network initially (maximally exposed)
- **Round-robin distribution**: 2 trolls = agents 0 (Good A) + 6 (Good B)
- **Excluded from metrics**: trolls are excluded from sustainability, peace, utility averages, and distribution plots. Only non-troll-to-non-troll trades count.
- **CLI**: `--trolls N` flag, `--rounds N` for longer games
- **File naming**: `{condition}_t{n_trolls}_run_{idx:02d}.json`

---

## NR Design — Local Gossip Reputation

**Based on**: RepuNet (arXiv:2505.05029, May 2025, AAMAS 2026) — Siyue Ren et al.

**Why not global reputation?** Our original R condition gave agents a system-computed score visible to all — trolls were isolated in ~2 rounds, far faster than RepuNet's 60-100 rounds. This was unrealistically powerful. RepuNet uses local/decentralized reputation where agents form their own assessments through direct experience and gossip.

**Our NR implementation:**
- **Network rewiring**: agents can sever links (unlimited per round) and request new links (auto-accepted). Full isolation allowed.
- **Gossip channel**: agents see a rolling 10-round history of all public messages from other agents. Messages are unverified — agents must judge credibility themselves.
- **No system scores**: agents are NOT told there is no global score — they simply don't receive one. Trust assessment comes from (1) lifetime partner summary, (2) recent trade detail, and (3) gossip.
- **Enhanced CoT reasoning**: all agents (not just NR) use 5-step reasoning including self-reflection ("how might others perceive me?") and gossip evaluation ("which warnings seem credible?").

**What NR tests**: Can decentralized information (gossip) + structural power (link severing) achieve cooperation comparable to a centralized system (GR)? RepuNet says yes, but slower. We expect troll isolation to take 5-10+ rounds in NR vs ~2 in GR.

**RepuNet key results** (for reference):
- Public goods game: cooperation 0.19 → 0.85 (4.5x improvement)
- Trust game: cooperation 0.17 → 0.98 (5.8x improvement)
- Ablation: removing gossip barely hurts (0.85→0.81); removing reputation collapses everything (0.85→0.29)

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

- All 7 conditions: B, GR, C, M, G, NR, S
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

**Troll design** — see "Troll Agents" section above. Key: trolls **actively propose trades** to all neighbors and **lie in public messages** while defecting on everything. This tests whether agents learn to weigh actions over words.

**Collapse definition** (decided): per-round mean utility < 0 sustained for **3+ consecutive rounds**.

**Key metric**: Per-round societal utility (NOT cumulative). Cumulative utility always increases as long as any agent cooperates — it never "dips." Per-round utility is what drops when trolls enter.

**Target result table:**

| Condition | Phase 1 Coop Rate | Phase 1 Prod Stability | Trolls to collapse |
|---|---|---|---|
| Top mechanism 1 | ? | ? | ? |
| Top mechanism 2 | ? | ? | ? |
| Top mechanism 3 | ? | ? | ? |
| Top mechanism 4 | ? | ? | ? |

**How each mechanism handles trolls (predicted):**

| Mechanism | Troll defense | Strategy type | Predicted resilience |
|---|---|---|---|
| B (baseline) | None — troll defects, victims retaliate, cascade collapse | — | Very low |
| GR | Troll's reputation drops, agents see they're bad — but can't avoid them (fixed network) | Information without action | Low-Medium |
| C | Troll breaches contracts, pays utility penalties — but trust damage done | Penalty | Medium |
| M | If troll delegates to mediator, mediator forces fair execution | **Neutralization** | High |
| G | Oracle detects 100% defection rate, escalates to fines/suspension | **Ejection** | High |
| NR | Agents sever links to troll + gossip spreads warnings — decentralized isolation | **Structural isolation + gossip** | Medium-High |
| S | Agents spend utility to punish troll; troll loses 3× per sanction | **Costly punishment** | Medium-High |

**Key insight**: Troll isolation happens in ALL mechanisms, not just NR. The difference is the mechanism:
- **Soft boycott** (B, GR, C, S): agents learn from lifetime partner summary and stop proposing/accepting trades. Slower, depends on agents processing history correctly. GR adds a public signal that speeds detection.
- **Structural isolation** (NR): agents sever network links based on experience + gossip. Permanent, visible to all, but slower than GR because information is decentralized.
- **Neutralization** (M): mediator overrides defection on delegated trades
- **Ejection** (G): oracle detects and suspends troll from market

M, NR, and G are predicted most resilient, but for fundamentally different reasons. This is a publishable finding if confirmed.

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
- **GR**: agents with low reputation received fewer trade proposals (information → avoidance)
- **G**: warned/fined agents reduced defection rate in subsequent rounds (deterrence → behavior change)
- **NR**: defectors' neighbor count dropped over time, cooperators' held stable (structural → isolation); gossip warnings preceded link severing (information → action)
- **C**: agents with active contracts defected less than in uncontracted trades (commitment → compliance)
- **M**: mediated trades had lower defection than unmediated trades (enforcement → fair execution)
- **S**: sanctioned agents reduced defection in subsequent rounds (punishment → behavior change)
All derivable from existing logged data — no new simulation runs needed, just post-hoc analysis.

**3. Controlled adversarial test (troll sweep)**
Inject hardcoded defectors (0, 2, 4, 6 trolls) and show which mechanisms maintain positive utility. Strongest evidence: the troll is a known ground-truth defector — if G suspends it, if NR isolates it, that's proof the mechanism detected and contained a real adversary.

### Open Design Questions

- **Timing**: trolls from round 1 (decided) or injected mid-game? Round-1 injection is simpler and tests steady-state resilience
- **Troll placement**: round-robin across goods (decided). Targeted placement (hub agent) could be a future extension
- **Troll awareness**: agents do NOT know trolls exist — they discover it through experience and gossip
- **Mixed trolls**: all 100% defection rate (decided). Variable defection rates (50%, 75%) could be a future extension
- **Cross-model comparison**: run same conditions on GPT-5.4-mini and DeepSeek-V3.2. If both agree, mechanisms are robust to model choice. If they diverge, high baseline cooperation may be model-specific RLHF bias

---

## Metrics Provenance — "Sustainability" and "Peace" Are Our Own Constructs

**Issue**: The codebase uses metrics named "sustainability" and "peace" internally. These names overlap with established definitions in the literature, but our formulas do not match. We cannot cite those papers for our metrics.

### What the literature defines

**Perolat et al. 2017** (used by Gallego 2026, arXiv:2603.19453 — "Cooperation and Exploitation in LLM Policy Synthesis for Sequential Social Dilemmas") defines four standard metrics for sequential social dilemmas:

| Metric | Perolat Definition | Our Definition | Compatible? |
|---|---|---|---|
| **Sustainability** | Mean timestep at which agents earn positive reward (temporal — did resources last through the episode?) | `production_t / production_round1` (ratio — are agents still producing at round-1 levels?) | **No** — theirs is temporal distribution, ours is a production ratio |
| **Peace** | Avg number of agents active per step, not tagged out by combat (gridworld-specific) | `1 - defections/trades` (fraction of trades without defection) | **No** — theirs counts agent-steps lost to combat beams, ours counts trade-level defection |
| **Equality** | `1 − Gini` over total agent rewards | Not yet implemented | — |
| **Efficiency** | Total reward per timestep | `mean_utility` per round | Closest match |

**GovSim** (Piatti et al., NeurIPS 2024, arXiv:2404.16698) defines sustainability as **survival rate** — the proportion of runs where the shared resource pool stays above a collapse threshold. GovSim does use `1 − Gini` as an equality metric.

### Decision: rename in paper, keep internal keys

- Display as **"Production Stability"** in paper and plot titles
- Display as **"Cooperation Rate"** in paper and plot titles
- Internal keys remain `sustainability` and `peace` to avoid breaking existing logs
- Define both clearly as our own constructs — no citation needed, just a clear formula in the methodology section
- Add **Gini coefficient** (citeable) and **Rawlsian min utility** as additional metrics (not yet implemented)

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

**Problem**: Mean utility can be misleading. If one agent extracts most of the utility (e.g., consistently defects and takes goods without delivering), the group mean looks healthy while 17/18 agents are suffering.

**Formula**:
```
G = Σᵢ Σⱼ |uᵢ − uⱼ| / (2n² · mean(u))
```
- G = 0: perfect equality; G = 1: maximum inequality

**Negative utility caveat**: Standard Gini requires all values ≥ 0. Since our utilities can be negative, shift all values by `|min(u)|` before computing.

**Key paper**: Shi et al. 2025, *"Social Welfare Function Leaderboard"* (arXiv:2510.01164) — finding: most LLMs are strongly utilitarian by default, maximising aggregate efficiency at the expense of severe inequality.

**Implementation**: Computable post-hoc from existing per-agent `utilities` dict. No simulation re-run needed.

---

## Key Behavioral Findings from Literature

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
- CoopEval — arXiv:2505.00754 (cooperation evaluation framework)
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
- Social Welfare Function Leaderboard — Shi et al. 2025 (arXiv:2510.01164)
