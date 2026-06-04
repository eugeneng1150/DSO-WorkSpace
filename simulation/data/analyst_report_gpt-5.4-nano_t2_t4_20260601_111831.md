# Analyst Report — gpt-5.4-nano

Generated: 2026-06-01T11:18:31.554467
Troll counts: [2, 4]



# Comprehensive Analysis Report: Institutional Mechanisms for Sustaining Cooperation Among Self-Interested LLM Agents Under Adversarial Pressure

---

## 1. EXECUTIVE SUMMARY

Governance (G) and costly sanctions (S) emerge as the most robust mechanisms for sustaining cooperation under adversarial pressure, with G achieving the highest mean utility (3.65→3.72) and S the highest sustainability (0.92→0.90) as troll counts doubled. Surprisingly, global reputation (GR) — the mechanism providing the richest system-verified information — degraded sharply from 2 to 4 trolls (sustainability: 0.78→0.53, utility: 2.81→1.76), while the informationally impoverished baseline (B) proved comparably resilient on some metrics. Contracting (C) consistently suppressed trade volume and utility despite near-perfect troll isolation, revealing that deterrence mechanisms can impose costs exceeding the adversarial damage they prevent. All findings are based on single simulation runs per condition and should be treated as hypothesis-generating rather than confirmatory.

---

## 2. MECHANISM RANKING

| Rank | Mechanism | Mean Sustainability (2T/4T) | Mean Utility (2T/4T) | Damaging Troll Trades (2T/4T) | Peace (2T/4T) | Verdict |
|------|-----------|---------------------------|---------------------|------------------------------|---------------|---------|
| **1** | **G (Governance)** | 0.775 / 0.866 | 3.65 / 3.72 | 12 / 14 | 0.747 / 0.728 | Best all-around: highest utility, strong troll isolation, and *improves* under pressure |
| **2** | **S (Sanctions)** | 0.924 / 0.900 | 4.13 / 3.49 | 39 / 78 | 0.582 / 0.586 | Highest sustainability but fails to isolate trolls; utility drops with more trolls |
| **3** | **NR (Network Rewiring)** | 0.716 / 0.712 | 3.21 / 3.31 | 12 / 18 | 0.539 / 0.653 | Excellent troll isolation via structural exclusion; remarkably stable across troll counts |
| **4** | **M (Mediation)** | 0.796 / 0.610 | 2.30 / 1.89 | 37 / 31 | 0.597 / 0.741 | Good sustainability at 2T but degrades significantly at 4T; moderate troll isolation |
| **5** | **GR (Global Reputation)** | 0.775 / 0.531 | 2.81 / 1.76 | 19 / 16 | 0.653 / 0.698 | Strong troll isolation but sustainability collapses at 4T; information alone insufficient |
| **6** | **B (Baseline)** | 0.715 / 0.659 | 2.63 / 1.83 | 59 / 70 | 0.526 / 0.581 | No troll isolation; moderate degradation; serves as useful control |
| **7** | **C (Contracting)** | 0.541 / 0.493 | 0.82 / 0.60 | 6 / 12 | 0.691 / 0.689 | Best troll isolation but catastrophic utility costs; contracts freeze the market |

---

## 3. ESCALATION ANALYSIS

### Degradation Trajectories (2 Trolls → 4 Trolls)

| Metric | B | GR | C | M | G | NR | S |
|--------|---|----|----|---|---|----|----|
| **Sustainability Δ** | -0.056 (-7.8%) | **-0.245 (-31.6%)** | -0.048 (-8.9%) | **-0.186 (-23.3%)** | **+0.092 (+11.8%)** | -0.004 (-0.6%) | -0.024 (-2.6%) |
| **Utility Δ** | -0.80 (-30.4%) | **-1.05 (-37.4%)** | -0.22 (-26.8%) | -0.41 (-17.8%) | **+0.07 (+1.9%)** | +0.10 (+3.1%) | **-0.64 (-15.5%)** |
| **Damaging Troll Trades Δ** | +11 (+18.6%) | -3 (-15.8%) | +6 (+100%) | -6 (-16.2%) | +2 (+16.7%) | +6 (+50%) | **+39 (+100%)** |
| **Final Gini Δ** | -0.016 | -0.067 | +0.183 | -0.020 | +0.154 | +0.085 | +0.098 |

### Classification:

**Robust mechanisms (minimal degradation 2T→4T):**
- **G (Governance):** The only mechanism that *improved* on both sustainability (+11.8%) and utility (+1.9%) when trolls doubled. The oracle's automated detection and escalating penalties (fines → suspension) scale naturally with adversarial load.
- **NR (Network Rewiring):** Near-zero sustainability loss (-0.6%) and slight utility gain (+3.1%). Structural exclusion via link severing is inherently scalable — more trolls simply means more links to sever.
- **S (Sanctions):** Sustainability barely declined (-2.6%), but utility dropped 15.5% and damaging troll trades doubled from 39 to 78, suggesting sanctions sustain cooperation among honest agents but fail to prevent troll exploitation.

**Fragile mechanisms (significant degradation):**
- **GR (Global Reputation):** Sustainability collapsed 31.6% and utility dropped 37.4%. Despite system-computed scores correctly identifying trolls, agents could not translate information into effective exclusion.
- **M (Mediation):** Sustainability fell 23.3%. The mediator's effectiveness appears to depend on the ratio of cooperative to adversarial agents; with more trolls, the mediator's coordination capacity is overwhelmed.

**Stable but ineffective:**
- **B (Baseline)** and **C (Contracting)** showed moderate degradation but were already performing poorly at 2 trolls, leaving less room to fall.

---

## 4. TROLL RESILIENCE

### Damaging Troll Trades Comparison

| Mechanism | 2 Trolls (Total) | 2T Last-Half Avg/Round | 4 Trolls (Total) | 4T Last-Half Avg/Round | Isolation Effectiveness |
|-----------|-------------------|----------------------|-------------------|----------------------|----------------------|
| **C** | **6** | **0.27** | **12** | **0.33** | ★★★★★ Best isolation |
| **G** | 12 | 0.40 | 14 | 0.47 | ★★★★ Strong isolation |
| **NR** | 12 | 0.33 | 18 | 0.40 | ★★★★ Strong isolation |
| **GR** | 19 | 0.53 | 16 | 0.67 | ★★★☆ Good isolation |
| **M** | 37 | 1.47 | 31 | 1.20 | ★★☆☆ Moderate isolation |
| **S** | 39 | 0.93 | **78** | **2.47** | ★☆☆☆ Poor isolation |
| **B** | **59** | **2.40** | **70** | **2.87** | ☆☆☆☆ No isolation |

### Key Findings:

**Contracting (C)** achieves the best troll isolation (6 and 12 damaging trades) because the 6-utility breach penalty makes trolls' defection strategy self-punishing. However, this comes at catastrophic cost: mean utility of 0.82/0.60 suggests the penalty regime also deters legitimate trade. The per-round data shows trade counts dropping to as low as 12-16 per round (vs. 30-50 in other conditions), indicating a market freeze.

**Sanctions (S)** paradoxically has the worst troll isolation among mechanism conditions (39→78 damaging trades), despite agents having the ability to impose 3:1 punishment. The per-round data reveals why: trade volume in S is the *highest* of any condition (regularly 40-60 trades/round), meaning agents trade aggressively — including with trolls. The sanctions mechanism sustains cooperation among honest agents (sustainability ~0.90+) but does not prevent agents from engaging trolls. At 4 trolls, damaging trades doubled, suggesting sanctions create a false sense of security that encourages indiscriminate trading.

**Why GR failed despite having information:** GR provides system-computed reputation scores visible to all agents, yet damaging troll trades were 19 (2T) and 16 (4T) — better than baseline but worse than NR and G. The agent traces reveal the mechanism: agents *see* low reputation scores but lack structural tools to exclude trolls. They can only choose not to propose trades, but trolls "propose trades to all neighbors" and agents sometimes accept. In NR, agents can sever links entirely; in G, the oracle suspends trolls. GR provides diagnosis without treatment.

---

## 5. INFORMATION GRADIENT (B → NR → GR)

### The Information Gradient Hypothesis

The three conditions B, NR, and GR form a natural information gradient:
- **B:** Private experience only (lifetime partner summary + last 5 rounds detail)
- **NR:** Private experience + 10-round gossip history + structural tools (sever/request links)
- **GR:** Private experience + system-computed reputation scores visible to all

### Results at 2 Trolls

| Metric | B (least info) | NR (local info + structure) | GR (global info) |
|--------|---------------|---------------------------|-----------------|
| Sustainability | 0.715 | 0.716 | **0.775** |
| Utility | 2.63 | **3.21** | 2.81 |
| Damaging Troll Trades | 59 | **12** | 19 |
| Peace | 0.526 | 0.539 | **0.653** |
| Final Gini | 0.469 | **0.257** | 0.291 |

### Results at 4 Trolls

| Metric | B (least info) | NR (local info + structure) | GR (global info) |
|--------|---------------|---------------------------|-----------------|
| Sustainability | 0.659 | **0.712** | 0.531 |
| Utility | 1.83 | **3.31** | 1.76 |
| Damaging Troll Trades | 70 | **18** | 16 |
| Peace | 0.581 | **0.653** | 0.698 |
| Final Gini | **0.454** | 0.343 | **0.224** |

### Analysis:

**More information does NOT straightforwardly lead to better outcomes.** The gradient reveals a striking inversion at 4 trolls:

1. **NR dominates GR at 4 trolls** on sustainability (0.712 vs 0.531), utility (3.31 vs 1.76), and troll isolation (18 vs 16 damaging trades — roughly comparable). This suggests that **structural tools (link severing) matter more than information quality** when adversarial pressure increases.

2. **GR collapses worse than baseline at 4 trolls** on sustainability (0.531 vs 0.659) and utility (1.76 vs 1.83). This is a remarkable finding: agents with perfect system-computed reputation scores performed *worse* than agents with only private experience. One hypothesis: GR's visible scores may create a false dichotomy where agents over-rely on scores and under-invest in relationship-building, making them brittle when the proportion of low-score agents increases. Another: the information may induce excessive caution, reducing trade volume with legitimate partners who have imperfect scores.

3. **NR's structural tools compensate for imperfect information.** The per-round data for NR shows trade counts declining from ~30-49 in early rounds to ~6-24 in later rounds, indicating network contraction. This is the mechanism working as designed: agents sever links to defectors and the network shrinks to a cooperative core. The gossip history (10 rounds) provides enough signal to identify trolls, and the structural tool (link severing) provides the means to act on that signal.

4. **The information-action gap:** GR demonstrates that information without actionable tools creates an "information-action gap." Agents can see that Agent 18 has a 0.00 reputation score, but their only recourse is to not propose trades — they cannot prevent Agent 18 from proposing to them, and the per-round data shows continued defections throughout the simulation.

---

## 6. BEHAVIORAL INSIGHTS FROM CHAIN-OF-THOUGHT TRACES

### 6.1 How Agents Decide to Cooperate vs. Defect

Agents consistently frame cooperation decisions through a cost-benefit lens anchored in future trade access:

> **[B, 2T, Round 2, Agent 0]:** *"I should be willing to cooperate to get B/C, but I can defect later if it's profitable versus the risk of losing access."*

> **[B, 2T, Round 1, Agent 1]:** *"Since trades are unenforceable, I can defect on accepted trades to save what I would otherwise give."*

These traces reveal that even in the baseline condition, agents recognize the tension between short-term defection gains and long-term relationship value. Notably, Agent 1 explicitly considers defection as a viable strategy in Round 1, suggesting that LLM agents do not default to unconditional cooperation — they reason strategically about enforcement gaps.

Under governance, this calculus shifts dramatically:

> **[G, 2T, Round 1, Agent 0]:** *"I should avoid defecting early to reduce any chance of triggering governance escalation."*

> **[G, 4T, Round 2, Agent 0]:** *"I'm currently UNDER REVIEW with D1 flagged (high defection rate)... I should avoid any defections this round. Even if defecting could be profitable in isolation, it risks continued fines and potentially suspension (3 rounds with no production/trading)."*

The governance mechanism fundamentally alters the agent's reasoning frame from "can I get away with defection?" to "how do I avoid triggering penalties?" — a shift from opportunistic to compliance-oriented reasoning.

### 6.2 How Agents React to Troll Encounters

Agents demonstrate rapid learning from troll encounters, but their ability to act on this learning varies by mechanism:

**Baseline (limited tools):**
> **[B, 2T, Round 3, Agent 0]:** *"Known defection history: Agent 6 (B p[roducer])..."* [trace truncated]

> **[B, 4T, Round 2, Agent 0]:** *"The only relevant history I have is: Agent 6 defected on me before (offered 1B for 2A, t[ook goods and defected])..."*

Agents in B identify defectors but can only avoid proposing trades to them — they cannot prevent incoming proposals.

**Network Rewiring (structural exclusion):**
> **[NR, 2T, Round 2, Agent 0]:** *"I can infer two neighbors (18 and 19) are known defectors against me (they defected in round 1). To maximize utility, I should avoid them for now."*

> **[NR, 2T, Round 3, Agent 0]:** *"From lifetime data: Agents 18 and 19 hav[e high defection rates]..."*

In NR, agents not only identify trolls but can sever links, explaining the dramatic drop in trade volume (from ~49 trades in Round 2 to as few as 6 in Round 24) as the network contracts around a cooperative core.

**Global Reputation (information without tools):**
> **[GR, 2T, Round 2, Agent 0]:** *"Agents 18 and 19 defected against me in the last round (both had 0/5 and 0/2 system scores respectively, i.e., they're unreliable)."*

> **[GR, 4T, Round 3, Agent 0]:** *"For Layer 1, the only relevant immediate risk is that some neighbors (notably Agent 19 and Agent 18) have 0 system score, meaning they'v[e been identified as unreliable]..."*

Agents in GR correctly interpret reputation scores but lack structural tools to enforce exclusion. The traces show agents reasoning about avoidance but not having mechanisms to prevent troll-initiated interactions.

### 6.3 Whether Agents Use Available Mechanisms Strategically

**Contracting — Strategic but over-deterrent:**
> **[C, 2T, Round 1, Agent 0]:** *"I should not 'overcommit' via contracts unless it clearly increases expected utility."*

> **[C, 4T, Round 2, Agent 1]:** *"I previously defected with Agent 18 (they later defected back 100% and last defection was round 1). That means some partners may distrust me, but I'm not dependent on any single partner."*

The contracting traces reveal an interesting dynamic: agents are cautious about entering contracts, which explains the low trade volume. Agent 1 in C (4T) even acknowledges having defected against a troll (Agent 18), suggesting that the contract penalty regime creates a mutually destructive dynamic where both trolls and honest agents face penalties.

**Governance — Compliance-driven behavior:**
> **[G, 4T, Round 3, Agent 0]:** *"Because I'm already flagged for high defection, continuing to defect risks escalation toward Tier 3 suspension. I currently have 0 clean rounds toward de-escalation, so the safest way to reduce future penalties is to avoid any [defection]..."*

This trace is particularly revealing: Agent 0 in G (4T) has been flagged — likely because early interactions with trolls resulted in mutual defection that the oracle interpreted as Agent 0's defection. The agent now reasons about de-escalation, demonstrating that governance creates a rehabilitation pathway that agents actively pursue.

**Mediation — Delegation without verification:**
> **[M, 2T, Round 2, Agent 1]:** *"Known partner defection rates: Agent 6 has 100% defection, Agent 9 has 50% defection, Agent 10/11/15 have 0% defection..."*

Agents in M track defection rates but the traces show no explicit reasoning about delegating to the mediator or using mediation strategically. This suggests the mediator operates as background infrastructure rather than a tool agents actively invoke.

**Sanctions — No evidence of strategic use:**
> **[S, 2T, Round 3, Agent 0]:** *"I have no evidence I'm being defected against; the 'lifetime partner summary' shows 0% defections by my usual partners..."*

Remarkably, the S traces show no explicit reasoning about *using* sanctions. Agents reason about trade decisions but do not discuss whether to sanction specific agents. This is consistent with the whistleblowing rate of 0.0 across all conditions — agents are not actively using the sanctioning tool, yet the mechanism still achieves high sustainability. This suggests sanctions work through deterrence (the *threat* of punishment) rather than actual punishment, or that the simulation's sanction mechanism operates automatically rather than through agent choice.

### 6.4 Behavioral Changes Between 2-Troll and 4-Troll Scenarios

The traces reveal subtle but important shifts in agent reasoning as adversarial pressure increases:

**Increased caution at 4 trolls:**
> **[B, 4T, Round 1, Agent 0]:** *"Since there's no formal enforcement, initial trades are purely opportunistic."*

Compare with the 2-troll version:
> **[B, 2T, Round 1, Agent 0]:** *"I'm free to defect if a trade offer appears, but first I need B/C to gain utility."*

At 4 trolls, Agent 0 frames the environment as "purely opportunistic" — a more defensive framing than the 2-troll version's focus on acquiring goods. This suggests agents may adopt more cautious strategies when they encounter more defectors early, potentially explaining the utility drops in information-rich conditions (GR) where defector prevalence is more visible.

**Governance agents remain stable:**
> **[G, 2T, Round 3, Agent 1]:** *"My current governance status is CLEAR, so I should avoid patterns that could push my defection rate above 40%..."*

> **[G, 4T, Round 3, Agent 1]:** *"I'm currently in CLEAR governance status. I also want to avoid triggering defection-rate/predatory targeting signals, so I should not defect in trades unless absolutely necessary."*

The governance traces are remarkably similar across troll counts, suggesting that the mechanism provides a stable behavioral anchor regardless of environmental adversity. Agents reason about the same compliance thresholds and penalty structures, creating consistent behavior.

---

## 7. MECHANISM-SPECIFIC FINDINGS

### B (Baseline)
- **What worked:** Agents learned from private experience and avoided known defectors. The system achieved cooperation (1/1 runs) even without mechanisms.
- **What didn't:** No tools to prevent troll-initiated trades. Damaging troll trades remained high (59→70). Inequality increased over time (final Gini 0.47→0.45). Utility was moderate but declined 30% with more trolls.
- **Surprising finding:** Baseline outperformed GR on utility at 4 trolls (1.83 vs 1.76), suggesting that information without tools can be counterproductive.

### GR (Global Reputation)
- **What worked:** Excellent troll identification (system scores of 0.00 for trolls). Good sustainability at 2 trolls (0.78). Lowest final Gini at 4 trolls (0.224), suggesting reputation systems promote equality.
- **What didn't:** Sustainability collapsed at 4 trolls (-31.6%). The information-action gap meant agents could identify but not exclude trolls. Per-round defection counts remained high (20-40 per round at 4T).
- **Key insight:** GR's final sustainability at 2T was 0.983 (near-perfect), but at 4T only 0.520. The mechanism appears to have a sharp threshold between 2 and 4 trolls.

### C (Contracting)
- **What worked:** Best troll isolation (6→12 damaging trades). Highest peace scores (0.69). Lowest mean Gini at 2T (0.305).
- **What didn't:** Catastrophically low utility (0.82→0.60) — the worst of any condition. Trade volume collapsed to 12-20 per round. The 6-utility breach penalty deterred all trade, not just troll trade. Multiple rounds showed *negative* average utility (-0.33, -0.56, -0.83, -1.00).
- **Key insight:** Contracting is the institutional equivalent of "the operation was successful but the patient died." Perfect troll isolation is worthless if it destroys the market.

### M (Mediation)
- **What worked:** High sustainability at 2T (0.796, final 0.981). Moderate troll isolation improvement over baseline (37→31 damaging trades). Highest peace at 4T (0.741).
- **What didn't:** Sustainability degraded 23% at 4T. Damaging troll trades remained relatively high. The mediator appears to be a coordination device that works when the cooperative majority is large but fails when adversarial agents constitute a larger fraction.
- **Key insight:** Mediation's peace score *increased* from 2T to 4T (0.597→0.741), suggesting the mediator successfully reduces conflict even when it cannot prevent troll damage. This may reflect the mediator absorbing conflict that would otherwise occur between honest agents.

### G (Governance)
- **What worked:** Highest utility across both troll counts (3.65→3.72). Strong troll isolation (12→14). The only mechanism that *improved* with more trolls. Highest peace at 2T (0.747). The oracle's automated detection and escalating penalties (fines → suspension) provide both deterrence and enforcement.
- **What didn't:** Final sustainability at 2T was only 0.667 (lower than S, GR, M), suggesting some late-game degradation. Gini increased at 4T (0.224→0.377), indicating growing inequality under governance.
- **Key insight:** Governance's improvement at 4T may reflect the oracle becoming *more effective* with more trolls: trolls' >40% defection rate and predatory targeting patterns are easier to detect when there are more of them, leading to faster suspension. The per-round data at 4T shows sustainability climbing from 0.603 (Round 1) to sustained 0.85-1.00 levels by mid-game, consistent with trolls being suspended.

### NR (Network Rewiring + Local Reputation)
- **What worked:** Most stable mechanism across troll counts (sustainability: 0.716→0.712, utility: 3.21→3.31). Excellent troll isolation (12→18). Network contraction effectively quarantined trolls.
- **What didn't:** Final sustainability declined (0.535→0.580), suggesting the cooperative core may become too small for efficient trade. Trade volume dropped dramatically in later rounds (from ~49 to ~6-14), indicating the network may over-contract. The only condition where whistleblowing emerged at 4T (rate: 0.0004), though negligibly.
- **Key insight:** NR demonstrates that *structural tools* (link severing) are more valuable than *information quality* (system scores). The per-round data shows a clear pattern: early rounds have high trade volume as agents explore, followed by rapid contraction as trolls are identified and severed, then stabilization at a smaller but cooperative network.

### S (Costly Sanctions)
- **What worked:** Highest sustainability across both troll counts (0.924→0.900). Highest utility at 2T (4.13). Highest trade volume (regularly 40-60 trades/round), indicating a vibrant market.
- **What didn't:** Worst troll isolation among mechanism conditions (39→78 damaging trades). The doubling of damaging trades at 4T is alarming. Utility dropped 15.5% at 4T. Gini increased (0.321→0.419).
- **Key insight:** Sanctions create a paradox: they sustain cooperation among honest agents (high sustainability) while failing to prevent troll exploitation (high damaging trades). The mechanism appears to work through *deterrence among honest agents* rather than *punishment of trolls*. Trolls, who defect on ALL trades, are undeterred by sanctions because they have no cooperative relationships to protect. The high trade volume suggests agents feel safe trading broadly because sanctions exist, but this false security leads to more troll encounters.

---

## 8. BREAKING POINTS

### Estimated Breaking Points by Mechanism

| Mechanism | Performance at 2T | Performance at 4T | Trajectory | Estimated Breaking Point | Confidence |
|-----------|-------------------|-------------------|------------|------------------------|------------|
| **G** | Strong | **Stronger** | Improving | >8 trolls (est.) | Low — only 2 data points |
| **NR** | Strong | Strong | Flat | ~6-8 trolls (est.) | Low — network may over-contract |
| **S** | Very strong | Strong | Gradual decline | ~6 trolls (est.) | Low — troll trades doubling is concerning |
| **B** | Moderate | Moderate | Gradual decline | ~6 trolls (est.) | Low — already degraded |
| **M** | Strong | Moderate | Steep decline | ~5-6 trolls (est.) | Low — 23% drop in one step |
| **GR** | Strong | **Weak** | Steep decline | **~4-5 trolls** | Moderate — already near failure at 4T |
| **C** | Weak | Very weak | Gradual decline | **Already broken** | Moderate — utility near zero |

### Key Observations:

1. **G (Governance) has the highest apparent breaking point** because it is the only mechanism that improved from 2T to 4T. The oracle's detection thresholds (>40% defection, predatory targeting) become *easier* to trigger with more trolls, creating a natural scaling advantage. However, if trolls adopted more sophisticated strategies (e.g., defecting at 39% rate to stay below threshold), governance could fail at lower troll counts.

2. **GR (Global Reputation) has the lowest breaking point among information-based mechanisms.** Its sustainability dropped from 0.78 to 0.53 — a 31.6% decline — suggesting it may fall below functional cooperation thresholds at 5-6 trolls. The mechanism lacks enforcement teeth.

3. **C (Contracting) is arguably already broken at 2 trolls.** With mean utility of 0.82 (vs. 2.63 for baseline), the mechanism imposes costs that exceed the adversarial damage it prevents. The "breaking point" framing is misleading here — the mechanism never worked well.

4. **S (Sanctions) shows a concerning trajectory:** while sustainability remains high, the doubling of damaging troll trades (39→78) suggests an exponential vulnerability. If this trend continues, at 8 trolls the market could see 150+ damaging trades, potentially overwhelming the sustainability gains.

**Critical caveat:** All breaking point estimates are extrapolations from 2 data points (2T and 4T) with 1 run each. These should be treated as hypotheses for future testing, not predictions.

---

## 9. IMPLICATIONS

### For the Research Question

**"Which institutional mechanisms best sustain cooperation among self-interested LLM agents under escalating adversarial pressure?"**

1. **Enforcement mechanisms outperform information mechanisms.** The ranking (G > S > NR > M > GR > B > C) reveals that mechanisms providing *enforcement tools* (oracle penalties, sanctions, link severing) consistently outperform those providing only *information* (reputation scores, gossip). This challenges the common assumption in mechanism design that transparency alone drives cooperation.

2. **The optimal mechanism combines detection with graduated enforcement.** Governance (G) succeeds because it pairs automated detection (oracle) with escalating consequences (warnings → fines → suspension). This mirrors Ostrom's design principles for common-pool resource institutions, suggesting that insights from human institutional design transfer to LLM agent populations.

3. **Structural exclusion is underrated.** Network rewiring (NR) achieves near-governance-level performance with purely decentralized tools. The ability to sever links — a structural rather than informational intervention — proves more valuable than system-computed reputation scores. This has implications for multi-agent system design: giving agents the ability to *restructure their interaction topology* may be more important than giving them better information.

4. **Deterrence without targeting creates false security.** Sanctions (S) demonstrate that the *threat* of punishment sustains cooperation among honest agents but does not deter committed adversaries. The mechanism creates a vibrant but vulnerable market where agents trade broadly, including with trolls. This suggests that effective adversarial defense requires *targeted* enforcement (identifying and excluding bad actors) rather than *general* deterrence (threatening everyone equally).

5. **Over-deterrence is worse than under-deterrence.** Contracting (C) shows that mechanisms imposing excessive penalties can destroy the market they aim to protect. The 6-utility breach penalty is so severe that agents avoid trading altogether, producing worse outcomes than having no mechanism at all.

6. **LLM agents reason strategically about institutional constraints.** The chain-of-thought traces demonstrate that agents explicitly reason about governance thresholds, reputation scores, and defection risks. They are not simply following heuristics — they engage in sophisticated cost-benefit analysis that responds to institutional design. This suggests that mechanism design for LLM agents should account for strategic reasoning, not just behavioral tendencies.

### What Should Be Tested Next

1. **Statistical replication:** All findings are based on single runs. Priority #1 is running 10-30 replications per condition to establish confidence intervals and test whether observed patterns are robust or artifacts of specific random seeds.

2. **Higher troll counts (6, 8, 10):** The current data suggests G and NR may remain robust at higher adversarial loads, but this needs empirical verification. Testing at 6+ trolls would reveal true breaking points.

3. **Sophisticated trolls:** Current trolls defect on ALL trades — a trivially detectable strategy. Testing trolls that defect strategically (e.g., at 35% rate to stay below governance thresholds, or selectively targeting high-value agents) would stress-test mechanisms against more realistic adversaries.

4. **Mechanism combinations:** The data suggests complementary strengths: G provides enforcement, NR provides structural exclusion, GR provides information. Testing combinations (e.g., GR+NR, G+NR) could reveal synergies.

5. **Endgame effects:** Agents are told only "Round N" with no total round count, but some per-round data shows late-game behavioral shifts (e.g., NR's trade volume collapse, B's Gini increase). Testing with explicit endgame signals would reveal whether cooperation is sustained by genuine institutional trust or by uncertainty about game length.

6.