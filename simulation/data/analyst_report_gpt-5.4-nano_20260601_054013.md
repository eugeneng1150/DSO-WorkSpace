# Analyst Report — gpt-5.4-nano

Generated: 2026-06-01T05:40:13.747685



# Multi-Agent Marketplace Simulation: Institutional Mechanisms for Sustaining Cooperation Among Self-Interested LLM Agents

## Comprehensive Analytical Report

---

## 1. EXECUTIVE SUMMARY

**Costly sanctions (S) and network rewiring with local reputation (NR) emerged as the two most effective but fundamentally different mechanisms for sustaining cooperation under adversarial pressure.** S achieved the highest mean sustainability (0.924), highest mean utility (4.13), and maintained robust trade volume, but completely failed to isolate trolls (14.53 avg troll trades/round in the last half). NR achieved the most decisive troll isolation in the entire experiment (0.53 avg troll trades/round in the last half—a 97% reduction from baseline) but suffered from network contraction that depressed sustainability to 0.535 by round 30. Contracting (C) was the clear failure case, producing the lowest mean utility (0.82) despite achieving the highest peace score (0.691), suggesting that binding contracts with harsh penalties chilled trade volume and created a risk-averse, low-throughput economy. Critically, all seven conditions achieved cooperation in their single run, and no mechanism produced whistleblowing or false accusations (all rates 0.0), indicating that LLM agents in this configuration relied on private experience and structural mechanisms rather than social signaling—a striking null result that demands further investigation.

---

## 2. MECHANISM RANKING

| Rank | Condition | Coop Rate | Mean Utility | Troll Isolation (Avg Troll Trades Last Half) | Mean Sustainability | Mean Peace | Final Gini | One-Line Verdict |
|------|-----------|-----------|-------------|----------------------------------------------|--------------------|-----------|-----------|--------------------|
| 1 | **S** (Costly Sanctions) | 1/1 | **4.13** | Poor (14.53) | **0.924** | 0.582 | 0.321 | Highest utility and sustainability; sanctions deter defection among cooperators but don't structurally exclude trolls. |
| 2 | **G** (Governance/Oracle) | 1/1 | **3.65** | Moderate (12.47) | 0.775 | **0.747** | 0.224 | Best peace score and lowest final Gini; oracle-backed enforcement creates orderly but not maximally productive markets. |
| 3 | **NR** (Network Rewiring) | 1/1 | **3.21** | **Excellent (0.53)** | 0.716 | 0.539 | 0.257 | Decisive troll quarantine but network contraction reduces trade volume and sustainability over time. |
| 4 | **GR** (Global Reputation) | 1/1 | **2.81** | Weak (16.6) | 0.775 | 0.653 | 0.291 | Strong final sustainability (0.983) but surprisingly poor troll isolation despite system-computed scores. |
| 5 | **M** (Mediation) | 1/1 | **2.30** | Moderate (14.07) | 0.796 | 0.597 | 0.326 | High mean sustainability and strong final value (0.981) but mediocre utility suggests delegation wasn't fully leveraged. |
| 6 | **B** (Baseline) | 1/1 | **2.63** | Poor (19.0) | 0.715 | 0.526 | 0.469 | No mechanisms, no troll isolation, highest final inequality; cooperation persists but degrades. |
| 7 | **C** (Contracting) | 1/1 | **0.82** | Moderate (14.2) | 0.541 | 0.691 | 0.220 | Catastrophic utility destruction; 6-utility breach penalties chilled trade volume and created a frozen, low-throughput economy. |

---

## 3. TROLL RESILIENCE

### Troll Isolation Performance (Average Troll Trades/Round, Last 15 Rounds)

| Condition | Troll Defections (Total) | Avg Troll Trades Last Half | Isolation Speed | Assessment |
|-----------|------------------------|--------------------------|-----------------|------------|
| **NR** | 92 | **0.53** | Fast (by ~round 8) | **Decisive structural exclusion** |
| **G** | 378 | 12.47 | Gradual | Moderate suppression via fines/suspension |
| **C** | 424 | 14.2 | Slow | Breach penalties deter but don't exclude |
| **M** | 421 | 14.07 | Slow | Mediator doesn't structurally block trolls |
| **S** | 473 | 14.53 | Minimal | Sanctions punish but don't prevent engagement |
| **GR** | 515 | 16.6 | Minimal | Reputation visible but agents still trade with trolls |
| **B** | 551 | 19.0 | None | No mechanism to isolate |

### Analysis

**NR is the only mechanism that achieved genuine troll quarantine.** The per-round data tells a dramatic story: in rounds 1-7, NR saw 16-33 defections per round (trolls were active), but by round 8, defections dropped to 5, and from round 17 onward, defections averaged only 6.5 per round. The trolls' total of 92 defections across 30 rounds (vs. 551 in baseline) represents an 83% reduction. By the last half, trolls averaged only 0.53 trades per round—they were effectively severed from the network.

The mechanism works because NR gives agents **structural power**: the ability to sever links. Combined with 10-round gossip history, agents could identify defectors and physically disconnect from them. The agent reasoning traces confirm this: Agent 0 in NR Round 2 notes *"two neighbors (18 and 19) are known defectors against me (they defected in round 1). To maximize utility, I should avoid them for now."* By Round 4, the same agent states: *"some neighbors (18, 19) are known to defect when bargaining, so I should not accept their offers."*

**Why did GR fail to isolate trolls despite having system-computed reputation scores?** This is one of the most surprising findings. GR provides the richest information signal—a centralized, objective reputation score visible to all—yet trolls still averaged 16.6 trades/round in the last half (only marginally better than baseline's 19.0). The answer appears to lie in the distinction between **information** and **action capacity**. GR agents could *see* that trolls had low scores, but they lacked the structural mechanism to *exclude* them. In a barter economy where agents need specific goods, an agent who needs Good B may have limited B-producing neighbors, and if a troll is one of them, the agent faces a choice between trading with a known defector or going without. The per-round data shows GR maintaining 26-37 trades/round throughout—trade volume never contracted the way NR's did—suggesting agents continued engaging broadly rather than selectively excluding.

**S (sanctions) also failed to isolate trolls** despite the 3:1 punishment ratio. Trolls are deterministic defectors immune to utility incentives; sanctioning them costs cooperators 1 utility each time while trolls simply absorb the -3 penalty and continue defecting. The sanction mechanism is designed for deterrence of rational agents, not exclusion of irrational ones. Notably, S had the highest trade volume in the experiment (averaging 40+ trades/round in later rounds), suggesting that the threat of sanctions encouraged *more* trading, not less—but this also meant trolls had more opportunities to defect.

---

## 4. INFORMATION GRADIENT (B → NR → GR)

The information gradient hypothesis—that more information leads to better cooperation outcomes—receives **mixed and nuanced support**.

### The Gradient

| Dimension | B (Private Only) | NR (Private + Gossip + Structure) | GR (Private + System Scores) |
|-----------|-----------------|----------------------------------|------------------------------|
| Information richness | Lowest | Medium (local, noisy) | Highest (global, accurate) |
| Action capacity | None | High (sever/request links) | None |
| Mean Utility | 2.63 | 3.21 (+22%) | 2.81 (+7%) |
| Mean Sustainability | 0.715 | 0.716 (+0.1%) | 0.775 (+8.4%) |
| Final Sustainability | 0.603 | 0.535 (-11%) | 0.983 (+63%) |
| Troll Isolation | 19.0 trades/half | 0.53 trades/half | 16.6 trades/half |
| Final Gini | 0.469 | 0.257 | 0.291 |

### Key Finding: Information Without Action Capacity Has Limited Value

**GR provides better information than NR (system-computed vs. gossip-based), but NR produces better troll isolation and higher mean utility.** This strongly suggests that **the ability to act on information (structural power) matters more than the quality of information itself.** NR agents can sever links with defectors, physically restructuring the network; GR agents can only choose not to accept trades, but they cannot prevent trolls from proposing trades or occupying network positions.

However, GR excels on a different dimension: **final sustainability** (0.983 vs. NR's 0.535). This reveals a critical tradeoff. NR's structural power comes at a cost: as agents sever links with defectors (and potentially with each other due to noisy gossip), the network contracts. The per-round data shows NR's trade volume declining from 49 in round 2 to as low as 6 in round 24. By contrast, GR maintains trade volume (26-42 trades/round throughout) because agents can't sever links—they can only modulate trust. The result is that GR sustains a larger, more liquid market even if it can't exclude bad actors.

**B (baseline) performs surprisingly well on mean utility (2.63)**, outperforming both C (0.82) and M (2.30). This suggests that LLM agents have a baseline cooperative tendency that doesn't require institutional support—but this cooperation is fragile (final sustainability 0.603, declining trend) and highly unequal (final Gini 0.469, the worst in the experiment).

### The Information Paradox

More information does not straightforwardly improve outcomes. The gradient shows:
- **B → NR**: Adding gossip + structural power improves utility (+22%) and troll isolation (97% reduction) but *reduces* final sustainability (-11%) due to network contraction.
- **B → GR**: Adding system scores improves sustainability (+63% final) and reduces inequality but barely improves utility (+7%) and fails at troll isolation.
- **NR → GR**: Moving from noisy-but-actionable to accurate-but-passive information *improves* sustainability but *worsens* troll isolation and utility.

The implication is that **information and action capacity are complements, not substitutes**, and the optimal mechanism would combine GR's information quality with NR's structural power.

---

## 5. BEHAVIORAL INSIGHTS FROM CHAIN-OF-THOUGHT TRACES

### 5.1 How Agents Decide to Cooperate vs. Defect

LLM agents consistently demonstrate **strategic reasoning about cooperation as an investment in future trade access**, not as an intrinsic preference. The reasoning is remarkably consistent across conditions:

**Agent 1, B condition, Round 1**: *"Since trades are unenforceable, I can defect on accepted trades to save what I would otherwise give."* — This shows agents explicitly recognizing the defection opportunity, yet...

**Agent 1, B condition, Round 2**: *"I should be willing to cooperate to get B/C, but I can defect later if it's profitable versus the risk of losing access."* — The agent frames cooperation as instrumentally rational, contingent on future trade access.

**Agent 1, C condition, Round 4**: *"I've defected before (e.g., Agent 15 last round says they defected 100% on me; I also see prior defections in history). There's no requirement to cooperate; I'll prioritize maximizing utility even if it reduces future trade access."* — Under contracting, where breach penalties exist, this agent has *already* internalized defection as a viable strategy, suggesting the 6-utility penalty wasn't sufficient to deter.

**Agent 1, G condition, Round 3**: *"My current governance status is CLEAR, so I should avoid patterns that could push my defection rate above 40% or create repeated predatory targeting."* — Under governance, agents explicitly calibrate their defection rate to stay below the detection threshold. This is a sophisticated strategic response: the agent isn't avoiding defection entirely but managing its *rate* to avoid triggering the oracle.

### 5.2 How Agents React to Troll Encounters

Agents across all conditions quickly identify trolls (Agents 18 and 19) as unreliable, but their *response* varies dramatically by mechanism:

**Agent 0, B condition, Round 4**: *"Agent 6, 18, 19 have defected on me before; Agents 7 and 14 have some defection history (7: 25%, 14: last defection round..."* — In baseline, the agent can only note the defection history; there's no mechanism to act on it beyond refusing future trades.

**Agent 0, NR condition, Round 2**: *"two neighbors (18 and 19) are known defectors against me (they defected in round 1). To maximize utility, I should avoid them for now."* — In NR, "avoiding" means severing the link entirely, which is why troll isolation is so effective.

**Agent 0, NR condition, Round 4**: *"some neighbors (18, 19) are known to defect when bargaining, so I should not accept their offers."* — By round 4, the agent has moved from cautious avoidance to categorical rejection.

**Agent 0, GR condition, Round 2**: *"Agents 18 and 19 defected against me in the last round (both had 0/5 and 0/2 system scores respectively, i.e., they're unreliable)."* — In GR, the agent has *quantitative* evidence of troll unreliability via system scores, yet the per-round data shows trolls still averaging 16.6 trades in the last half. This suggests that while Agent 0 avoids trolls, *other agents* may not—perhaps because they need the goods trolls nominally offer, or because the system score alone doesn't trigger categorical exclusion.

### 5.3 Strategic Use (or Non-Use) of Available Mechanisms

**The most striking behavioral finding is the universal zero rate for whistleblowing, false accusations, and warning accuracy across all conditions.** No agent in any condition ever issued a warning about another agent. This is remarkable given that:
- NR explicitly provides gossip channels
- GR provides reputation scores that could be discussed
- S provides anonymous sanctions that could be coordinated

The agent traces reveal why. In NR, Agent 1, Round 2: *"Public messages only say Agents 18 and 19 are 'committed to fair trading,' but there are no warnings about them."* The trolls themselves broadcast false messages (*"committed to fair trading"*), but no cooperating agent counters these claims. In NR Round 3, Agent 1 notes: *"No public broadcasts this round (only generic 'fair...')"* — agents appear to treat the communication channel as noise rather than signal.

This suggests that **LLM agents in this configuration are passive information consumers rather than active information producers.** They read gossip but don't generate it. They observe reputation scores but don't discuss them. They have sanction power but don't coordinate its use. This is a critical design finding: the mechanisms that work (NR's link severing, G's oracle detection) are ones that operate *automatically* or through *individual action*, not through collective communication.

**Agent 1, M condition, Round 4**: *"I'm not currently in any trade, and I should act opportunistically. Past partner behavior matters more than 'fairness'."* — Under mediation, agents explicitly prioritize opportunism over the mediator's intended function. The mediation mechanism appears to have been largely ignored as a coordination device, with agents treating it as background infrastructure rather than actively delegating disputes.

### 5.4 Governance-Specific Strategic Behavior

The governance condition produced the most sophisticated strategic reasoning:

**Agent 1, G condition, Round 2**: *"To avoid governance penalties, I should not become a frequent defector."* — The agent explicitly manages its defection portfolio.

**Agent 0, G condition, Round 2**: *"I have not shown any defection behavior in the provided history (my trade history isn't shown as defecting), and governance is CLEAR. I should avoid defecting because it risks triggering D1/D4 and causing utility penalties or suspension."* — The agent references specific governance detection rules (D1/D4) and calibrates behavior accordingly.

**Agent 1, G condition, Round 4**: *"With governance active and currently CLEAR, I should avoid any pattern that could later push my defection rate above 40% or trigger predatory targeting."* — This is the clearest example of **threshold gaming**: the agent knows the exact detection threshold (40%) and manages its behavior to stay just below it.

### 5.5 Surprising Behaviors and Emergent Norms

**Contracting agents became risk-averse to the point of economic paralysis.** Agent 0, C condition, Round 1: *"I should not 'overcommit' via contracts unless it clearly increases expected utility."* This caution, multiplied across 18 agents, produced a dramatic reduction in trade volume (averaging only 16-27 trades/round vs. 30-50 in other conditions) and the lowest mean utility in the experiment (0.82). The 6-utility breach penalty was so severe relative to the 3-utility consumption gain that agents preferred not to trade rather than risk being defected on under contract.

**Sanctions agents traded more, not less.** S condition averaged 40+ trades/round in later rounds, the highest in the experiment. The availability of punishment appears to have created a sense of security that encouraged more trading—even though trolls continued to defect at high rates. This is consistent with experimental economics findings that punishment institutions increase cooperation among cooperators even when they don't eliminate defectors.

---

## 6. MECHANISM-SPECIFIC FINDINGS

### B — Baseline (No Mechanisms)

**What worked:** LLM agents have a surprisingly robust baseline cooperative tendency. Mean sustainability of 0.715 and mean utility of 2.63 indicate that cooperation emerges even without institutional support. Agents use private experience to identify and partially avoid defectors.

**What didn't:** Cooperation degrades over time (final sustainability 0.603, down from 1.0 in round 1). Inequality increases dramatically (Gini from 0.252 to 0.469). Trolls remain fully integrated (19.0 trades/round in the last half). Without mechanisms, the system trends toward a low-trust, high-inequality equilibrium.

### GR — Global Reputation

**What worked:** Final sustainability is the second-highest in the experiment (0.983), suggesting that reputation information helps agents coordinate on cooperative equilibria over time. Final Gini (0.291) is substantially better than baseline (0.469).

**What didn't:** Troll isolation is surprisingly poor (16.6 trades/round in the last half, only 13% better than baseline). The system-computed scores are accurate but agents lack the structural power to exclude bad actors. Mean utility (2.81) is only 7% above baseline, suggesting that reputation information alone doesn't dramatically improve economic efficiency.

**Key insight:** GR's strength is in *sustaining* cooperation among cooperators (high final sustainability) rather than *excluding* defectors. The reputation scores serve as a coordination device for the cooperative majority rather than an exclusion mechanism for the defecting minority.

### C — Contracting

**What worked:** Highest peace score (0.691) and lowest final Gini (0.220). Contracts create orderly, equitable outcomes for those who do trade.

**What didn't:** **Contracting was catastrophic for economic welfare.** Mean utility of 0.82 is 69% below baseline—agents were *worse off* with contracts than without them. Mean sustainability (0.541) is the lowest in the experiment. Trade volume averaged only ~20 trades/round vs. 35+ in baseline.

**Why:** The 6-utility breach penalty created a **chilling effect**. With consumption gain of only +3 per unit, a single breach penalty wipes out the gains from two successful trades. Agents rationally responded by trading less. Agent 0, C condition, Round 1 explicitly states the concern: *"I should not 'overcommit' via contracts unless it clearly increases expected utility."* The per-round utility data shows multiple rounds with negative average utility (rounds 3, 5, 7, 15, 17, 27), indicating that breach penalties were actively destroying value.

**Design lesson:** Penalty magnitude must be calibrated to the gains from trade. A 6-utility penalty in a system where the maximum per-trade gain is 3 utility creates a 2:1 penalty-to-gain ratio that makes risk-averse agents prefer autarky.

### M — Mediation

**What worked:** High mean sustainability (0.796) and strong final sustainability (0.981). The mediator appears to have provided a coordination benefit even if agents didn't actively delegate.

**What didn't:** Mean utility (2.30) is below baseline (2.63), and peace (0.597) is only marginally above baseline (0.526). The mediation mechanism appears to have been **largely ignored as an active tool**. Agent reasoning traces show no evidence of agents strategically delegating disputes or using the mediator to resolve conflicts.

**Why agents didn't delegate:** The traces suggest agents treated mediation as background infrastructure. Agent 1, M condition, Round 4: *"I'm not currently in any trade, and I should act opportunistically. Past partner behavior matters more than 'fairness'."* The "free delegation" design may have been too passive—agents needed to actively choose to use the mediator, and LLM agents in this configuration defaulted to direct bilateral negotiation.

**Puzzle:** Despite low active use, M achieved the second-highest final sustainability (0.981). This may indicate that the mediator's *existence* (even if rarely invoked) served as a background coordination device, or that the mediator was handling disputes automatically in ways not captured in the sampled traces.

### G — Governance (Oracle Detection)

**What worked:** Best peace score (0.747), second-lowest final Gini (0.224), and highest mean utility after S (3.65). The oracle's detection of defection >40% and predatory targeting created a credible deterrent that agents explicitly referenced in their reasoning. Moderate troll suppression (12.47 trades/round in the last half, 34% below baseline).

**What didn't:** Final sustainability (0.667) is below the mean (0.775), suggesting that governance may have created compliance without genuine cooperation—agents cooperated to avoid penalties rather than because they valued the cooperative equilibrium. The per-round data shows sustainability fluctuating between 0.493 and 1.0 without a clear upward trend.

**Key behavioral finding:** Agents engaged in **threshold gaming**, explicitly managing their defection rates to stay below the 40% detection threshold. Agent 1, G condition, Round 4: *"I should avoid any pattern that could later push my defection rate above 40%."* This means the oracle's 40% threshold effectively *licensed* defection rates up to 39%—a classic problem with bright-line rules.

### NR — Network Rewiring + Local Reputation

**What worked:** **Decisive troll isolation** (0.53 avg troll trades/round in the last half, 97% reduction from baseline). Highest mean utility after S and G (3.21). Good final Gini (0.257). The combination of gossip history and structural power (link severing) created the most effective defense against adversarial agents in the experiment.

**What didn't:** Final sustainability collapsed to 0.535 (worst in the experiment except C). Trade volume declined from 49 in round 2 to as low as 6 in round 24. The network contracted as agents severed links not just with trolls but potentially with each other due to noisy gossip signals or overcautious behavior.

**The NR paradox:** The mechanism that best isolates trolls also most damages the cooperative network. By giving agents the power to sever links, NR creates a tool that is effective against trolls but also fragments the cooperative economy. The per-round data shows a clear inflection around rounds 8-10: troll defections drop sharply, but so does trade volume. By round 24, only 6 trades occurred in the entire round—the network had contracted to a small core of trusted partners.

**Design lesson:** Link severing needs to be paired with link *formation* incentives. NR allows agents to request new links, but the traces suggest agents were more aggressive about severing than requesting. A mechanism that made link formation easier or cheaper might preserve the troll-isolation benefit while preventing network collapse.

### S — Costly Sanctions

**What worked:** **Highest mean utility (4.13), highest mean sustainability (0.924), and remarkably stable sustainability** (final 0.950). S produced the most economically productive cooperative equilibrium in the experiment. Trade volume was the highest across all conditions (averaging 40+ trades/round in later rounds, peaking at 61 in round 18).

**What didn't:** Troll isolation was poor (14.53 trades/round in the last half, only 24% below baseline). The 3:1 punishment ratio (spend 1, target loses 3) is effective against rational agents who can be deterred but useless against deterministic defectors. Peace score (0.582) was mediocre, and Gini (0.321) was mid-range.

**Did agents actually punish?** The traces don't show explicit sanction decisions in the sampled rounds, but the aggregate data tells the story: S had 473 troll defections (vs. 551 in baseline), suggesting trolls were still actively trading. However, the cooperators' mean utility (4.13) was 57% above baseline (2.63), indicating that sanctions created a cooperative surplus among the 18 LLM agents even while trolls continued to operate. The sanctions mechanism appears to have functioned primarily as a **deterrent among cooperators** rather than a punishment tool against trolls.

**The S puzzle:** Why does S produce the highest utility despite poor troll isolation? The answer may be that sanctions create **confidence to trade**. When agents know that defectors can be punished (even if trolls are immune to deterrence), they trade more aggressively. The per-round data shows S averaging 40+ trades/round in the second half—far more than any other condition. More trades mean more opportunities for mutually beneficial exchange, which drives up aggregate utility even if some trades are with trolls.

---

## 7. IMPLICATIONS

### For the Research Question: "Which mechanism sustains cooperation under adversarial pressure?"

**No single mechanism dominates across all dimensions.** The results reveal a fundamental tradeoff space:

1. **Troll exclusion vs. economic productivity**: NR best excludes trolls but contracts the economy. S best sustains productivity but doesn't exclude trolls.
2. **Information vs. action**: GR provides the best information but lacks action capacity. NR provides action capacity with noisy information. The combination would likely outperform either alone.
3. **Deterrence vs. structural exclusion**: G and S deter rational agents from defecting but cannot stop deterministic defectors. NR structurally excludes defectors regardless of their rationality.
4. **Order vs. welfare**: C and G produce the most orderly markets (high peace, low Gini) but at the cost of economic welfare. S produces the highest welfare but with more disorder.

### The Headline Finding

**LLM agents are surprisingly cooperative by default but strategically sophisticated in their use of institutional mechanisms.** They calibrate defection rates to governance thresholds, avoid overcommitting under harsh contract penalties, and aggressively sever links with known defectors when given structural power. However, they are **passive communicators**—they don't generate warnings, coordinate sanctions, or actively use mediation. The mechanisms that work best are those that require **individual action** (severing a link, paying for a sanction) rather than **collective action** (broadcasting warnings, coordinating punishment, delegating to mediators).

### What Should Be Tested Next

1. **Hybrid mechanisms**: Combine NR's structural power with GR's information quality. Allow agents to sever links based on system-computed reputation scores. This should preserve troll isolation while reducing the false-positive link severing that causes network contraction.

2. **Calibrated contracting**: Test C with lower breach penalties (e.g., 2 utility instead of 6) to find the penalty level that deters defection without chilling trade.

3. **Active communication incentives**: The universal zero whistleblowing rate suggests LLM agents need explicit incentives or prompting to use communication channels. Test whether adding a small utility reward for accurate warnings activates the gossip mechanism.

4. **Multiple runs**: **All findings are based on single runs (1/1) per condition.** This is insufficient for statistical claims. The observed differences (e.g., S's 4.13 mean utility vs. C's 0.82) are large enough to likely survive replication, but the more nuanced comparisons (e.g., GR's 2.81 vs. B's 2.63) could easily reverse with different random seeds, troll placement, or agent initialization. A minimum of 10-20 runs per condition is needed for confidence intervals.

5. **Troll sophistication**: The current trolls are deterministic defectors who broadcast lies. Test against more sophisticated adversarial agents (e.g., ones that cooperate early to build reputation, then exploit it—"wolf in sheep's clothing" strategies) to see whether mechanisms that failed against simple trolls (GR, S) might succeed against strategic ones, or vice versa.

6. **Threshold gaming under governance**: The finding that agents explicitly manage defection rates to stay below the 40% oracle threshold suggests testing adaptive thresholds or probabilistic detection to prevent gaming.

7. **Network formation dynamics in NR**: Test whether adding incentives for link formation (e.g., small utility bonus for establishing new trade relationships) can prevent the network contraction that undermined NR's otherwise excellent performance.

---

### Methodological Caveats

- **N=1 per condition**: All rankings and comparisons should be treated as preliminary hypotheses, not established findings.
- **Agent homogeneity**: All 18 cooperating agents use the same model (GPT-5.4-nano). Real multi-agent systems would feature heterogeneous capabilities and strategies.
- **Sampled traces**: The reasoning traces are sampled from early rounds (1-4) and primarily from Agents 0-2 (all A specialists). Behavior of B and C specialists, and behavior in later rounds, may differ substantially.
- **Zero communication rates**: The universal absence of whistleblowing/warnings may reflect a prompt design issue rather than a genuine behavioral finding. If agents weren't explicitly instructed on *how* to issue warnings, the zero rate may reflect confusion rather than strategic choice.
- **Troll design**: Deterministic defectors who propose trades to all neighbors and broadcast lies represent a specific adversarial profile. Results may not generalize to other adversarial strategies.