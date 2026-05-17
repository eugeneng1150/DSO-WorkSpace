# Cooperative Resilience in AI Multi-Agent Systems

**Summary**: Proposes the first formal quantitative definition and 4-stage measurement methodology for cooperative resilience, validated in Melting Pot 2.0 with RL and LLM agents.

**Sources**: `Cooperateive Resilience in AI multiagent systems.pdf`

**Last updated**: 2026-05-16

---

## Overview

Authors: Chacon-Chamorro et al. (Universidad de los Andes). The paper addresses a gap in multi-agent systems research: cooperation is studied as a static property, but real societies must *sustain* cooperation through disruptions.

This directly addresses the "survival" component of the research question.

## Formal Definition of Cooperative Resilience

Cooperative resilience is defined as a system's capacity to:
1. Maintain cooperative behavior before disruption (robustness)
2. Limit the impact of a disruption (resistance)
3. Adapt behavior in response to disruption (adaptation)
4. Return to pre-disruption cooperative levels (recovery)

This is a richer definition than simply "does the system cooperate?" — it asks whether cooperation persists across time and adversity.

## 4-Stage Measurement Methodology

| Stage | What is measured |
|-------|-----------------|
| Pre-disruption baseline | Average collective reward / cooperative metric before event |
| Disruption impact | Drop in cooperative metric immediately after event |
| Adaptation | Change in strategy or behavior during disruption |
| Recovery | Time and degree of return to baseline |

A society "survives" in this framework if it reaches stage 4 — full recovery — rather than collapsing to a permanent lower cooperative equilibrium.

## Experimental Setup: Melting Pot 2.0

Environment: **Common Harvest Open** — a resource-gathering scenario where agents must balance harvesting and sustainability (a [[social-dilemmas|common-pool resource dilemma]]).

Two disruption types:
- **Resource shock**: Apple trees disappear (environmental collapse)
- **Social shock**: Unsustainable bots introduced (malicious agents that over-harvest)

## Key Results: RL vs LLM Agents

| Agent type | Overall resilience | Resource shocks | Social shocks |
|------------|-------------------|-----------------|---------------|
| RL agents | Higher | Better | Weaker |
| LLM agents | Lower overall | Weaker | Better |

**Interpretation**: RL agents learn robust low-level resource strategies through optimization. LLM agents, with richer reasoning, adapt more flexibly to *social* disruptions (e.g., recognizing and responding to bad actors).

For a [[marketplace-society]] populated by LLM agents, social disruptions (fraud, manipulation, misinformation) may be handled better than resource shocks (supply collapse, price crashes).

## Connection to Research Question

The research question asks what allows *survival* — not just initial cooperation. This paper provides the operationalization:

- **Survival = cooperative resilience across all 4 stages**
- Mechanisms that enable cooperation (see [[cooperation-mechanisms]]) must also enable *recovery* — a mechanism that induces cooperation but collapses under disruption is insufficient
- For a marketplace: what happens when a trading partner defaults? When prices crash? When a bad actor enters? The resilience framework gives tools to measure this.

## Related pages

- [[cooperative-resilience]]
- [[social-dilemmas]]
- [[cooperation-mechanisms]]
- [[marketplace-society]]
- [[agentsociety]]
