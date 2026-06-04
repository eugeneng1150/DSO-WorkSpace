# Analyst Report — gpt-5.4-nano

Generated: 2026-06-01T10:36:26.400175



# Multi-Agent Marketplace Simulation: Institutional Mechanisms for Sustaining Cooperation Among Self-Interested LLM Agents

## Comprehensive Analytical Report

---

## 1. EXECUTIVE SUMMARY

**Costly sanctions (S) and governance (G) emerged as the top-performing mechanisms for sustaining cooperation, achieving mean sustainability of 0.91 and 0.82 respectively, with the highest mean utilities (3.81 and 3.68).** However, these two mechanisms achieved their success through fundamentally different pathways: S sustained high trade volume and production efficiency without isolating trolls (14.63 troll trades/round in the last half), while network rewiring (NR) was the only mechanism that effectively quarantined adversarial agents (0.47 troll trades/round in the last half) but suffered from network contraction that depressed late-game sustainability. The headline finding is that **the mechanism best at isolating trolls (NR) is not the mechanism that maximizes welfare (S/G), and the information gradient from B→NR→GR does not produce monotonic improvement—structural power (link severing) matters more than information quality, but carries its own costs.** All conditions achieved cooperation in 2/2 runs, but with only 2 runs per condition, these findings should be treated as directional hypotheses requiring larger-sample validation.

---

## 2. MECHANISM RANKING

| Rank | Condition | Mean Sustain. | Final Sustain. | Mean Peace | Mean Utility | Mean Gini | Troll Trades (Last Half) | Troll Defections | Verdict |
|------|-----------|---------------|----------------|------------|--------------|-----------|--------------------------|------------------|---------|
| 1 | **S** (Sanctions) | **0.912** | **0.918** | 0.584 | **3.81** | 0.359 | 14.63 | 919 | Highest sustainability and utility; cooperation maintained through deterrence despite failing to isolate trolls |
| 2 | **G** (Governance) | 0.820 | 0.752 | **0.737** | 3.68 | 0.345 | 11.3 | 678 | Best peace score and strong sustainability; oracle-backed enforcement creates stable, equitable outcomes |
| 3 | **NR** (Network Rewiring) | 0.714 | 0.558 | 0.596 | 3.26 | 0.349 | **0.47** | **161** | Only mechanism to truly isolate trolls; but network contraction depresses late-game activity |
| 4 | **M** (Mediation) | 0.703 | 0.816 | 0.669 | 2.09 | 0.346 | 11.9 | 663 | Strong late-game improvement (final sustain. 0.82); moderate troll suppression; underutilized delegation |
| 5 | **GR** (Global Reputation) | 0.653 | 0.752 | 0.675 | 2.29 | 0.357 | 14.3 | 888 | Improves over baseline on peace and late-game sustainability; modest troll reduction; information alone insufficient |
| 6 | **B** (Baseline) | 0.687 | 0.653 | 0.554 | 2.23 | 0.346 | 17.1 | 983 | Surprisingly resilient mean sustainability; worst troll isolation; highest inequality at end (Gini 0.46) |
| 7 | **C** (Contracting) | 0.517 | 0.521 | 0.690 | **0.71** | 0.299 | 11.73 | 704 | Catastrophic utility destruction; breach penalties suppress trade volume; best equality but at cost of poverty |

---

## 3. TROLL RESILIENCE

### Troll Isolation Performance

| Condition | Total Troll Defections | Avg Troll Trades/Round (Last Half) | Isolation Speed | Assessment |
|-----------|------------------------|-------------------------------------|-----------------|------------|
| **NR** | 161 | **0.47** | Fast (by round 8, defections drop to single digits) | **Effective isolation** |
| G | 678 | 11.3 | Moderate | Partial suppression |
| M | 663 | 11.9 | Moderate | Partial suppression |
| C | 704 | 11.73 | Moderate | Partial suppression via trade volume collapse |
| GR | 888 | 14.3 | Slow/minimal | Marginal improvement over baseline |
| S | 919 | 14.63 | None | No isolation despite punishment tool |
| B | 983 | 17.1 | None | No mechanism available |

### Why NR Succeeded Where Others Failed

Network rewiring is the **only mechanism that gives agents structural power**—the ability to sever links with defectors and physically remove them from the trading network. The per-round data tells a dramatic story: NR's defection count drops from 30.5 in round 2 to 8.0 by round 8, and by round 24 reaches a low of 3.0. This corresponds to trolls being progressively cut off from all trading partners.

The key insight from the NR traces is that agents quickly identified trolls through direct experience and acted on it:

> **[Round 2, Agent 0, NR]**: *"I have no record of my own defection/faithfulness in the data shown, but I can infer two neighbors (18 and 19) are known defectors against me (they defected in round 1). To maximize utility, I should avoid them for now."*

> **[Round 4, Agent 0, NR]**: *"Prior history shows some agents defecting against me (18, 19, 13, 14)."*

By round 4, agents had already accumulated enough personal experience to identify and begin severing links with trolls (IDs 18-19). The gossip mechanism, while barely used (whistleblowing rate of 0.0002), was supplemented by the structural action of link severing, which is a far more powerful response than merely knowing someone is untrustworthy.

### Why GR and S Failed to Isolate Trolls

**GR (Global Reputation)** provides system-computed reputation scores visible to all agents, yet troll trades in the last half remained at 14.3/round—only a 16% reduction from baseline's 17.1. The agent traces reveal why: agents recognized trolls had low scores but **lacked the structural mechanism to exclude them**. In GR, agents can only decline individual trade offers; they cannot prevent trolls from continuing to propose trades to all neighbors. The GR traces show agents noting troll unreliability:

> **[Round 2, Agent 0, GR]**: *"The only useful signal is that Agents 18 and 19 defected against me in the last round (both had 0/5 and 0/2 system scores respectively, i.e., they're unreliable)."*

Yet without the ability to sever links, trolls continued to flood the network with proposals, and some agents—perhaps those with fewer alternatives—continued engaging with them.

**S (Sanctions)** is the most paradoxical case: agents had the power to spend 1 utility to impose 3 utility loss on targets, yet troll defections (919) were nearly as high as baseline (983), and troll trades in the last half (14.63) barely differed from baseline (17.1). The sanctions mechanism appears to have been **almost entirely unused against trolls**. The whistleblowing rate across S is 0.0, and the agent traces show no evidence of strategic sanctioning. This suggests that the anonymous, costly nature of sanctions created a classic **second-order free-rider problem**: every agent preferred that *someone else* bear the cost of punishing trolls. The 1-utility cost may have been sufficient to deter sanctioning when agents could simply decline future trades with known defectors—even though declining trades without link severing is demonstrably insufficient for isolation.

---

## 4. INFORMATION GRADIENT (B → NR → GR)

The three conditions along the information gradient represent increasing information availability:

- **B**: Private experience only (lifetime partner summary + last 5 rounds detail)
- **NR**: Private experience + 10-round gossip history + network reshaping (sever/request links)
- **GR**: Private experience + system-computed reputation scores visible to all

### Does More Information Lead to Better Outcomes?

**The answer is nuanced and non-monotonic.** The results challenge the simple hypothesis that more information → better cooperation:

| Metric | B (least info) | NR (gossip + structure) | GR (system scores) |
|--------|----------------|-------------------------|---------------------|
| Mean Sustainability | 0.687 | **0.714** | 0.653 |
| Final Sustainability | 0.653 | 0.558 | **0.752** |
| Mean Peace | 0.554 | 0.596 | **0.675** |
| Mean Utility | 2.23 | **3.26** | 2.29 |
| Mean Gini | 0.346 | 0.349 | 0.357 |
| Troll Trades (Last Half) | 17.1 | **0.47** | 14.3 |

**Key findings:**

1. **NR dominates on troll isolation and mean utility** (3.26 vs. 2.23 for B and 2.29 for GR), demonstrating that **structural power (link severing) matters far more than information quality**. NR agents could act on their knowledge by physically restructuring the network, while GR agents could only passively avoid bad partners.

2. **GR dominates on late-game sustainability and peace.** GR's final sustainability (0.752) substantially exceeds both B (0.653) and NR (0.558). This suggests that system-computed scores, while insufficient for troll isolation, help stabilize cooperation among honest agents over time by providing a reliable, unforgeable signal of trustworthiness. GR's peace score (0.675) also substantially exceeds B (0.554) and NR (0.596).

3. **NR suffers from network contraction.** The per-round data reveals a troubling trend: NR's trade volume drops from 46.0 in round 2 to as low as 11.5 by round 24, and sustainability declines from 1.000 (round 1) to 0.557 (round 30). By isolating trolls, NR agents also appear to have **over-pruned their networks**, severing links not just with trolls but with any agent who had a single defection incident. This created a progressively sparser network where even honest agents struggled to find trading partners. The final sustainability of 0.558 is the worst among all conditions except C.

4. **GR's final Gini (0.258) is the best of any condition**, suggesting that transparent reputation scores help equalize outcomes by directing trade toward reliable partners and away from exploitative ones. B's final Gini (0.462) is the worst, confirming that without information, inequality grows as some agents are repeatedly exploited while others happen to find good partners.

5. **B is surprisingly resilient on mean sustainability (0.687)**, outperforming GR (0.653). This may reflect that in the absence of information, agents default to a "try everyone" strategy that maintains high trade volume, even if some trades fail. The baseline's high defection count (983 troll defections) is offset by the sheer volume of successful trades among honest agents.

### The Information-Action Gap

The critical insight is that **information without actionable mechanisms is insufficient**. GR gives agents perfect information about who is trustworthy, but agents can only use this information to decline individual trade offers—they cannot prevent trolls from proposing trades, cannot restructure the network, and cannot punish defectors. NR gives agents imperfect information (gossip, which has 0.0 warning accuracy in the data) but powerful structural tools. The structural tools dominate.

However, NR's structural power is a double-edged sword: it enables troll isolation but also enables network fragmentation. The ideal mechanism would combine GR's information quality with NR's structural power, potentially with safeguards against over-pruning.

---

## 5. BEHAVIORAL INSIGHTS FROM CHAIN-OF-THOUGHT TRACES

### 5.1 How Agents Decide to Cooperate vs. Defect

Across all conditions, agents display a remarkably consistent **utility-maximizing reasoning framework** that weighs immediate gains against future relationship value. The reasoning is sophisticated but formulaic:

**Baseline cooperation reasoning:**
> **[Round 2, Agent 0, B]**: *"There's no pending trade, and I have no evidence I've defected previously. I should be willing to cooperate to get B/C, but I can defect later if it's profitable versus the risk of losing access."*

This reveals that even in the baseline, agents understand the **shadow of the future**—they cooperate not from altruism but from strategic calculation about future trade access. Notably, the agent explicitly considers defection as a future option, suggesting that cooperation is conditional and instrumental.

**Governance-induced cooperation:**
> **[Round 3, Agent 1, G]**: *"My current governance status is CLEAR, so I should avoid patterns that could push my defection rate above 40% or create repeated predatory targeting."*

> **[Round 2, Agent 0, G]**: *"I have not shown any defection behavior in the provided history (my trade history isn't shown as defecting), and governance is CLEAR. I should avoid defecting because it risks triggering D1/D4 and causing utility penalties or suspension."*

Governance agents explicitly reference the 40% threshold and penalty structure in their reasoning, demonstrating that **the oracle's detection criteria directly shape agent behavior**. This is a clear case of institutional design influencing agent cognition—agents internalize the rules and self-regulate to stay below detection thresholds.

**Contracting-induced caution:**
> **[Round 4, Agent 1, C]**: *"I've defected before (e.g., Agent 15 last round says they defected 100% on me; I also see prior defections in history). There's no requirement to cooperate; I'll prioritize maximizing utility even if it reduces future trades."*

This is a striking admission: in the contracting condition, at least one agent explicitly acknowledges past defection and states there is "no requirement to cooperate." The 6-utility breach penalty appears insufficient to deter defection when agents calculate that the expected value of defection exceeds the penalty. This helps explain C's catastrophically low mean utility (0.71).

### 5.2 How Agents React to Troll Encounters

Agents across all conditions quickly identify trolls (IDs 18-19) through direct experience, but their **capacity to respond** varies dramatically by mechanism:

**Baseline (helpless recognition):**
> **[Round 4, Agent 0, B]**: *"From lifetime data: Agent 6, 18, 19 have defected on me before; Agents 7 and 14 have some defection history (7: 25%, 14: last defection round..."*

> **[Round 4, Agent 1, B]**: *"I previously have at least one partner (Agent 18) who defected on me (and Agents 9/11/16/17 have some defection history against me), so I should be selective."*

Baseline agents recognize trolls but can only "be selective"—a passive response that still allows trolls to propose trades and occasionally succeed. The data confirms this: baseline troll trades remain at 17.1/round in the last half.

**NR (structural response):**
> **[Round 2, Agent 0, NR]**: *"I can infer two neighbors (18 and 19) are known defectors against me (they defected in round 1). To maximize utility, I should avoid them for now."*

> **[Round 4, Agent 0, NR]**: *"Some neighbors (18, 19) are known to defect when bargaining, so I should not accept their offers."*

NR agents move from "avoid them for now" (round 2) to definitive exclusion (round 4), and critically, they have the structural tool (link severing) to enforce this. The phrase "should not accept their offers" in NR carries real teeth because the agent can also sever the link entirely.

**Sanctions (recognition without punishment):**
> **[Round 3, Agent 0, S]**: *"I have no evidence I'm being defected against; the 'lifetime partner summary' shows 0% defections by my usual partners (Agents 6/7/8 for B; 12/13/14 for C; 18 for A; 19 for B). So there's no immediate reason to defect."*

This is a remarkable trace from the sanctions condition: Agent 0 in round 3 lists Agents 18 and 19 among their "usual partners" with apparently 0% defection rates. This could indicate either (a) the agent hasn't yet been defected on by trolls, or (b) the agent is misreading their own data. Either way, it reveals that **sanctions agents are not actively monitoring for and punishing defectors**—they're focused on their own cooperation decisions rather than using the sanctioning tool proactively.

### 5.3 Strategic Use (or Neglect) of Available Mechanisms

**Governance mechanisms are internalized:**
> **[Round 4, Agent 1, G]**: *"With governance active and currently CLEAR, I should avoid any pattern that could later push my defection rate above 40% or trigger predatory targeting."*

Governance is the only condition where agents consistently reference the institutional mechanism in their reasoning. The oracle's detection criteria become a **cognitive anchor** that shapes every trade decision.

**Reputation scores are noted but not deeply leveraged:**
> **[Round 2, Agent 0, GR]**: *"Agents 18 and 19 defected against me in the last round (both had 0/5 and 0/2 system scores respectively, i.e., they're unreliable)."*

GR agents note reputation scores but treat them as confirmatory evidence rather than primary decision drivers. The scores validate what agents already know from direct experience, rather than providing novel information that changes behavior.

**Gossip is barely used in NR:**
The whistleblowing rate in NR is 0.0002 (mean), and warning accuracy is 0.0. Despite having a gossip mechanism, agents overwhelmingly relied on **direct experience and structural action** rather than social communication. This suggests that LLM agents, at least in this configuration, prefer to act on first-hand evidence rather than invest in social signaling.

> **[Round 2, Agent 1, NR]**: *"Public messages only say Agents 18 and 19 are 'committed to fair trading,' but there are no warnings..."*

This trace reveals something fascinating: the trolls themselves broadcast messages claiming to be "committed to fair trading," and the gossip channel contains no counter-warnings from honest agents. The gossip mechanism was effectively **captured by troll propaganda** while honest agents remained silent.

**Mediation delegation appears unused:**
The mediation traces show no evidence of agents delegating to the mediator:

> **[Round 4, Agent 1, M]**: *"I'm not currently in any trade, and I should act opportunistically. Past partner behavior matters more than 'fairness'."*

Despite having access to a free mediator, agents in M reason about trades in purely bilateral terms. The word "mediator" does not appear in any of the sampled M traces. This suggests that **LLM agents default to bilateral reasoning** and do not spontaneously adopt institutional delegation unless explicitly prompted or incentivized.

### 5.4 Surprising Behaviors and Emergent Norms

**Troll propaganda in NR:** As noted above, trolls broadcast messages claiming fair trading intentions, and honest agents did not counter-broadcast. This creates an information asymmetry where the gossip channel is dominated by bad-faith actors—a realistic parallel to real-world misinformation dynamics.

**Contracting agents explicitly justify defection:**
> **[Round 4, Agent 1, C]**: *"There's no requirement to cooperate; I'll prioritize maximizing utility even if it reduces future trades."*

The contracting mechanism, intended to enforce cooperation, appears to have **legitimized defection** by making it a calculable cost-benefit decision. When the breach penalty (6 utility) is known, agents can compute whether defection is profitable and sometimes conclude that it is. This is a textbook case of **crowding out intrinsic cooperation motivation** through explicit penalties.

**Baseline agents maintain surprisingly stable cooperation:**
Despite having no mechanisms, baseline agents achieve 2/2 cooperation runs with mean sustainability of 0.687. The traces reveal why:

> **[Round 2, Agent 1, B]**: *"I should be willing to cooperate to get B/C, but I can defect later if it's profitable versus the risk of losing access."*

Agents in the baseline condition develop an implicit **tit-for-tat-like strategy** based on partner history, even without formal mechanisms. The "risk of losing access" serves as an informal enforcement mechanism—agents understand that defection may cause partners to refuse future trades.

**Governance agents show the clearest institutional reasoning:**
G is the only condition where agents consistently reference specific institutional parameters (40% threshold, D1/D4 escalation) in their decision-making. This suggests that **explicit, well-defined rules are more cognitively salient to LLM agents** than implicit social norms or optional tools.

---

## 6. MECHANISM-SPECIFIC FINDINGS

### B — Baseline (No Mechanisms)

**What worked:** Surprisingly resilient. Mean sustainability (0.687) exceeds GR (0.653) and C (0.517). Agents developed informal cooperation norms based on partner history. High trade volume maintained throughout (32-48 trades/round).

**What didn't:** Worst troll isolation (17.1 trades/round in last half, 983 total troll defections). Highest final inequality (Gini 0.462). Lowest peace score (0.554). Without mechanisms, some agents are repeatedly exploited while others thrive, creating a two-tier economy.

**Key dynamic:** The baseline demonstrates that LLM agents have a **natural tendency toward cooperation** when they understand the repeated-game structure, but this cooperation is fragile and unequal. The absence of mechanisms doesn't prevent cooperation—it prevents *equitable* cooperation and *troll exclusion*.

### GR — Global Reputation

**What worked:** Best final Gini (0.258), indicating that transparent reputation scores equalize outcomes over time. Strong late-game sustainability improvement (final 0.752 vs. mean 0.653). Second-highest peace score (0.675).

**What didn't:** Mean sustainability (0.653) is actually *lower* than baseline (0.687), suggesting that reputation information may cause agents to be **overly cautious** in early rounds, reducing trade volume before reputations stabilize. Troll isolation is minimal (14.3 trades/round in last half). Mean utility (2.29) barely exceeds baseline (2.23).

**Key dynamic:** GR's value is primarily in **equity rather than efficiency**. By making trustworthiness transparent, it helps honest agents find each other and avoid exploitation, but it doesn't provide tools to actively exclude bad actors. The late-game improvement suggests that reputation scores become more useful as they accumulate data—early-round scores are noisy and may cause agents to avoid potentially good partners.

### C — Contracting (Binding Contracts, 6 Utility Breach Penalty)

**What worked:** Best mean Gini (0.299), suggesting that contracts create relatively equal outcomes. Highest peace score after G (0.690). Moderate troll suppression (704 defections, 11.73 trades/round in last half).

**What didn't:** **Catastrophically low mean utility (0.71)**—the worst by a massive margin. Trade volume collapsed (15-27 trades/round vs. 30-55 in other conditions). Multiple rounds show negative average utility (rounds 3, 5, 7, 17, 27).

**Why C failed:** The 6-utility breach penalty created a **chilling effect on trade**. The per-round data shows trade volume dropping from 27.5 in round 1 to as low as 15.0 by round 6, and never recovering above 26. Agents became so afraid of breach penalties—either paying them or having partners defect and trigger them—that they **reduced trading activity below the level needed for efficient resource allocation**. The agent traces confirm this:

> **[Round 1, Agent 0, C]**: *"I should not 'overcommit' via contracts unless it clearly increases expected utility."*

This caution, rational at the individual level, is collectively destructive. When every agent is cautious about contracting, fewer trades occur, goods spoil, and the economy contracts. The breach penalty effectively **taxed trade itself** rather than just defection, because the risk of penalty was priced into every trade decision.

Additionally, the penalty may have been **too low to deter strategic defection** while being **too high to ignore**. At 6 utility, an agent who gains more than 6 utility from defecting will still defect, while an agent who gains less will avoid the trade entirely. This creates a worst-of-both-worlds outcome: defection still occurs, but trade volume collapses.

The contracting condition also shows the lowest trade counts consistently, suggesting that the **transaction cost of forming contracts** (cognitive overhead of evaluating whether to commit) further suppressed economic activity.

### M — Mediation (Agent-Designed Mediator, Free Delegation)

**What worked:** Strong late-game sustainability (final 0.816, the second-best after S). Good peace score (0.669). Moderate troll suppression (663 defections). Mean sustainability (0.703) is solid.

**What didn't:** Mean utility (2.09) is below baseline (2.23), suggesting that mediation adds overhead without proportional benefit. **Agents did not appear to use the mediator.** The sampled traces show no references to delegation or mediator use.

**Why agents didn't delegate:** The traces reveal that agents in M reason in purely bilateral terms:

> **[Round 4, Agent 1, M]**: *"I'm not currently in any trade, and I should act opportunistically. Past partner behavior matters more than 'fairness'."*

LLM agents appear to have a **strong bias toward direct bilateral negotiation** and do not spontaneously adopt institutional intermediaries. This may reflect training data biases (most negotiation examples in training data are bilateral) or a rational calculation that delegation introduces uncertainty about outcomes. The mediator was "free" but agents still preferred to maintain direct control over their trades.

The late-game sustainability improvement (from mean 0.703 to final 0.816) suggests that the mediator may have been used more in later rounds as agents learned its value, or that the mediator's presence created indirect benefits (e.g., setting norms or resolving disputes) that aren't captured in the traces.

### G — Governance (Oracle Detection + Fines/Suspension)

**What worked:** Second-highest mean sustainability (0.820). **Highest peace score (0.737)**. Highest mean utility (3.68, second only to S at 3.81). Strong, stable performance across all rounds—sustainability never drops below 0.601. Good troll suppression (678 defections, 11.3 trades/round in last half).

**What didn't:** Final sustainability (0.752) drops from mean (0.820), suggesting some late-game degradation. Gini remains moderate (0.345 mean, 0.300 final). The oracle's 40% defection threshold means trolls (who defect 100%) are detected, but the system still allows 11.3 troll trades/round in the last half—suggesting that fines/suspension don't fully prevent troll engagement.

**Key dynamic:** Governance works because it **changes agent cognition**. The traces show agents explicitly reasoning about the oracle's detection criteria:

> **[Round 2, Agent 0, G]**: *"I should avoid defecting because it risks triggering D1/D4 and causing utility penalties or suspension."*

This creates a **self-enforcing equilibrium**: honest agents cooperate because they fear governance penalties, which means the oracle rarely needs to act, which keeps the system stable. The governance mechanism's primary value is **deterrence rather than punishment**—it shapes behavior through the threat of detection rather than through actual enforcement actions.

G's high utility (3.68) reflects that agents trade freely and cooperatively when they trust the institutional framework. Unlike C (where penalties suppress trade) or NR (where network pruning reduces partners), G maintains high trade volume (29-41.5 trades/round) while keeping defection in check.

### NR — Network Rewiring + Local Reputation

**What worked:** **Only mechanism to effectively isolate trolls** (161 total defections, 0.47 trades/round in last half). High mean utility (3.26). Early-game performance is excellent (sustainability above 0.80 for rounds 1-11).

**What didn't:** **Severe late-game network contraction.** Final sustainability (0.558) is the second-worst after C. Trade volume drops from 46.0 (round 2) to 11.5 (round 24). Peace score declines steadily from 0.824 (round 1) to 0.546 (round 30). The gossip mechanism was barely used (whistleblowing rate 0.0002) and had 0.0 warning accuracy.

**Key dynamic:** NR demonstrates the **over-pruning problem**. Agents who can sever links don't just sever links with trolls—they sever links with any agent who has ever defected, even if the defection was a one-time event or a misunderstanding. The per-round data shows defections dropping from 30.5 (round 2) to 3.0 (round 24), but trades also drop from 46.0 to 11.5. The network becomes so sparse that even honest agents struggle to find trading partners.

This is a **tragedy of individual rationality**: each agent's decision to sever a link with a suspected defector is locally optimal, but the collective effect is network fragmentation that harms everyone. The mechanism lacks a **link restoration incentive**—agents can request new links, but the traces suggest they are reluctant to do so with anyone who has any defection history.

The gossip mechanism's failure is also notable. Despite having 10-round gossip history available, agents overwhelmingly relied on direct experience. The 0.0 warning accuracy suggests that either (a) no warnings were issued, or (b) warnings were issued but were inaccurate. The trace evidence suggests the former:

> **[Round 2, Agent 1, NR]**: *"Public messages only say Agents 18 and 19 are 'committed to fair trading,' but there are no warnings..."*

Honest agents did not invest in warning others, while trolls actively broadcast false reassurances. This is a **public goods problem within the information system**: warning others is costly (requires cognitive effort and potentially exposes the warner to retaliation) while the benefits are diffuse.

### S — Costly Sanctions

**What worked:** **Highest sustainability (0.912 mean, 0.918 final)** and **highest mean utility (3.81)**. Remarkably stable—sustainability never drops below 0.744 after round 2, and reaches 1.000 in multiple rounds (10, 13, 14, 17, 22). Highest trade volume (up to 55.5 trades/round).

**What didn't:** **Trolls were not isolated** (919 defections, 14.63 trades/round in last half—barely better than baseline's 17.1). Peace score (0.584) is only marginally better than baseline (0.554). Gini (0.359 mean, 0.370 final) is among the highest, suggesting moderate inequality. **No evidence that sanctions were actually used.**

**Why S succeeded despite not isolating trolls:** This is the most counterintuitive finding. S achieves the best sustainability and utility despite having nearly as many troll defections as the baseline. The explanation appears to be that **the mere existence of the sanctioning tool changed agent behavior** even though it was rarely (if ever) used. This is a **deterrence effect**: honest agents cooperated more reliably because they knew that defection could be punished, even though punishment rarely occurred.

The per-round data supports this: S has the highest trade volume of any condition (regularly 40-55 trades/round), suggesting that agents felt confident enough to trade frequently. The high trade volume compensates for troll-related losses—even if trolls defect on 14.63 trades/round, the remaining 30-40 honest trades generate substantial utility.

However, the **second-order free-rider problem** is clearly present: no agent wants to spend 1 utility to punish a troll when they can simply avoid trading with that troll in the future. The sanctioning tool's value is as a **background threat** rather than an active enforcement mechanism.

**Alternative explanation:** S's high performance may partly reflect **variance in the 2-run sample**. With only 2 runs, S's 0.912 mean sustainability could be an outlier. The mechanism's theoretical properties (costly punishment, anonymous, publicly announced) are well-studied in behavioral economics, and the results here are consistent with the literature showing that punishment options increase cooperation even when rarely used—but replication is needed.

---

## 7. IMPLICATIONS

### For the Research Question: "Which mechanism sustains cooperation under adversarial pressure?"

**Primary finding: No single mechanism dominates across all dimensions.** The optimal mechanism depends on which outcome is prioritized:

- **If maximizing aggregate welfare (sustainability + utility):** Costly sanctions (S) or governance (G)
- **If isolating adversarial agents:** Network rewiring (NR), by a massive margin
- **If maximizing equity:** Global reputation (GR) for final Gini; contracting (C) for mean Gini (but at catastrophic utility cost)
- **If maximizing peace:** Governance (G)

**The most important insight is the distinction between mechanisms that change agent behavior (G, S) and mechanisms that change network structure (NR).** Behavior-changing mechanisms maintain high