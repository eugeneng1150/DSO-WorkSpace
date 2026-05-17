# Cooperative Resilience

**Summary**: The capacity of a multi-agent system to maintain cooperative behavior through disruptions, not just achieve it in stable conditions.

**Sources**: `Cooperateive Resilience in AI multiagent systems.pdf`

**Last updated**: 2026-05-16

---

## Definition

Cooperative resilience is distinct from cooperative *capacity*. A system may be highly cooperative under normal conditions yet collapse under disruption. Resilience asks: does cooperation *survive* adversity?

Formally defined and measured in [[cooperative-resilience-paper]]. The four-stage framework:

1. **Pre-disruption baseline** — measure cooperative metric (collective reward, social metrics) under stable conditions
2. **Disruption impact** — measure the immediate drop when a disruptive event occurs
3. **Adaptation** — measure changes in agent behavior during the disruption
4. **Recovery** — measure return to baseline level and speed of recovery

A resilient society completes all four stages. A fragile one collapses after stage 2.

## Types of Disruption

From the Melting Pot 2.0 experiments:

**Resource shocks** (e.g., apple disappearance, supply collapse, price crash):
- Test whether agents can maintain cooperation when shared resources become scarce
- RL agents handle these better — they have robust low-level strategies honed through optimization
- LLM agents struggle more — their reasoning-based approach doesn't adapt as quickly to sudden resource unavailability

**Social shocks** (e.g., unsustainable bots, malicious agents, fraud):
- Test whether agents can detect and respond to bad actors in their environment
- LLM agents handle these better — they can reason about behavior, identify anomalies, and adjust social strategies
- RL agents struggle — their policies are not designed to reason about agent intentions

## Implications for Agent Design

For a [[marketplace-society]] with LLM agents:
- The system will be more vulnerable to resource/economic shocks than to social shocks
- Hybrid agent design (LLM reasoning + RL-trained low-level policies) may achieve better across both disruption types
- Resilience should be a *design criterion*, not an emergent hope

## Relationship to Mechanisms

[[cooperation-mechanisms|Cooperation mechanisms]] interact with resilience:
- **Contracting**: resilient to social shocks (contract violations are detectable and sanctionable) but may be brittle under resource shocks if contracts assume resource availability
- **Reputation**: can degrade under disruption if bad actors accumulate enough reputation before being identified
- **Mediation**: mediator becomes a single point of failure — if the mediator fails, cooperation collapses
- **Repetition**: resilient if agents maintain relationships through disruption; fails if disruption forces agent turnover

## Measuring Societal Survival

The combination of [[social-metrics]] and cooperative resilience gives a complete operational definition of "societal survival":

- A society **survives** if, after any plausible disruption, it recovers to baseline levels of Efficiency, Equality, Sustainability, and Peace within a finite time
- A society **fails** if any shock permanently depresses one or more of these metrics

## Related pages

- [[cooperative-resilience-paper]]
- [[social-metrics]]
- [[cooperation-mechanisms]]
- [[social-dilemmas]]
- [[marketplace-society]]
- [[agentsociety]]
