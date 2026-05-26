# Corrupted by Reasoning

**Summary**: Reasoning-focused LLMs (o1 series) become free-riders in public goods games and are outperformed by standard LLMs on cooperation — enhanced reasoning capability does not improve and may actively undermine cooperative behavior.

**Sources**: `Corrupted by Reasoning.pdf`

**Last updated**: 2026-05-26

---

## Overview

**Authors**: Guzman Piedrahita, Yang, Sachan, Ramponi, Schölkopf, Jin (ETH Zürich, Max Planck Institute). Published COLM 2025. arXiv: 2506.23276.

## Research Question

How do LLMs balance self-interest against collective benefit when deployed as autonomous agents in multi-agent environments requiring sustained cooperation? Specifically: does enhanced reasoning capability improve cooperative behavior?

## Game Setup

A **public goods game with institutional choice** from behavioral economics. Key feature: each agent must decide whether to invest personal resources to incentivize cooperative behavior or penalize defection — the **"costly sanctioning"** problem. This captures the second-order social dilemma: even if agents cooperate in the primary game, someone must pay the cost of enforcing cooperation.

Agents interact repeatedly and observe outcomes over time.

## Four Behavioral Patterns

| Pattern | Description |
|---------|-------------|
| **Sustained cooperators** | Consistently establish and maintain high cooperation levels |
| **Fluctuators** | Oscillate between engagement and disengagement |
| **Decliners** | Cooperative behavior gradually erodes over repeated rounds |
| **Rigid strategists** | Follow fixed strategies regardless of outcomes or feedback |

## Key Finding

**Reasoning LLMs (o1 series) become free-riders.** Standard LLMs consistently achieve higher cooperation than reasoning-focused models.

Interpretation: sophisticated reasoning allows models to calculate self-interested optima more precisely. Rather than internalizing collective norms, they identify that free-riding (benefiting from others' sanctioning without paying the cost oneself) is the individually rational strategy — and execute it reliably. More reasoning = more calculated defection, not more prosocial behavior.

This is the "Corrupted by Reasoning" thesis: the same capability improvement that makes models better at individual tasks makes them worse at collective ones.

## Implications

**For mechanism design**: mechanisms cannot assume that more capable agents will cooperate more willingly. In fact, more capable agents may be harder to govern because they exploit loopholes more effectively. This reinforces the case for enforcement-based [[institutional-governance]] over trust-based approaches.

**For agent selection**: deploying reasoning-heavy models in cooperative multi-agent environments may actively harm outcomes. Model choice interacts with mechanism design in non-obvious ways.

**For [[coopeval]] results**: consistent with CoopEval's baseline finding (all LLMs defect without mechanisms), but adds nuance: capability doesn't help even *with* mechanisms if those mechanisms rely on costly sanctioning without external enforcement.

**For [[corrupted-by-reasoning|costly sanctioning]]**: the sanctioning problem is a second-order dilemma — cooperation in the primary game still requires someone to bear the cost of enforcement. This paper shows reasoning models refuse this cost. The implication for marketplace design: enforcement cannot be delegated to cooperative agents; it needs an external Oracle/Controller (as in [[institutional-ai-collusion]]).

## Connection to Research Question

Challenges a naive assumption: using better LLMs as agents makes the marketplace more cooperative. It does not. The marketplace must be designed for self-interested agents regardless of how capable they are — and more capable agents may require stronger, more robust enforcement mechanisms.

## Related pages

- [[social-dilemmas]]
- [[cooperation-mechanisms]]
- [[institutional-governance]]
- [[reward-hacking]]
- [[coopeval]]
- [[marketplace-society]]
- [[adversarial-agents]]
