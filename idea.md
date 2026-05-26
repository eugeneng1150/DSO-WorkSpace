# Idea Dump

> These are exploratory ideas and notes — not committed to implementation.
> Last updated: 2026-05-22

---

## Current Setup Summary

- **18 LLM agents** (gpt-5.4-nano via Azure), 6 per good (A, B, C), all CoT reasoning
- **Barter economy**: no tokens, goods-for-goods trade, cost 1 utility to produce, 3 utility per consumed unit, 20% spoilage
- **30 rounds**, 15 runs per condition, 7-9 neighbors per agent
- **2 core metrics**: Sustainability (production vs round 1 baseline), Peace (cumulative: 1 - total defections / total trades)
- **Cooperation threshold**: both metrics > 0.5
- **Utility**: unbounded but O(n) growth — no compounding mechanism, linear accumulation per round

### Current Mechanisms (2^4 factorial = 16 conditions)

| Code | Mechanism | Type | Description |
|------|-----------|------|-------------|
| R | Reputation | Agent-participatory | System-tracked reputation (exponential decay: 0.9 * old + 0.1 * observation), visible to agents, initial = 1.0 |
| C | Contracting | Agent-participatory | Formal binding contracts: propose → sign/reject → enforce. Breach penalty = 6 utility (2x one unit's value) |
| M | Mediation | Agent-participatory | Democratic: agents propose mediator rules, vote, then delegate trades. Mediator executes fair/split/cancel. Fee = 1 utility |
| G | Governance | External-deterministic | **IMPLEMENTED.** Oracle detects defection patterns (4 signals, 5-round window) → Controller escalates: Active → Warning → Fined (2/4/6 utility) → Suspended (3 rounds, no trade/production). De-escalation via 2 consecutive clean rounds. |
| N | Network Rewiring | Agent-participatory | **IMPLEMENTED.** Standalone 17th condition (not factorial-combined). Agents can sever_link (1/round, unilateral, immediate) and request_link (1/round, auto-accept if target < 9 neighbors). No minimum floor — full isolation allowed. Adapted from RepuNet (arXiv:2505.05029). Private reputation is implicit via trade history + CoT reasoning. |

Conditions: B, R, C, M, G, N (isolated mechanisms for initial runs). Full factorial (RC, RM, RG, CM, CG, MG, RCM, RCG, RMG, CMG, RCMG) disabled until initial results reviewed.

---

## Potential New Mechanism: Governance (G)

**Source**: "Institutional AI: Governing LLM Collusion in Multi-Agent Cournot Markets via Public Governance Graphs" (arXiv:2601.11369, Jan 2025)

### Key Contrast with R/C/M

R, C, M are all **agent-participatory** — agents choose whether to use them, propose rules, vote, sign contracts. Governance (G) is **external and deterministic** — agents cannot opt out or influence the rules. This is a fundamentally different institutional design philosophy:
- R/C/M = bottom-up, agent-designed institutions
- G = top-down, externally imposed regulation

### How It Would Work in Our Setup

**State machine**: Active → Warning → Fined → Suspended (+ Credited for restoration)

**Oracle (deterministic, no LLM)**: Each round, monitors public market signals:
- Defection rate spike (rolling window)
- Trade concentration (one agent monopolizing a good)
- Production withdrawal (agents reducing output)
- Collusion signals (repeated exclusive partnerships)

**Controller**: When signals fire, traverses the governance graph:
- Active → Warning: public notice, no penalty
- Warning → Fined: utility penalty (graduated: 35% / 75% / 100% of round utility)
- Fined → Suspended: removed from trade for N rounds (production forced to zero)
- Restorative: Fined → Credited → Active (earn credits via good behavior, spend to reduce penalties)

**Agent integration**: Governance notices injected into prompts each round (current status, warnings, fine amounts, recovery guidance). Agents respond by changing behavior, not by changing rules.

**Deterrence condition**: pS >= Δπ (probability of detection × sanction cost >= collusive profit gain)

### Factorial Design Impact

Adding G as a 4th factor:
- **Full factorial**: 2^4 = 16 conditions × 15 runs = 240 runs (doubles compute)
- **Selective**: Only run G, GR, GC, GM, GRCM = 5 extra conditions (13 total)

### Open Questions

- What oracle thresholds make sense for our marketplace? (Paper used Cournot-specific HHI/CV — we need trade-specific signals)
- Should fines be utility-based (like breach penalties) or token-based?
- How many rounds of suspension is meaningful in a 30-round game?
- Does G make R redundant? (Both track behavior, but G punishes while R merely informs)
- Does G + M create tension? (Agents vote on mediation rules, but governance overrides them?)

---

## Governance Signal Validity (D2 and D3)

**Issue**: D1 and D4 are clearly defection-based signals grounded in the governance literature. D2 (production withdrawal) and D3 (trade volume collapse) were added by Claude without a specific paper citation. They may be penalising agents unfairly.

**D3 specific problem**: An agent can trigger D3 (fewer than 2 completed trades in 5 rounds) even if it's not their fault — e.g. their neighbors are refusing to trade with them. The oracle punishes the victim, not the defector.

**Options to consider:**

| Option | What changes | Risk |
|---|---|---|
| Remove D2 and D3 entirely | Only keep D1 (defection rate) and D4 (predatory targeting) | G becomes purely defection-reactive; production/participation collapse goes undetected |
| Keep D2, remove D3 | Production withdrawal is a plausible signal; trade volume is too noisy | Partial fix |
| Fix D3 to be proposer-side only | Only count trades *proposed by the agent* that collapsed, not trades where others rejected them | More defensible but harder to implement |
| Cite a paper for D2/D3 | Find a governance/market regulation framework that justifies monitoring production and trade volume | Preferred if a citation exists |

**Files to change if removing D2 and D3:**
- `simulation/mechanisms/governance.py` — remove `_check_production_withdrawal` and `_check_trade_volume_collapse` methods, remove D2/D3 from `evaluate()`
- `prompts/governance.txt` — remove D2 and D3 from the signal list shown to agents

**Decision needed**: Keep, fix, or remove D2/D3?

---

## Other Candidate Mechanisms (From Literature)

### Costly Punishment / Sanctions (S)
- **Paper**: Piedrahita et al. 2025, "Corrupted by Reasoning" (arXiv:2506.23276)
- **Idea**: Agents can spend tokens/utility to punish defectors. Cost-to-impact ratio (e.g., 1:3 — spend 1 token to inflict 3 utility damage)
- **Difference from G**: Agent-initiated punishment vs externally imposed. Agents choose WHO to punish and pay the cost
- **Key finding from paper**: Reasoning LLMs (o1-style) free-ride MORE in sanctioning institutions — they exploit the system
- **Open question**: Does this just become griefing? Need to consider false punishment

### Taxation / Redistribution (T)
- **Paper**: Zheng et al. 2022, "The AI Economist" (Science Advances); "LLM Economist" (arXiv:2507.15815, 2025)
- **Idea**: Tax a percentage of each agent's round utility, redistribute equally or to lowest-utility agents
- **Difference from R/C/M**: Addresses inequality, not defection. Could stabilize Sustainability by supporting struggling agents
- **Open question**: What tax rate? Flat or progressive? Does redistribution remove incentive to trade well?

### Escrow / Performance Bonds (E)
- **Paper**: "Quantifying Trust: Financial Risk for AI Agents" (ARS, arXiv:2604.03976); Blockchain+MARL (Nature Sci Reports 2025)
- **Idea**: Before a trade, both parties stake collateral (tokens). If trade succeeds, collateral returned. If one defects, their collateral goes to the victim
- **Difference from C**: Contracting is post-hoc (penalty after breach). Escrow is pre-committed (stake before trade)
- **Open question**: How much collateral? Agents with low tokens can't afford to stake — creates barrier to trade

### Dynamic Partner Selection / Network Rewiring (N) — PREFERRED CANDIDATE

**Paper**: "Reputation as a Solution to Cooperation Collapse in LLM-based MASs" (RepuNet, arXiv:2505.05029, May 2025, AAMAS 2026)
- Authors: Siyue Ren, Wanli Fu, Xinkun Zou, Chen Shen, Yi Cai, Chen Chu, Zhen Wang, Shuyue Hu

**RepuNet in detail:**
- Two-level mechanism: (1) agent-level reputation dynamics, (2) system-level network rewiring
- Reputation is LLM-generated: score from -1 to +1 plus natural language description, updated after every encounter
- Gossip mechanism: agents can spread info about others, listeners evaluate credibility on 5-point scale
- Network is a directed graph — edge i→j means "i is willing to trade with j"
- After each encounter, agent decides via LLM: keep edge ("Y") or sever ("N")
- Gossip can sever existing edges but CANNOT create new ones (need direct encounter first)
- Result: cooperators cluster, defectors get isolated

**Their results:**
- Public goods game: cooperation 0.19 → 0.85 (4.5x improvement)
- Trust game: cooperation 0.17 → 0.98 (5.8x improvement)
- Ablation: removing gossip barely hurts (0.85→0.81); removing reputation collapses everything (0.85→0.29)
- Emergent finding: LLM agents share 90% positive gossip (opposite of human tendency)

**How N would work in our setup:**
- Start with same fixed 7-9 neighbor graph
- Each round (when N is active), agents can:
  - **Sever** a link to a neighbor they no longer trust
  - **Request** a new link to a non-neighbor (requires mutual consent or reputation threshold)
- Network evolves over 30 rounds — defectors lose trade partners, cooperators gain them
- Agent sees updated neighbor list in prompt each round

**Design decision: N as separate mechanism vs dense starting network**

| Approach | Pros | Cons |
|---|---|---|
| **N as toggleable mechanism** (recommended) | Clean factorial comparison; same starting graph for all conditions; directly measures what rewiring adds; isolation of defectors is a measurable emergent outcome | Agents start with limited partners; may need several rounds before rewiring has effect |
| **Dense network (everyone starts connected)** | More "realistic"; no initial topology bias | 17 potential partners per agent makes prompts huge; removes scarcity of trade partners (key driver of the dilemma); changes baseline game structure so you can't cleanly measure what N adds; defection matters less if you can always find someone else |

**Recommendation: N as a separate toggleable mechanism.** The interesting finding from RepuNet was that cutting off defectors works — not starting connected and hoping for the best. Starting sparse and letting agents earn/lose connections creates real stakes. A dense network removes the scarcity that makes cooperation valuable.

**Two types of reputation — important distinction:**

| | Our R mechanism | RepuNet's built-in reputation (part of N) |
|---|---|---|
| Who computes it | System (deterministic formula: 0.9 * old + 0.1 * observation) | Each agent via LLM reflection |
| Score | Objective, same for all observers | Subjective, differs per observer (agent i's view of j ≠ agent k's view of j) |
| Visibility | Public — every agent sees the same number | Private — only the evaluating agent sees their own assessment |
| Update rule | Hardcoded exponential decay | LLM decides based on encounter context + prior assessment |
| Includes | Numerical score only | Numerical score (-1 to +1) + natural language description |

N is a **self-contained mechanism** — it already includes its own agent-level reputation layer (self-reflection + subjective peer evaluation). Agents reflect on each encounter, form their own private assessments, and rewire based on those. N alone is NOT "rewiring blind."

**Interaction with R — what each combination tests:**
- **R alone**: agents see a public objective reputation score but can't structurally act on it (fixed network)
- **N alone**: agents maintain private subjective reputations via LLM reflection + rewire based on them (RepuNet-style, self-contained)
- **RN together**: agents have BOTH private subjective evaluations AND the system's public objective score — does the public signal help coordination, or does it just create anchoring bias on the LLM's own judgment?

This gives us a clean comparison of three reputation philosophies:
1. **Top-down information** (R): system tells you who to trust
2. **Bottom-up judgment** (N): you decide for yourself who to trust, and act on it
3. **Both** (RN): system score + personal judgment — do they complement or conflict?

**Open questions:**
- How many sever/request actions per round? (1 each? unlimited?)
- Should severed agents be able to reconnect later? (forgiveness path)
- Minimum neighbor count floor? (prevent total isolation — agent with 0 neighbors can't trade at all)
- If bad agents get isolated, they can't earn utility or recover — is that a feature (strong deterrence) or a problem (no restoration)?
- For N: how much LLM cost does per-encounter reflection add? (RepuNet uses 9 prompt templates per reputation update — with 18 agents and multiple trades per round, this could be expensive)
- Does the public R score anchor/override the agent's own subjective judgment in RN? (anchoring effects are strong in LLMs — see behavioral findings)

### Metanorm Enforcement
- **Paper**: "Evolution of Social Norms in LLM Agents using Natural Language" (arXiv:2409.00993, Sep 2024)
- **Idea**: Second-order punishment — punish agents who FAIL to punish defectors. Creates social pressure to enforce norms
- **Difference from S**: Sanctions target defectors. Metanorms target bystanders who tolerate defection
- **Open question**: Very complex — agents need to observe who punished whom. May be too much cognitive load for the LLM

### Insurance / Risk Pooling (I)
- **No LLM-specific paper** — classical basis: Arrow 1963, Townsend 1994
- **Idea**: Agents pool tokens into an insurance fund. If an agent gets defected on, the fund compensates them. Premium paid each round
- **Difference from all others**: Doesn't prevent defection — mitigates its damage. Reduces risk aversion that drives conservative/defensive play
- **Open question**: Novel contribution opportunity (no one has done this with LLM agents). But complex to implement and explain to agents

---

## Experimental Design: Two-Phase Resilience Study

### Research Question

Which institutional mechanisms allow a marketplace of self-interested LLM agents to sustain cooperation — and how resilient are those mechanisms to adversarial actors that cannot be incentivized?

### Key Framing

All agents are **self-interested**, not good-faith cooperators. Mechanisms work by making cooperation the **rational choice**. A "troll" is a hardcoded defector — a self-interested agent that **cannot be incentivized** to cooperate regardless of mechanism. The question is: can the mechanism sustain cooperation among the remaining rational agents even when some participants are immune to incentives?

### Phase 1: Mechanism Selection (current work)

**Goal**: Which mechanisms make cooperation the rational choice for self-interested agents?

- All mechanism conditions (B, R, C, M, RC, RM, CM, RCM — potentially more with G, N)
- 0 trolls — pure self-interest dynamics
- 15 runs per condition, 30 rounds
- Metrics: Peace, Sustainability, per-round societal utility
- **Output**: Ranked list of mechanism conditions by cooperation outcomes

### Phase 2: Adversarial Resilience (future work)

**Goal**: Take the top 3-4 mechanisms from Phase 1 and stress-test with escalating trolls.

**Why funnel, not full factorial**: If a mechanism can't even get self-interested agents to cooperate in Phase 1, there's no point testing it against trolls — it already fails. A troll is just a more extreme version of self-interest. But run the top 3-4 (not just the single winner) in case rankings shift under adversarial pressure.

**Troll agent design** (hardcoded, no LLM — may become LLM-driven later):
- **Does NOT produce** anything (0 production — pure parasite)
- **Does NOT propose trades** (has nothing to offer)
- **Does NOT send messages** (silent)
- **Defects on ALL incoming trade offers** (takes goods, delivers nothing)
- Ignores all mechanism features (doesn't sign contracts honestly, doesn't respect mediator, etc.)
- Makes 0 LLM calls — deterministic, cheap to run
- Distributed evenly across goods via round-robin (2 trolls = 1 from Good A group, 1 from Good B group)

**Implementation approach**: `TrollAgent(_BaseAgent)` class in `agent.py`. In `_call_agents_phase`, skip prompt building and LLM call for trolls. Trade phase: return `defect_trade` for every pending offer via `agent.get_trade_actions(market)`. `make_agents(n_trolls=N)` replaces N agents. CLI: `--trolls N` and `--troll-sweep` for full sweep.

**File naming with trolls**: `{condition}_t{n_trolls}_run_{idx:02d}.json` (e.g., `B_t2_run_00.json`)

**Escalation**: inject 0, 2, 4, 6 trolls (out of 18 agents) — find each mechanism's **breaking point**

**Key metric**: Per-round societal utility (NOT cumulative). Cumulative utility always increases as long as any agent cooperates — it never "dips." Per-round utility is what drops when trolls enter, and what goes to zero when society collapses.

**Target result table:**

| Condition | Phase 1 Peace | Phase 1 Sustainability | Trolls to collapse |
|---|---|---|---|
| Top mechanism 1 | ? | ? | ? |
| Top mechanism 2 | ? | ? | ? |
| Top mechanism 3 | ? | ? | ? |
| Top mechanism 4 | ? | ? | ? |

**Collapse definition** (needs decision): when per-round societal utility drops below a floor, or Peace drops below 0.5, sustained for N consecutive rounds.

**Target graph** (the paper figure):
```
plot_troll_sweep():
  X-axis: Number of trolls (0, 2, 4, 6)
  Y-axis: Final-round mean utility (averaged across runs)
  Lines:  One per condition (B, R, C, M, G, N)
  Horizontal line at y=0 (collapse threshold)
  Shows: which mechanisms hold positive utility longest as trolls increase
```

**How each mechanism handles trolls (predicted):**

| Mechanism | Troll defense | Predicted resilience |
|---|---|---|
| B (baseline) | None. Troll defects, victims retaliate, cascade collapse | Very low — 1 troll may be enough |
| R | Troll's reputation drops, agents can see they're bad — but can't avoid them (fixed network) | Low — information without action |
| C | Troll breaches contracts, pays utility penalties — but trust damage already done | Medium — penalties hurt troll but don't prevent initial damage |
| M | If troll delegates to mediator, mediator forces fair execution — **neutralizes** the troll | High — mechanism directly overrides troll's defection |
| N | Agents sever links to troll — troll gets **isolated** from trade network. Troll produces nothing so no trade value. | High — mechanism quarantines the troll |
| G | Oracle detects troll's defection pattern (D1 fires immediately at 100% defection rate), escalates to fines/suspension | High — troll gets suspended from market entirely |

M, N, and G are predicted to be most resilient, but for fundamentally different reasons:
- **M**: neutralizes troll behavior (forces fair trade)
- **N**: quarantines troll from network (cuts off access)
- **G**: punishes/removes troll from market (suspension)

This is a publishable finding if confirmed — different mechanisms defend against adversaries through different strategies (neutralization vs isolation vs ejection).

### Substantiating Claims (Post-Experiment Analysis)

Three levels of evidence, from weakest to strongest:

**1. Statistical significance (p-values)**
With 15 runs per condition, use Mann-Whitney U test (non-parametric, no normality assumption) to compare each mechanism vs baseline B:
```python
from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(mechanism_utilities, baseline_utilities, alternative="greater")
```
Report as a table: condition | mean final utility | p-value vs B. p < 0.05 = significant.
Also compare across mechanisms (R vs G, N vs G, etc.) for pairwise rankings.

**2. Causal pathway evidence (mechanism of action)**
Don't just show outcomes improved — show the mechanism worked THROUGH its intended channel:
- **R**: agents with low reputation received fewer trade proposals (information → avoidance)
- **G**: warned/fined agents reduced defection rate in subsequent rounds (deterrence → behavior change)
- **N**: defectors' neighbor count dropped over time, cooperators' held stable (structural → isolation)
- **C**: agents with active contracts defected less than in uncontracted trades (commitment → compliance)
- **M**: mediated trades had lower defection than unmediated trades (enforcement → fair execution)
All derivable from existing logged data — no new simulation runs needed, just post-hoc analysis.

**3. Controlled adversarial test (troll sweep)**
Inject hardcoded defectors (0, 2, 4, 6 trolls) and show which mechanisms maintain positive utility. This is the strongest evidence because the troll is a known ground-truth defector — if G suspends it, if N isolates it, that's proof the mechanism detected and contained a real adversary. See Phase 2 below.

### Open Design Questions for Phase 2

- **Timing**: trolls from round 1, or injected mid-game (e.g., round 15)? Round 1 tests resilience; mid-game tests recovery
- **Round count**: 30 rounds may be too short for Phase 2. Consider 50+ rounds to give mechanisms time to detect and respond
- **Troll placement**: random placement in the network, or targeted (e.g., troll placed as a hub with max neighbors)? Random is cleaner but targeted is more adversarial
- **Troll awareness**: do other agents know trolls exist? Or do they discover it through experience?
- **Mixed trolls**: all trolls defect 100%? Or vary (some defect 50%, some 100%) for a more realistic adversary spectrum?

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
