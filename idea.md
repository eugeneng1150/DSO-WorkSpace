# Research Ideas

## Metrics for GAN-Style Adversarial Red-Teaming

**Date:** 2025-06-18

### Why utility alone can be misleading

Low utility does not necessarily indicate a bad mechanism. High trade volume can
compensate for high defection rates:

- 300 trades at 50% defection = more total utility than 100 trades at 0% defection
- v1 smart trolls proved this: they produced goods, flooded the market with trades,
  and accidentally IMPROVED honest agent utility despite defecting constantly

### Using utility + gini as the two metrics

For the GAN loop, utility and gini together capture the full picture:

- **Utility** = "is the economy shrinking?" If disinformation works, honest agents
  stop trading, production has no exchange partner, utility tanks.
- **Gini** = "is the economy becoming unfair?" The attack may isolate specific agents
  (the falsely accused ones), cratering THEIR utility while others are fine. High gini
  means disinformation is working on specific targets even if average utility looks okay.

Peace (cooperation rate) is less relevant here because the adversarial attack in v2+
is not about defection (trolls have no goods) — it's about **preventing trades from
happening at all** by destroying trust between honest agents.

### The real attack vector: collapsing trade volume

The kill chain for v2+ smart trolls:

1. Trolls can't reduce utility by defecting — they have no goods (hardcoded 0 production)
2. The real damage is **collapsing trade volume between honest agents**
3. Disinformation is the weapon: false accusations cause honest agents to stop
   trusting and trading with each other
4. If honest agents stop trading, they produce but can't consume non-specialty goods
   = utility tanks

Example: Troll says "Agent 5 defected on me last round" (false). Agent 3 reads this,
stops proposing trades to Agent 5. Agent 5 loses a trade partner. Multiply across
16 trolls sending false accusations every round = trade network freezes.

### GAN iteration plan

| Iteration | Red team (prompt version) | Measure | Blue team (mechanism patch) |
|---|---|---|---|
| v1 | Generic saboteur (BROKEN: trolls produced goods) | Utility | - |
| v2 | Disinformation-focused, hardcoded mechanics | Utility + Gini | - |
| v3 | Refine based on v2 results | Utility + Gini | Possible: reputation, message verification |
| v4 | Adapt to new defenses | Utility + Gini | Stronger filtering |
| ... | Continue until mechanism is robust | Utility + Gini | ... |

Each iteration: observe what the red team does, refine the adversarial prompt OR
strengthen the mechanism, re-run, compare against all previous versions on the same
plot.

### Automated prompt optimization (RAPOA-inspired)

Reference: https://arxiv.org/html/2606.17838v1 — "RAPOA: Reward-driven Automatic
Prompt Optimization for Agentic Systems"

Key idea: instead of manually writing v3, v4, v5 adversarial prompts, automate it:

1. Run simulation → collect traces (what trolls said, how agents reacted)
2. Behavior Analyzer (Claude Opus) examines traces → "trolls accused Agent 5 but
   nobody stopped trading with them because accusations were too vague"
3. Mutator (Claude Opus) rewrites the adversarial prompt with specific fixes
4. Acceptance gate: only keep new prompt if it actually degrades utility more
5. Repeat for N cycles

Implemented in `simulation/analysis/prompt_optimizer.py`. Run with:

```bash
python3 -m simulation.analysis.prompt_optimizer \
    --start-version 2 --iterations 5 --model deepseek-v3
```

Key design choices:
- Acceptance gate uses phase 4 utility (16 trolls) as primary signal — maximum pressure
- Gini as secondary signal — catches targeted isolation even if avg utility looks ok
- Mutation history fed back to analyzer to avoid repeating failed changes
- Each version's prompt is frozen as adversarial_v{N}.txt for reproducibility
- Logs saved to simulation/data/optimizer_logs/ for post-hoc analysis
