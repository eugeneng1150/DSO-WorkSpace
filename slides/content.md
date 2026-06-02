# Slide 1: Title
- Multi-Agent Marketplace Simulation: Comparing Institutional Cooperation Mechanisms
- Date: 2 June 2026

# Slide 2: Research Question
- Can institutional mechanisms help Self Interested LLM agents sustain cooperation in adversarial environments?

# Slide 3: Literature Context
- Without mechanisms, all modern LLMs defect in social dilemmas (CoopEval)
- Contracting and Mediation ranked most effective in controlled experiments (CoopEval)
- But: more capable reasoning LLMs become better free-riders, not more cooperative (Corrupted by Reasoning)
- Reputation alone is moderate; becomes powerful when combined with dynamic networks + gossip — 85-98% cooperation (RepuNet)
- Constitutional/prompt-level governance ("be honest") is statistically indistinguishable from no governance (Institutional AI)
- A single defector among cooperators can collapse the system in 1-7 rounds (Subtle Art of Defection)
- Gap: most studies test one mechanism in isolation — we compare 7 head-to-head under adversarial stress

# Slide 4: The Environment
- 18 LLM agents in a marketplace over 30 rounds
- Each round: produce goods, communicate, trade, consume
- Agents need diverse goods to earn utility (incentivizes trade)
- 20% spoilage per round — hoarding is penalized
- Adversarial stress test: inject troll agents (2T and 4T) who always defect

# Slide 5: The Marketplace
- [SVG DIAGRAM: Triangle layout — 3 groups of 6 agents, trading between groups]

# Slide 6: Simulation Architecture
- [MERMAID DIAGRAM: High-level architecture]

# Slide 7: The 7 Mechanisms
- B — Baseline (no mechanism, pure barter)
- GR — Global Reputation (system-computed trust scores visible to all)
- C — Contracting (binding agreements with breach penalties)
- M — Monitoring (public trade audit log)
- G — Governance (community voting on trade rules)
- NR — Network Rewiring + Local Reputation (gossip + link severing)
- S — Sanctioning (collective punishment for defectors)

# Slide 8: Experiment Setup
- Models: gpt-5.4-nano, DeepSeek-V3
- Troll counts: 0 (baseline), 2 (10%), 4 (20%)
- 30 rounds per run
- Metrics: total utility, trade volume, defection rate, production stability

--- RESULTS OVERVIEW ---

# Slide 9: Results — Utility Trajectories (4 Trolls)
- [IMAGE: utility_trajectories.png]
- G leads (112 total), S close behind (105), NR solid (99)
- GR roughly equals Baseline (53 vs 55) — reputation alone doesn't help
- C is the only condition going negative (16) — worse than no mechanism

# Slide 10: Results — Troll Resilience (4 Trolls)
- [IMAGE: troll_resilience_table.png]
- C shows only 9 damaging troll trades vs S's 78
- But C only has 163 total trades vs S's 689
- Low troll damage is a side effect of low trade volume, not active exclusion

--- KEY INSIGHT ---

# Slide 11: Troll Isolation ≠ Cooperation
- All mechanisms eventually reduce damaging troll trades over 30 rounds
- The harder problem is getting self-interested agents to cooperate with each other
- G and S succeed because they both isolate trolls AND create incentives for honest agents to keep trading
- The real benchmark: "can honest agents still thrive despite trolls?"

--- ESCALATION & FAILURE MODES ---

# Slide 12: Escalation — 2 Trolls → 4 Trolls
- G is the ONLY mechanism that improved — sustainability +11.8%, utility +1.9%
- NR nearly flat — sustainability -0.6%, utility +3.1%
- GR collapsed — sustainability -31.6%, utility -37.4%. Worse than Baseline at 4T
- S resilient on sustainability (-2.6%) but damaging troll trades doubled (39→78)
- CAVEAT: Based on 1 run per condition — needs statistical replication

# Slide 13: Two Opposite Failure Modes (C vs S)
- C — Over-Deterrence: best troll isolation but market freeze. Utility: 0.55
- S — Under-Deterrence: worst troll isolation but vibrant market. Utility: 3.49
- Neither achieves targeted exclusion

# Slide 14: Why Contracting (C) Fails
- Agents fear they cannot fulfill contracts — inherently risk averse
- Agents reason incorrectly: "a contract could backfire if the counterparty rejects" — rejection costs nothing
- Death spiral: penalty fear → mechanism avoidance → unprotected barter → utility loss → market freeze

# Slide 15: Defections & Trade Volume
- [IMAGE: defection_trajectory.png] — G defections decline over time
- [IMAGE: trade_volume.png] — C trade volume near zero (market freeze visualized)

--- NR DEEP DIVE ---

# Slide 16: NR — Cross-Model Behavioral Difference
- Same mechanism (gossip + link severing), very different emergent behavior
- Nano: generic messages ("Open to new trades this round")
- DeepSeek: active warnings, cross-referencing, public apologies
- Mechanism effectiveness is model-dependent

# Slide 17: NR Network Rewiring in Action
- [IMAGE: network_snapshot_NR_run00.png]
- Round 10 → Round 30: trolls isolated, honest agents rebuild denser connections

--- INFORMATION GAP ---

# Slide 18: GR vs NR — Information-Action Gap
- GR: perfect information, no enforcement → GR ≈ Baseline
- NR: worse info but CAN sever links → NR outperforms GR
- Actionable tools > perfect information

--- WRAP-UP ---

# Slide 19: Key Takeaways
- Governance (G) and Sanctioning (S) are most troll-resilient
- NR is effective but model-dependent
- Contracting backfires — penalty fear causes market freeze
- GR ~ Baseline — information without enforcement is insufficient
- Mechanism design matters more than information quality

# Slide 20: Next Steps
- Cross-model comparison (DeepSeek across all conditions)
- Test C_low variant (lower penalty)
- Higher troll counts (6, 8) to find breaking points
- 3 runs per condition for statistical significance
