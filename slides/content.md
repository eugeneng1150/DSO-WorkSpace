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
- M — Mediation (agent-designed mediator, delegation) ⚠ KNOWN BUG — see slide 14
- G — Governance (oracle detection, escalating fines/suspension)
- NR — Network Rewiring + Local Reputation (gossip + link severing)
- S — Sanctioning (collective punishment for defectors)

# Slide 8: Experiment Setup
- Models: gpt-5.4-nano, gpt-5.4-mini, DeepSeek-V3
- Troll counts: 0 (baseline), 2 (10%), 4 (20%) out of 18+troll agents
- 30 rounds per run
- Metrics: total utility, trade volume, defection rate, sustainability

--- RESULTS OVERVIEW ---

# Slide 9: Results — Utility Trajectories (Nano, 4 Trolls)
- [IMAGE: utility_trajectories.png]
- G leads (112 total), S close behind (105), NR solid (99)
- GR ≈ Baseline (53 vs 55) — reputation alone doesn't help
- C is the only condition going negative (16) — worse than no mechanism

# Slide 10: Results — Troll Resilience (Nano, 4 Trolls)
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

# Slide 12: Escalation — 2 Trolls → 4 Trolls (Nano)
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

# Slide 15: ⚠ Why Mediation (M) Fails — Delegation Bug
- Zero delegated trades across all 3 models, all 30 rounds
- Root cause: only the acceptor can delegate — proposer has no delegation option
- Coordination trap: every agent reasons "delegation only helps if counterparty also delegates"
- In CoopEval, both players decide simultaneously (symmetric). Ours is asymmetric — coordination never bootstraps
- M achieves cooperation_rate 0.997 but utility -1.22 — "cooperation theater"
- Implementation flaw, not a null result on mediation. Fix planned for future work.
- ALL M results should be interpreted with this caveat

# Slide 16: Defections & Trade Volume
- [IMAGE: defection_trajectory.png] — G defections decline over time
- [IMAGE: trade_volume.png] — C trade volume near zero (market freeze visualized)

--- NR DEEP DIVE ---

# Slide 17: NR — Cross-Model Behavioral Difference
- Same mechanism (gossip + link severing), very different emergent behavior
- Nano: generic messages ("Open to new trades this round")
- DeepSeek: active warnings, cross-referencing, public apologies
- Mechanism effectiveness is model-dependent

# Slide 18: NR Network Rewiring in Action
- [IMAGE: network_snapshot_NR_run00.png]
- Round 10 → Round 30: trolls isolated, honest agents rebuild denser connections

--- INFORMATION GAP ---

# Slide 19: GR vs NR — Information-Action Gap
- GR: perfect information, no enforcement → GR ≈ Baseline
- NR: worse info but CAN sever links → NR outperforms GR
- Actionable tools > perfect information

--- CROSS-MODEL ---

# Slide 20: Cross-Model Summary Table — All 3 Models
- [IMAGE: model_summary_table.png — all 3 models, gold border = best per model]
- G has gold border for mini and nano. DeepSeek best = NR (ceiling effect)
- M near-zero utility across all models (delegation bug)
- C consistently lowest utility for weaker models

# Slide 21: What Changes Across Models
- G is #1 on all 3 models — only mechanism never net-negative
- DeepSeek baseline stubbornly strong (sust 0.999) — mechanisms barely help
- Mini is most fragile (sust 0.47 at baseline) — only G rescues it
- NR and GR are capability-gated — work for DeepSeek, fail for mini
- S robust for nano (+0.24 sust) but mediocre for mini
- M results unreliable — excluded from ranking (delegation bug)

# Slide 22: DeepSeek Utility Trajectories — 4 Trolls
- [IMAGE: deepseek utility_trajectories.png]
- NR (200) and G (191) lead, both above baseline B (181)
- M collapses to -37 — only condition going deeply negative
- Overall utilities much higher than nano (stronger cooperative prior)

# Slide 23: Mini Utility Trajectories — 4 Trolls
- [IMAGE: mini utility_trajectories.png]
- NR (53) and B (43) lead — but far below nano/DeepSeek
- G (24) suppresses trade volume but achieves highest sustainability (0.67)
- M (-4) and C (11) near-zero — consistent failure across models
- Mini paradox: high cooperation rate (0.78) but lowest sustainability (0.47)

# Slide 24: Model Capability > Mechanism Choice
- Marginal benefit table (Δ sustainability vs own baseline, 4 trolls):
  - G:  DeepSeek +0.000, Mini +0.195, Nano +0.207
  - S:  DeepSeek +0.001, Mini +0.036, Nano +0.241
  - NR: DeepSeek -0.026, Mini -0.051, Nano +0.053
  - GR: DeepSeek -0.020, Mini -0.069, Nano -0.128
  - C:  DeepSeek -0.110, Mini +0.040, Nano -0.247
- M excluded (delegation bug)
- The model is a bigger lever than the mechanism
- Formal enforcement (G) helps weak models; information-based mechanisms hurt them

--- WRAP-UP ---

# Slide 25: Key Takeaways
- G is the only mechanism never net-negative across all 3 models — and the only one that rescues mini
- Model > Mechanism: baseline spread (sust 0.47–0.99) dwarfs mechanism effects
- Mechanisms can backfire: C freezes markets, S drains commons, GR/NR hurt weak models
- Capability-gated: information-rich mechanisms (GR, NR) need capable models; formal enforcement (G) works everywhere
- M results unreliable (delegation bug). All conclusions provisional pending replication

# Slide 26: Next Steps
- Fix M delegation — implement bilateral delegation and re-run
- Fill missing data — mini at 0/2 trolls; DeepSeek at 2 trolls (5 missing conditions)
- Replication — 3 runs per condition for statistical significance
- Stress test — higher troll counts (6, 8) to find G's breaking point
