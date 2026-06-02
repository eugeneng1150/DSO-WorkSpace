# Slide Outline — Multi-Agent Marketplace Simulation
# Updated: 2 June 2026

## SETUP (slides 1-9)

# 1: Title
# 2: Research Question
# 3: Literature Context
# 4: The Environment
# 5: The Marketplace (SVG)
# 6: Simulation Architecture (Mermaid)
# 7: The 7 Mechanisms (M flagged as having known bug)
# 8: How We Measure Success — Metrics slide
  - Sustainability = production_t / production_1 — leading indicator of economic health
  - Cooperation Rate = 1 - defections/trades — are trades honored?
  - Mean Utility per Round — the bottom line
  - Gini Coefficient — is utility distributed fairly?
  - All metrics exclude trolls
# 9: Experiment Setup — 3 models, troll counts, 30 rounds

## THE BIG PICTURE — CROSS-MODEL FIRST (slides 10-17)

# 10: Statement — "Mechanism effectiveness is overwhelmingly model-dependent"
  - Lead with the punchline before showing the data

# 11: Nano Utility Trajectories (4 trolls)
  - G (112) > S (105) > NR (99), C near zero

# 12: DeepSeek Utility Trajectories (4 trolls)
  - NR (200) and G (191) lead, B (181) already strong
  - M collapses to -37 (delegation bug)
  - 3x higher utilities than nano

# 13: Mini Utility Trajectories (4 trolls)
  - NR (53) and B (43) lead but far below others
  - G (24) low utility but highest sustainability (0.67)
  - Mini paradox: coop rate 0.78 but sustainability 0.47

# 14: Cross-Model Summary Table
  - model_summary_table.png with all 3 models, gold borders
  - G best for mini and nano; NR best for DeepSeek (ceiling)

# 15: Model > Mechanism — Δ sustainability table
  - G: +0.195 mini, +0.207 nano, 0 deepseek
  - GR/NR/C hurt weak models
  - M excluded (delegation bug)

# 16: G is the Only Consistent Winner
  - Never net-negative across all 3 models
  - Works because oracle doesn't rely on agent reasoning
  - NR/GR capability-gated, S model-split, C consistently harmful

# 17: All Mechanisms Isolate Trolls — That's Not the Hard Part
  - Every mechanism (including baseline) eventually contains trolls
  - The real problem: honest-agent cooperation
  - Cooperation rate is misleading (mini: 0.78 coop but 0.47 sust)
  - Real benchmark: "can honest agents thrive despite trolls?"

## DEEP DIVES — WHY (slides 18-23)

# 18: Why C Consistently Fails (cross-model, not nano-specific)
  - Penalty fear → market freeze across all 3 models
  - CoopEval comparison: their C rewrites payoffs, ours adds punishment
  - Death spiral: penalty fear → avoidance → barter → loss

# 19: M Delegation Bug
  - Zero delegation, all 3 models, 30 rounds
  - Root cause: asymmetric design (only acceptor can delegate)
  - Implementation flaw, not null result. Fix planned.
  - ⚠ All M results unreliable — excluded from rankings

# 20: Information vs Action — GR/NR are Capability-Gated
  - GR: perfect info, no enforcement → fails for weak models
  - NR: worse info but can sever links → outperforms GR
  - Both require agents capable of reasoning about social signals
  - Actionable tools > perfect information

# 21: NR Network Rewiring in Action
  - network_snapshot: trolls isolated, honest agents rebuild denser connections

# 22: Escalation 2T → 4T (Nano only, caveated)
  - G improved (+11.8% sust), NR/S flat, GR collapsed (-31.6%)
  - Caveat: nano only, 1 run per condition

# 23: Evidence — Defection & Trade Volume plots (Nano)
  - G defections decline; C trade volume near zero

## WRAP-UP (slides 24-25)

# 24: Key Takeaways
  - G is the only mechanism never net-negative across all 3 models
  - Model > Mechanism (baseline spread dwarfs mechanism effects)
  - Mechanisms can backfire (C, GR/NR on weak models)
  - Capability-gated: formal enforcement works everywhere, info mechanisms need capable models
  - M unreliable (bug). All conclusions provisional (single-run)

# 25: Next Steps
  - Fix M delegation (bilateral)
  - Fill missing data (mini 0/2T, deepseek 2T)
  - Replication (3 runs per condition)
  - Stress test (6, 8 trolls — find G's breaking point)
