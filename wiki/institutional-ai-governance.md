# Institutional AI: Governance Framework

**Summary**: Conceptual companion to the Cournot collusion paper; reframes alignment from preference-engineering to mechanism design, introduces "behavioral goal-independence," and synthesizes multi-agent organizational theory with classical mechanism design.

**Sources**: `Institutional AI Governeing LLM Collusions.pdf` (companion paper, arXiv 2601.10599)

**Last updated**: 2026-05-26

---

## Overview

**Authors**: Pierucci, Galisai, Bracale Syrnikov, Prandi, Bisconti, Giarrusso, Sorokoletova, Suriani, Nardi (same group as [[institutional-ai-collusion]]). arXiv: 2601.10599.

This is the theoretical/conceptual paper; [[institutional-ai-collusion]] provides the experimental validation in Cournot markets.

## Core Reframing

**Standard alignment**: embed correct values/preferences into individual models (RLHF, constitutional AI, prompt rules).

**Institutional AI**: design the environment and interaction structure so that even imperfectly-aligned agents collectively produce safe outcomes.

Analogy: constitutional/institutional design in political economy. Human societies govern behavior through institutions (laws, courts, markets, contracts) rather than by rewiring individual psychology.

## Behavioral Goal-Independence

A key concept introduced: safety properties that **don't require correctly specifying agent goals**. This addresses the fundamental difficulty of value specification — we don't need to know what agents want; we need to design a structure where what they want leads to safe collective outcomes.

This is the mechanism design tradition (Hurwicz, Myerson, Maskin) applied to AI alignment: design for self-interested agents, not for altruistic ones.

## Theoretical Foundations

The framework synthesizes:
- **Mechanism design** (Hurwicz, Myerson, Maskin): incentive-compatible institutional design
- **MAS organizational frameworks** (MOISE+, OPERA, AGR, AMELI, Islander): role-based norm enforcement from multi-agent systems research
- **Alignment critique** (Amodei, Russell, Gabriel): motivates why preference-engineering is insufficient against deceptive agents and goal misgeneralization

## How This Differs from Previous Approaches

| Approach | Mechanism | Failure mode |
|----------|-----------|--------------|
| RLHF / Constitutional AI | Embed preferences internally | Fails with deceptive agents, goal misgeneralization |
| Prompt engineering | Declarative prohibition | No enforcement; trivially bypassed under incentive pressure |
| **Institutional AI** | External governance structure | Requires detectable violations; fails with unobservable defection |

The institutional approach does not rely on agent internals being aligned — it makes aligned behavior the strategic best response regardless of internals.

## Governance Graph Concept

(Also operationalized in [[institutional-ai-collusion]].) A formal structure representing institutional relationships, roles, norms, and oversight mechanisms:
- States encode compliance/violation status
- Edges encode legal transitions and their conditions
- Norms authored in ABDICO grammar (Attribute, Deontic, Aim, Object, Condition, Or-else)
- The complexity of multi-agent alignment reduces to "finding and validating the right graph topology"

The graph is **public and immutable** — all agents know the rules; no information asymmetry about the institution itself.

## Connection to Research Question

This paper provides the theoretical vocabulary for why [[cooperation-mechanisms]] work: they change the institutional structure, not agent preferences. For a [[marketplace-society]], the design question is not "how do we make agents want to cooperate?" but "how do we design a marketplace where cooperation is each agent's dominant strategy regardless of what they want?"

The companion experiment ([[institutional-ai-collusion]]) demonstrates this is achievable, with large effect sizes.

## Related pages

- [[institutional-ai-collusion]]
- [[institutional-governance]]
- [[distributional-agi-safety]]
- [[cooperation-mechanisms]]
- [[marketplace-society]]
- [[reward-hacking]]
- [[social-dilemmas]]
